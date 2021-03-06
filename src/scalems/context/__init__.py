"""Workflow scope and execution environment context management.

SCALE-MS optimizes data flow and data locality in part by attributing all
workflow references to well-defined scopes. Stateful API facilities, workflow
state, and scoped references are managed as WorkflowContext instances.

"Workflow context" is an important parameter in several cases.
Execution management tools like scalems.run(), scalems.wait(), and scalems.dispatch()
update the workflow managed in a particular scope, possibly by interacting with
other scopes. Commands for declaring work or data add items to specific instances
of workflow managers. Internally, SCALEMS explicitly refers to theses scopes as
*context*, but *context* is often an optional parameter for user-facing functions.

This module supports scoped_context() and get_context() with internal module state.
These tools interact with the context management of the asynchronous dispatching,
but note that they are not thread-safe. scoped_context() should not be used in
a coroutine except in the root coroutine of a Task or otherwise within the scope
of a contextvars.copy_context().run(). scalems will try to flag misuse by raising
a ProtocolError, but please be sensible.
"""

import abc
import asyncio
import collections
import contextlib
import contextvars
import functools
import json
import logging
import warnings
import weakref

from scalems.exceptions import InternalError, MissingImplementationError, ProtocolError, ScaleMSException, ScopeError

logger = logging.getLogger(__name__)
logger.debug('Importing {}'.format(__name__))


# Identify an asynchronous Context. Non-asyncio-aware functions may need to behave
# differently when we know that asynchronous context switching could happen.
# We allow multiple dispatchers to be active, but each dispatcher must
# 1. contextvars.copy_context()
# 2. set itself as the dispatcher in the new Context.
# 3. run within the new Context.
# 4. ensure the Context is destroyed (remove circular references)
_dispatcher = contextvars.ContextVar('dispatcher', default=None)


class ResourceType:
    def identifier(self) -> str:
        """Resource type identifier"""
        return '.'.join(self._identifier)

    def as_strings(self) -> tuple:
        return self._identifier

    def __init__(self, type_identifier: tuple):
        if not isinstance(type_identifier, tuple):
            raise TypeError('Expected a tuple of identifier strings.')
        # TODO: format checking.
        self._identifier = tuple([element for element in type_identifier])


class Description:
    def shape(self) -> tuple:
        return self._shape

    def type(self) -> ResourceType:
        return self._type

    def __init__(self, resource_type: ResourceType, *, shape: tuple = (1,)):
        # TODO: input validation
        self._shape = shape
        self._type = resource_type


class CommandResourceType(ResourceType):
    def input_description(self) -> Description:
        return Description(self._input_description.type(), shape=self._result_description.shape())

    def result_description(self) -> Description:
        return Description(self._result_description.type(), shape=self._result_description.shape())

    def __init__(self, *args, inputs: Description, results: Description, **kwargs):
        super().__init__(*args, **kwargs)
        self._input_description = Description(inputs.type(), shape=inputs.shape())
        self._result_description = Description(results.type(), shape=results.shape())


# TODO: class AbstractWorkflowItemView(abc.ABC):


class ItemView:
    """Standard object returned by a WorkflowContext when adding details to the workflow.

    Provides the normative interface for workflow items as a user-space object
    that proxies access through a workflow manager.

    Provides a Future like interface.

    At least in the initial implementation, a ItemView does not extend the lifetime
    of the Context to which it refers. If the Context from which the ItemView was
    obtained goes out of scope or otherwise becomes invalid, some ItemView interfaces
    can raise exceptions.

    .. todo:: Allows proxied access to future results through attribute access.

    """
    def uid(self) -> bytes:
        """Get the canonical unique identifier for this task.

        The identifier is universally unique and can be used to query any
        workflow manager for awareness of the task and (if the context is aware
        of the task) to get a view of the task.

        Returns:
            256-bit binary digest as a 32 element byte sequence.
        """
        return bytes(self._uid)

    def done(self) -> bool:
        """Check the status of the task.

        Returns:
            true if the task has finished.

        """
        context = self._context()
        if context is None:
            raise ScopeError('Out of scope. Managing context no longer exists!')
        return context.item(self.uid()).done()

    def result(self):
        """Get a local object of the tasks's result type.

        .. todo:: Forces dependency resolution.

        """
        context = self._context()
        if context is None:
            raise ScopeError('Out of scope. Managing context no longer exists!')
        return context.item(self.uid()).result()

    def description(self) -> Description:
        """Get a description of the resource type."""
        context = self._context()
        if context is None:
            raise ScopeError('Out of scope. Managing context no longer exists!')
        return context.item(self.uid()).description()

    def __getattr__(self, item):
        """Proxy attribute accessor for special task members.

        If the workflow element provides the requested interface, the managing
        Context will provide appropriate access. For "result" attributes, the
        returned reference supports the Future interface.
        """
        # We don't actually want to do this check here, but this is essentially what
        # needs to happen:
        #     assert hasattr(self.description().type().result_description().type(), item)
        context = self._context()
        if context is None:
            raise ScopeError('Out of scope. Managing context no longer available!')
        task = context.item(self.uid())  # type: Task
        try:
            return getattr(task, item)
        except KeyError as e:
            raise


    def __init__(self, context, uid: bytes):
        self._context = weakref.ref(context)
        if isinstance(uid, bytes) and len(uid) == 32:
            self._uid = uid
        else:
            raise ProtocolError('uid should be a 32-byte binary digest (bytes).')


