"""SCALE-MS - Scalable Adaptive Large Ensembles of Molecular Simulations.

This package provides Python driven data flow scripting and graph execution
for molecular science computational research protocols.

Refer to https://scale-ms.readthedocs.io/ for package documentation.

Refer to https://github.com/SCALE-MS/scale-ms/wiki for development documentation.

Invocation:
    ScaleMS scripts describe a workflow. To run the workflow, you must tell
    ScaleMS how to dispatch the work for execution.

    For most use cases, you can run the script in the context of a particular
    execution scheme by using the ``-m`` Python command line flag to specify a
    ScaleMS execution module::

        # Execute with the default local execution manager.
        python -m scalems.local myworkflow.py
        # Execute with the RADICAL Pilot based execution manager.
        python -m scalems.radical myworkflow.py

    Execution managers can be configured and used from within the workflow script,
    but the user has extra responsibility to properly shut down the execution
    manager, and the resulting workflow may be less portable. For details, refer
    to the documentation for particular WorkflowContexts.

"""
import abc
import contextlib
import functools
import logging
import typing

import scalems.exceptions as exceptions
from .context import get_context
from .subprocess import executable

logger = logging.getLogger(__name__)
logger.debug('Importing {}'.format(__name__))


class ScriptEntryPoint(abc.ABC):
    """Annotate a SCALE-MS entry point function.

    An importable Python script may decorate a callable with scalems.app to
    mark it for execution. This abstract base class provides SCALE-MS with a
    way to identify callables marked for execution and is not intended to be
    used directly.

    See :py:func:`scalems.app`
    """
    name: typing.Optional[str]

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        ...


def app(func: typing.Callable) -> typing.Callable:
    """Annotate a callable for execution by SCALEMS.


    """
    class App(ScriptEntryPoint):
        def __init__(self, func: typing.Callable):
            if not callable(func):
                raise ValueError('Needs a function or function object.')
            self._callable = func
            self.name = None

        def __call__(self, *args, **kwargs):
            return self._callable(*args, **kwargs)

    decorated = functools.update_wrapper(App(func), wrapped=func)

    return decorated


ResultType = typing.TypeVar('ResultType')
class WorkflowObject(typing.Generic[ResultType]): ...


def wait(ref: WorkflowObject[ResultType], **kwargs) -> ResultType:
    """Resolve a workflow reference to a local object.

    ScaleMS commands return abstract references to work without waiting for the
    work to execute. Other ScaleMS commands can operate on these references,
    relying on the framework to manage data flow.

    If you need to extract a concrete result, or otherwise force data flow resolution
    (blocking the current code until execution and data transfer are complete),
    you may use scalems.wait(ref) to convert a workflow reference to a concrete
    local result.

    Note that scalems.wait() can allow the current scope to yield to other tasks.
    Developers should use scalems.wait() instead of native concurrency primitives
    when coding for dynamic data flow.

    .. todo:: Establish stable API/CPI for tasks that create other tasks or modify the data flow graph during execution.

    scalems.wait() will produce an error if you have not configured and launched
    an execution manager in the current scope.
    """
    from . import context
    return context.wait(ref, **kwargs)


def run(ref: WorkflowObject[ResultType], context=None, **kwargs) -> ResultType:
    """Execute a workflow and return the results.

    This call is not necessary if an execution manager is already running, such
    as when a workflow script is invoked with `python -m scalems.<some_executor> workflow.py`,
    when run in a Jupyter notebook (or other application with a compatible native event loop),
    or when the execution manager is launched explicitly within the script.

    `scalems.run()` may be useful if you want to embed a ScaleMS application in another
    application, or as a short-hand for execution management with the Python
    Context Manager syntax by which ScaleMS execution can be more explicitly directed.
    `scalems.run()` is analogous to (and may simply wrap a call to) `asyncio.run()`.

    As with `asyncio.run()`, `scalems.run()` is intended to be invoked (from the
    main thread) exactly once in a Python interpreter process lifetime. It is
    probably fine to call it more than once, but such a use case probably indicates
    non-standard ScaleMS software design. Nested calls to `scalems.run()` have
    unspecified behavior.
    """
    from .context import run

    # Get asyncio event loop. Use existing event loop or get a new one.
    # Dispatch according to the current WorkflowManager context.
    # If specific work is not requested, scan the local scope for scalems tasks,
    # dispatch them according to the current WorkflowManager context, and run
    # all managed work.

    return run(ref, context=context, **kwargs)


def function_wrapper(output: dict = None):
    # Suppress warnings in the example code.
    # noinspection PyUnresolvedReferences
    """Generate a decorator for wrapped functions with signature manipulation.

    New function accepts the same arguments, with additional arguments required by
    the API.

    The new function returns an object with an ``output`` attribute containing the named outputs.

    Example:

        >>> @function_wrapper(output={'spam': str, 'foo': str})
        ... def myfunc(parameter: str = None, output=None):
        ...    output.spam = parameter
        ...    output.foo = parameter + ' ' + parameter
        ...
        >>> operation1 = myfunc(parameter='spam spam')
        >>> assert operation1.spam.result() == 'spam spam'
        >>> assert operation1.foo.result() == 'spam spam spam spam'

    Arguments:
        output (dict): output names and types

    If ``output`` is provided to the wrapper, a data structure will be passed to
    the wrapped functions with the named attributes so that the function can easily
    publish multiple named results. Otherwise, the ``output`` of the generated operation
    will just capture the return value of the wrapped function.
    """
    raise exceptions.MissingImplementationError()


def subgraph(variables=None):
    """Allow operations to be configured in a sub-context.

    The object returned functions as a Python context manager. When entering the
    context manager (the beginning of the ``with`` block), the object has an
    attribute for each of the named ``variables``. Reading from these variables
    gets a proxy for the initial value or its update from a previous loop iteration.
    At the end of the ``with`` block, any values or data flows assigned to these
    attributes become the output for an iteration.

    After leaving the ``with`` block, the variables are no longer assignable, but
    can be called as bound methods to get the current value of a variable.

    When the object is run, operations bound to the variables are ``reset`` and
    run to update the variables.

    Example::

        @scalems.function_wrapper(output={'data': float})
        def add_float(a: float, b: float) -> float:
            return a + b

        @scalems.function_wrapper(output={'data': bool})
        def less_than(lhs: float, rhs: float, output=None):
            output.data = lhs < rhs

        subgraph = scalems.subgraph(variables={'float_with_default': 1.0, 'bool_data': True})
        with subgraph:
            # Define the update for float_with_default to come from an add_float operation.
            subgraph.float_with_default = add_float(subgraph.float_with_default, 1.).output.data
            subgraph.bool_data = less_than(lhs=subgraph.float_with_default, rhs=6.).output.data
        operation_instance = subgraph()
        operation_instance.run()
        assert operation_instance.values['float_with_default'] == 2.

        loop = scalems.while_loop(function=subgraph, condition=subgraph.bool_data)
        handle = loop()
        assert handle.output.float_with_default.result() == 6

    """
    raise exceptions.MissingImplementationError()


def logical_not(value):
    """Negate boolean inputs."""
    raise exceptions.MissingImplementationError()


def logical_and(iterable):
    """Produce a boolean value resulting from the logical AND of the elements of the input.

    The API does not specify whether the result is published before all values
    of *iterable* have been inspected, but (for checkpointing, reproducibility,
    and simplicity of implementation), the operation is not marked "complete"
    until all inputs have been resolved.
    """
    raise exceptions.MissingImplementationError()


def while_loop(*, function, condition, max_iteration=10, **kwargs):
    """Generate and run a chain of operations such that condition evaluates True.

    Returns a reference that acts like a single operation in the current
    work graph, but which is a proxy to the operation at the end of a dynamically generated chain
    of operations. At run time, *condition* is evaluated for the last element in
    the current chain. If *condition* evaluates False, the chain is extended and
    the next element is executed. When *condition* evaluates True, the object
    returned by `while_loop` becomes a proxy for the last element in the chain.

    TODO: Allow external access to intermediate results / iterations?

    Arguments:
        function: a callable that produces an instance of an operation when called (with ``**kwargs``, if provided).
        condition: a call-back that returns a boolean when provided an operation instance.
        max_iteration: execute the loop no more than this many times (default 10)

    *function* (and/or *condition*) may be a "partial function" and/or stateful function object
    (such as is produced by subgraph()) in order to retain state between iterations.

    TODO: Specify requirements of *function* and *condition*. (Picklable? scalems.Function compatible?)

    TODO: Describe how *condition* could be fed asynchronously from outside of the wrapped *function*.

    TODO: Does *condition* need to evaluate directly to a native bool, or do we
        detect whether a Future is produced, and call ``result()`` if necessary?

    Warning:
        *max_iteration* is provided in part to minimize the cost of bugs in early
        versions of this software. The default value may be changed or
        removed on short notice.

    """
    raise exceptions.MissingImplementationError()