class WorkflowView:
    """Middleware interface for interacting with managed workflow items.

    This interface exists to compartmentalize access methods to the managed workflow,
    keeping the public WorkflowContext interface as simple as possible. The interfaces
    may be combined in the future.
    """


class WorkflowItemRecord:
    """Encapsulate the management of an item record in a BasicWorkflowManager."""



class BasicWorkflowManager:
    """Reference implementation for a workflow manager.

    Support addition and querying of items.
    """
    def __init__(self):
        self._items = dict()


class InvalidStateError(ScaleMSException):
    """Object state is not compatible with attempted access.

    May result from a temporarily unserviceable request or an inappropriate
    usage. Emitter should provide a specific message.

    This exception serves a similar function to asyncio.InvalidStateError.
    """


class Task:
    """Encapsulate the implementation details of a managed Task workflow item.

    * Provide the interface required to support ItemView.
    * Wrap the task execution handling details.

    Note: We need an interface to describe the return value of manager.item().
    We currently manage tasks internally via Task instances, but that is a detail
    that is subject to change without warning.

    Warning:
        Not thread-safe. Access should be mediated by WorkflowManager protocols
        within the asyncio event loop.

    Once Task objects are created, they may not be updated directly by the client.

    TODO:
        Really, this can and should be implemented in terms of asyncio.Task with
        some additional SCALEMS overlay.

    State machine:
        Initial (no coroutine) -> Dispatched (coroutine) -> Executing (Task or Future) -> Final (awaited)

    TODO:
        Allow composable details. A WorkflowManager can provide its own task factory,
        but it is convenient to provide a complete base implementation, and extension
        is likely limited to how the task is dispatched and how the Futures are
        fulfilled, which seem very pluggable.
    """
    def result(self):
        if not self.done():
            raise InvalidStateError('Called result() on a Task that is not done.')
        return self._result

    def description(self) -> Description:
        decoded_record = json.loads(self._encoded)
        resource_type = ResourceType(tuple(decoded_record['type']))
        # TODO: Handle multidimensional references.
        shape = (1,)
        value = Description(resource_type=resource_type, shape=shape)
        return value

    def uid(self) -> bytes:
        if not isinstance(self._uid, bytes):
            raise InternalError('Task._uid was stored as bytes. Implementation changed?')
        return bytes(self._uid)

    def done(self) -> bool:
        return self._done.is_set()

    def __getattr__(self, item):
        # TODO: Manage internal state updates.
        # TODO: Respect different attribute type semantics.
        try:
            decoded_record = json.loads(self._encoded)
            logger.debug('Decoded {}: {}'.format(type(decoded_record).__name__, str(decoded_record)))
            value = decoded_record[item]
        except json.JSONDecodeError as e:
            raise AttributeError('Problem retrieving "{}"'.format(item)) from e
        except KeyError as e:
            logger.debug('Did not find "{}" in {}'.format(item, self._encoded))
            raise AttributeError('Problem retrieving "{}"'.format(item)) from e
        return value

    def __init__(self, context, record):
        self._encoded = str(record)
        decoded_record = json.loads(self._encoded)

        self._uid = bytes.fromhex(decoded_record['uid'])
        if not len(self._uid) == 256//8:
            raise ProtocolError('UID is supposed to be a 256-bit hash digest. Got {}'.format(repr(self._uid)))
        self._done = asyncio.Event()
        self._result = None

        # As long as we are storing Tasks in the context, we cannot store contexts in Tasks.
        self._context = weakref.ref(context)

    def set_result(self, result):
        # Not thread-safe.
        if self._done.is_set():
            raise ProtocolError('Result is already set for {}.'.format(repr(self)))
        self._result = result
        self._done.set()
        logger.debug('Result set for {} in {}'.format(self.uid().hex(), str(self._context())))

    # @classmethod
    # def deserialize(cls, context, record: str):
    #     item_view = context.add_item(record)
    #     return item_view
    # def serialize(self):
    #     ...


# TODO: Incorporate into WorkflowContext interface.
# Design note: WorkflowContext classes could cache implementation details for item types,
# but (since we acknowledge that work may be defined before instantiating the context to
# which it will be dispatched), we need to allow the WorkflowContext implementation to
# negotiate/fetch the implementation details at any time. In general, relationships between specific
# workflow item types and context types should be resolved in terms of context traits,
# not specific class definitions. In practice, we have some more tightly-coupled relationships,
# at least in early versions, as we handle (a) subprocess-type items, (b) function-based items,
# and (c) data staging details for (1) local execution and (2) remote (RADICAL Pilot) execution.
@functools.singledispatch
def workflow_item_director_factory(item, *, context, label: str = None):
    """

    Get a workflow item director for a context and input type.

    When called, the director finalizes the new item and returns a view.
    """
    raise MissingImplementationError('No registered implementation for {} in {}'.format(repr(item), repr(context)))


@workflow_item_director_factory.register
def _(item_type: type, *, context, label: str = None):
    # When dispatching on a class instead of an instance, just construct an
    # object of the indicated type and re-dispatch. Note that implementers of
    # item types must register an overload with this singledispatch function.
    # TODO: Consider how best to register operations and manage their state.
    def constructor_proxy_director(*args, **kwargs):
        if not isinstance(item_type, type):
            raise ProtocolError('This function is intended for a dispatching path on which *item_type* is a `type` object.')
        item = item_type(*args, **kwargs)
        director = workflow_item_director_factory(item, context=context, label=label)
        return director()
    return constructor_proxy_director


class WorkflowEditor(abc.ABC):
    @abc.abstractmethod
    def add_item(self, item) -> ItemView:
        ...


class WorkflowManager(abc.ABC):
    """Abstract base class for SCALE-MS workflow Contexts.

    A workflow context includes a strategy for dispatching a workflow
    for execution. Instances provide the concurrent.futures.Executor
    interface with support and semantics that depend on the Executor
    implementation and execution environment.

    Notably, we rely on the Python contextmanager protocol to regulate
    the acquisition and release of resources, so SCALE-MS workflow
    contexts do not initialize Executors at creation. Instead,
    client code should use `with` blocks for scoped initialization and
    *shutdown* of Executor roles.

    TODO: Enforce centralization of Context instantiation for the interpreter process.
    For instance:
    * Implement a root context singleton and require acquisition of new Context
      handles through methods in this module.
    * Use abstract base class machinery to register Context implementations.
    * Require Context instances to track their parent Context, or otherwise
      participate in a single tree structure.
    * Prevent instantiation of Command references without a reference to a Context instance.

    TODO:
        Check that I'm actually toggling something for the context instance to avoid recursive dispatch loops rather than
        just multiple recursion of self. Maybe keep a reference to the context hierarchy node to use when entering,
        and let implementations decide whether to allow multiple entrance, provided there is a reasonable way to clean up
        the correct number of times.

    TODO:
        In addition to adding callbacks to futures, allow subscriptions to workflow updates.
        This allows intermediate updates to be propagated and could be a superset of the additem hook.

    """

    # TODO: Consider a threading.Lock for editing permissions.
    # TODO: Consider asyncio.Lock instances for non-thread-safe state updates during execution and dispatching.

    # TODO: Reference a generic interface for return type.
    @abc.abstractmethod
    def item(self, identifier) -> ItemView:
        """Access an item in the managed workflow."""


    # TODO: Consider helper functionality and `label` support.
    # def find(self, label: str = None):
    #     """Try to locate a workflow object.
    #
    #     Find reference by label. Find owner of non-local resource, if known.
    #     """


    def default_dispatcher(self):
        """Get a default dispatcher instance, if available.

        Provide a hint to scalems.run() on how to execute work in this scope.

        WorkflowManager implementations define their own semantics. If implemented,
        the returned object should be an AsyncContextManager. If the dispatching
        facility is not reentrant, the WorkflowManager may raise ProtocolError.

        WorkflowManagers are not required to provide a default dispatcher.
        """
        return None

    @contextlib.asynccontextmanager
    async def dispatch(self, dispatcher):
        """Implement the middleware dispatching protocol (TBD).

        The workflow manager attaches the dispatcher to a queue manager, through
        which the dispatcher receives current and future work (until a Stop message
        is issued, when leaving the context for "active" dispatching.
        """
        dispatcher_task = asyncio.create_task(dispatcher)  # type: asyncio.Task
        try:
            yield  # What do we want here? Probably the interface for the queue manager to use.
        finally:
            # send stop message, then
            await dispatcher_task
            dispatcher_exception = dispatcher_task.exception()
            if dispatcher_exception is not None:
                logger.exception('Dispatcher encountered exception '.format(repr(dispatcher_exception)))
                raise dispatcher_exception

    # @abc.abstractmethod
    # def add_task(self, operation: str, bound_input):
    #     """Add a task to the workflow.
    #
    #     Arguments:
    #         operation: named operation to perform
    #         bound_input: reference to a workflow object compatible with operation input.
    #
    #     Returns:
    #         Reference to the new task.
    #
    #     TODO: Resolve operation implementation to dispatch task configuration.
    #     """
    #     ...

    @abc.abstractmethod
    def add_item(self, task_description):
        """Add a task to the workflow.

        Returns:
            Reference to the new task.

        TODO: Resolve operation implementation to dispatch task configuration.
        """
        ...