def desequence(iterable):
    """Remove sequencing from an iterable.

    Given an input of shape (N, [M, ...]), produce an iterable of resources
    (of shape (M,...)). Ordering information from the outer dimension is lost,
    even in an ensemble scope, in which parallel data flows generally retain
    their ordering.

    This allows iterative tools (e.g. `map`) to use unordered or asynchronous
    iteration on resource slices as they become available.
    """
    raise exceptions.MissingImplementationError()


def resequence(keys, collection):
    """Set the order of a collection.

    Use the ordered list of keys to define the sequence of the elements in the
    collection.

    In addition to reordering an ordered collection, this function is useful
    for applying a sequence from one part of a work flow to data that has been
    processed asynchronously.
    """
    raise exceptions.MissingImplementationError()


def gather(iterable):
    """Convert an iterable or decomposable collection to a complete collection.

    Use to synchronize/localize data. Reference with ambiguous dimensionality or
    decomposable dimensions are converted to references with concrete dimensionality
    and non-decomposable dimensions. When the output of *gather* is used as input
    to another function, the entire results of *iterable* are available in the
    operation context.

    This function should generally not be necessary when defining a work flow,
    but may be necessary to disambiguate data flow topology, such as when N
    operations should each consume an N-dimensional resource in its entirety,
    in which case, *gather* is implicitly an *all_gather*.

    Alternatives:
        For decomposable dimensions, we may want to allow a named *scope* for
        the decomposition. Then, explicit *gather* use cases would be replaced
        by an annotation to change the *scope* for a dimension, and, as part of
        a function implementation's assertion of its decomposability, a function
        could express its ensemble/decomposition behavior in terms of a particular
        target scope of an operation.
    """
    raise exceptions.MissingImplementationError()


def scatter(iterable, axis=1):
    """Explicitly decompose data.

    For input with outer dimension size N and dimensionality D,
    or for an iterable of length N and elements with dimensionality D-1,
    produce a Resource whose outer dimensions are decomposed down to dimension
    D-*axis*.

    Note: This function is not necessary if we either require fixed dimensionality
    of function inputs or minimize implicit broadcast, scatter, and gather behavior.
    Otherwise, we will need to disambiguate decomposition.
    """
    raise exceptions.MissingImplementationError()


def reduce(function, iterable):
    """Repeatedly apply a function.

    For an Iterable[T] and a function that maps (T, T) -> T, apply the function
    to map Iterable[T] -> T. Assumes *function* is associative.

    If *iterable* is ordered, commutation of operands is preserved,
    but associativity of the generated operations is not specified.
    If *iterable* is unordered, the caller is responsible for ensuring that
    *function* obeys the commutative property.

    Compare to :py:func:`functools.reduce`
    """
    raise exceptions.MissingImplementationError()


def extend_sequence(sequence_a, sequence_b):
    """Combine sequential data into a new sequence."""
    raise exceptions.MissingImplementationError()


def map(function, iterable, shape=None):
    """Generate a collection of operations by iteration.

    Apply *function* to each element of *iterable*.

    If *iterable* is ordered, the generated operation collection is ordered.

    If *iterable* is unordered, the generated operation collection is unordered.
    """
    raise exceptions.MissingImplementationError()


def poll():
    """Inspect the execution status of an operation.

    Inspects the execution graph state in the current context at the time of
    execution.

    Used in a work graph, this adds a non-deterministic aspect, but adds truly
    asynchronous adaptability.
    """
    raise exceptions.MissingImplementationError()