class DefaultContext(WorkflowManager):
    """Manage workflow data and metadata, but defer execution to sub-contexts.

    Not yet implemented or used.
    """

    def add_item(self, task_description):
        raise MissingImplementationError('Trivial work graph holder not yet implemented.')

    def item(self, identifier) -> ItemView:
        raise MissingImplementationError('Trivial work graph holder not yet implemented.')


class Scope(collections.namedtuple('Scope', ('parent', 'current'))):
    """Backward-linked list (potentially branching) to track nested context.

    There is not much utility to tracking the parent except for introspection
    during debugging. The previous state is more appropriately held within the
    closure of the context manager. This structure may be simplified without warning.
    """


# Root workflow context for the interpreter process.
_interpreter_context = DefaultContext()

# Note: Scope indicates the hierarchy of "active" WorkflowManager instances (related by dispatching).
# This is separate from WorkflowManager lifetime and ownership. WorkflowManagers should track their
# own activation status and provide logic for whether to allow reentrant dispatching.
# TODO: Shouldn't the previous "current" be notified or negotiated with? Should we be locking something?
# Note that it makes no sense to start a dispatching session without concurrency, so we can think
# in terms of a parent context doing contextvars.copy_context().run(...)
# I think we have to make sure not to nest scopes without a combination of copy_context and context managers,
# so we don't need to track the parent scope. We should also be able to use weakrefs.
current_scope = contextvars.ContextVar('current_context', default=Scope(None, None))
current_scope.set(Scope(parent=None, current=_interpreter_context))


def get_context():
    """Get a reference to the manager of the current workflow scope."""
    # TODO: Redocument and adjust semantics.
    # The contextvars and get_context should only be used in conjunction with
    # a workflow_scope() context manager that is explicitly not thread-safe, but
    # which can employ some checks for non-multi-threading access assumptions.
    # get_context() is used to determine the default workflow manager when *context*
    # is not provided to scalems object factories, scalems.run(), scalems.wait() and
    # (non-async) `result()` methods. Default *context* values are a user convenience
    # and so should only occur in the root thread for the UI / high-level scripting interface.
    # Async coroutines can safely use get_context(), but should not use the
    # non-async workflow_scope() context manager for nested scopes without wrapping
    # in a contextvars.run().
    scope = current_scope.get().current
    # This check is in case we use weakref.ref:
    if scope is None:
        raise ProtocolError('Context for current scope seems to have disappeared.')
    return scope


@contextlib.contextmanager
def scope(context):
    """Set the current workflow management within a clear scope.

    Restore the previous workflow management scope on exiting the context manager.

    Within the context managed by *scope*, get_context() will return *context*.

    Not thread-safe. In general, this context manage should only be used in the
    root thread.
    """
    parent = get_context()
    dispatcher = _dispatcher.get()
    if dispatcher is not None and parent is not dispatcher:
        raise ProtocolError('It is unsafe to use concurrent scope() context managers in an asynchronous context.')
    logger.debug('Entering scope of {}'.format(str(context)))
    current = context
    token = current_scope.set(
        Scope(
            parent=parent,
            current=current)
    )
    if token.var.get().parent is current:
        logger.warning('Unexpected re-entrance. Workflow is already managed by {}.'.format(repr(current)))
    if token.old_value.current != token.var.get().parent:
        raise ProtocolError('Unrecoverable race condition: multiple threads are updating global context unsafely.')
    # Try to confirm that current_scope is not already subject to modification by another
    #  context manager in a shared asynchronous context.
    # This nesting has to have LIFO semantics both in and out of coroutines, and cannot block.
    # One option would be to refuse to nest if the current scope is not the root scope and
    # the root scope has an active dispatcher. Note that a dispatcher should use
    # contextvars.copy_context().run() and set a new root context.
    # Alternatively, we could try to make sure that no asynchronous yields are allowed
    # when the current context is a nested scope within a dispatcher context, but technically
    # this is okay as long as a second scope is not nested within the first from within
    # a coroutine that might not finish until after the first scope finishes.
    try:
        yield current
    finally:
        """Exit context manager without processing exceptions."""
        logger.debug('Leaving scope of {}'.format(str(context)))
        # Restore context module state since we are not using contextvars.Context.run() or equivalent.
        if token.var.get().parent is not parent or token.var.get().current is not current:
            raise ProtocolError(
                'Unexpected re-entrance. Workflow scope changed while in context manager.'.format(repr(current)))
        else:
            token.var.reset(token)
        # TODO: Consider if/how we should process un-awaited tasks.


def _run(*, work, context, **kwargs):
    """Run in current scope."""
    import asyncio
    from asyncio.coroutines import iscoroutine, iscoroutinefunction

    # TODO: Allow custom dispatcher hook.
    if iscoroutinefunction(context.run):

        logger.debug('Creating coroutine object for workflow dispatcher.')
        # TODO: Handle in context.run() via full dispatcher implementation.
        try:
            if callable(work):
                handle = work(**kwargs)
        except Exception as e:
            logger.exception('Uncaught exception in scalems.run() processing work: ' + str(e))
            raise e
        # TODO:
        # coro = context.run(work, **kwargs)
        try:
            coro = context.run()
        except Exception as e:
            logger.exception('Uncaught exception in scalems.run() calling context.run(): ' + str(e))
            raise e

        logger.debug('Starting asyncio.run()')
        # Manage event loop directly, since asyncio.run() doesn't seem to always clean it up right.
        # TODO: Check for existing event loop.
        loop = asyncio.get_event_loop()
        try:
            task = loop.create_task(coro)
            result = loop.run_until_complete(task)
        finally:
            loop.close()
        assert loop.is_closed()

        logger.debug('Finished asyncio.run()')
    else:
        logger.debug('Starting context.run() without asyncio wrapper')
        result = context.run(work, **kwargs)
        logger.debug('Finished context.run()')
    return result


def run(work, context=None, **kwargs):
    """Execute the provided coroutine object.

    Abstraction for :py:func:`asyncio.run()`

    Note: If we want to go this route, we should integrate with the
    asyncio event loop policy, or obtain an event loop instance and
    use it w.r.t. run_in_executor and set_task_factory.

    .. todo:: Coordinate with RP plans for event loop contexts and concurrency module executors.

    See also https://docs.python.org/3/library/asyncio-dev.html#debug-mode
    """
    # Cases, likely in appropriate order of resolution:
    # * work is a SCALEMS ItemView or Future
    # * work is a asyncio.coroutine
    # * work is a asyncio.coroutinefunction
    # * work is a regular Python callable
    # * work is None (get all work from current and/or parent workflow context)

    # TODO: Check whether coroutine is already executing and where.
    # if iscoroutine(coroutine):
    #     return asyncio.run(coroutine, **kwargs)

    # No automatic dispatching yet. Coroutine must be executable
    # in the current or provided context.
    try:
        if context is None:
            context = get_context()
        if context is get_context():
            result = _run(work=work, context=context, **kwargs)
        else:
            with scope(context):
                result = _run(work=work, context=context, **kwargs)
        return result
    except Exception as e:
        message = 'Uncaught exception in scalems.context.run(): {}'.format(str(e))
        warnings.warn(message)
        logger.warning(message)

    # TODO: Consider generalized coroutines to be dispatched through
    #     custom event loops or executors.
