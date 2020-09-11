"""Dispatch scalems.exec through RADICAL Pilot.

In the first draft, we keep the tests simpler by assuming we are invoked in an
environment where RP is already configured. In a follow-up, we will use a
dispatching layer to run meaningful tests through an RP Context specialization.
In turn, the initial RP dispatching will probably use a Docker container to
encapsulate the details of the RP-enabled environment, such as the required
MongoDB instance and RADICAL_PILOT_DBURL environment variable.
"""

import os
import warnings

import pytest
import scalems
import scalems.context
import scalems.radical

def get_rp_decorator():
    """Decorator for tests that should be run in a RADICAL Pilot environment only."""
    try:
        import radical.pilot as rp
        import radical.utils as ru
    except ImportError:
        rp = None
        ru = None

    with_radical_only = pytest.mark.skipif(
        rp is None or ru is None or 'RADICAL_PILOT_DBURL' not in os.environ,
        reason="Test requires RADICAL environment.")

    # The above logic may not be sufficient to mark the usability of the RP environment.
    if rp is not None and 'RADICAL_PILOT_DBURL' in os.environ:
        try:
            # Note: radical.pilot.Session creation causes several deprecation warnings.
            # Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', category=DeprecationWarning)
                with rp.Session():
                    with_radical_only = pytest.mark.skipif(False,
                                                           reason="RP should be available.")
        except:
            with_radical_only = pytest.mark.skip(reason="Cannot create radical.pilot.Session")

    return with_radical_only


# Decorator for tests that should be run in a RADICAL Pilot environment only.
with_radical_only = get_rp_decorator()


@pytest.fixture
def rp_config():
    """Provide a RADICAL Pilot Resource Config to a test suite.

    The 'resource' key in a Pilot Description must name a key that the Session
    can use to get default values for the execution environment.
    """
    # Ref: https://radicalpilot.readthedocs.io/en/stable/machconf.html#customizing-resource-configurations-programatically
    import radical.pilot as rp
    import radical.utils as ru
    # TODO: Resolve usage error.
    # Ref: https://github.com/radical-cybertools/radical.pilot/issues/2181
    try:
        cfg = rp.ResourceConfig('local.localhost', ru.Config('radical.pilot.session', name='default', cfg=None))
    except:
        cfg = dict()
    # `local.localhost` is preconfigured, but some of the properties are likely not appropriate.
    # Ref: https://github.com/radical-cybertools/radical.pilot/blob/devel/src/radical/pilot/configs/resource_local.json
    # TODO: Is there a more canonical way to programmatically generate a valid config?
    # Ref: https://radicalpilot.readthedocs.io/en/stable/machconf.html#writing-a-custom-resource-configuration-file
    # TODO: Set a sensible number of cores / threads / GPUs.
    return dict(config=cfg, rp=rp, ru=ru)


@with_radical_only
def test_rp_import():
    """Confirm availability of RADICAL Pilot infrastructure.

    Tests here may be too cumbersome to run in every invocation of a pytest fixture,
    so let's just run them once in this unit test.
    """
    import radical.pilot as rp
    import radical.utils as ru
    assert rp is not None
    assert ru is not None
    assert 'RADICAL_PILOT_DBURL' in os.environ
    # TODO: Assert the presence of required ResourceConfig source file(s)...
    # assert os.path.exists()


# Note: radical.pilot.Session creation causes several deprecation warnings.
# Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@with_radical_only
def test_rp_basic_task(rp_config):
    rp = rp_config['rp']

    # Note: Session creation will fail with a FileNotFound error unless venv is explicitly `activate`d.
    # TODO: Figure out what `activate` does that `rp-venv/bin/python` doesn't do.
    with rp.Session() as session:
        # Based on `radical.pilot/examples/config.json`
        # TODO: Does the Session have a default spec for 'local.localhost'? Can/should we reference it?
        # See also https://github.com/radical-cybertools/radical.pilot/issues/2181
        resource = 'local.localhost'
        resource_config = {resource: {}}
        if resource in rp_config['config']:
            resource_config[resource].update(rp_config.config[resource])
        resource_config[resource].update({
            'project': None,
            'queue': None,
            'schema': None,
            'cores': 1,
            'gpus': 0
        })

        pilot_description = dict(resource=resource,
                                 runtime=30,
                                 exit_on_error=True,
                                 project=resource_config[resource]['project'],
                                 queue=resource_config[resource]['queue'],
                                 cores=resource_config[resource]['cores'],
                                 gpus=resource_config[resource]['gpus'])

        pmgr = rp.PilotManager(session=session)
        umgr = rp.UnitManager(session=session)
        pilot = pmgr.submit_pilots(rp.ComputePilotDescription(pilot_description))
        umgr.add_pilots(pilot)

        task_description = {'executable': '/bin/date',
                            'cpu_processes': 1,
                            }

        task = umgr.submit_units(rp.ComputeUnitDescription(task_description))

        # Can we wait for `task` instead of waiting for all units?
        task.wait()
        assert task.exit_code == 0

        # Do we need to do umgr.wait_units()? Should this be (or is it already) a responsibility of rp.Session?
        umgr.wait_units()

    assert session.closed


# Note: radical.pilot.Session creation causes several deprecation warnings.
# Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@with_radical_only
def test_basic_rp_executor(rp_config):
    """Test the execution-side RP execution support.

    A master task (or hierarchy of callers) must be able to deserialize a record
    containing one or more tasks, place the tasks with the provided RP facilities,
    and prepare the results package to be conveyed to the client.

    Ref https://github.com/SCALE-MS/scale-ms/issues/69
    """
    rp = rp_config['rp']

    # Note: Session creation will fail with a FileNotFound error unless venv is explicitly `activate`d.
    # TODO: Figure out what `activate` does that `rp-venv/bin/python` doesn't do.
    with rp.Session() as session:
        # Based on `radical.pilot/examples/config.json`
        # TODO: Does the Session have a default spec for 'local.localhost'? Can/should we reference it?
        # See also https://github.com/radical-cybertools/radical.pilot/issues/2181
        resource = 'local.localhost'
        resource_config = {resource: {}}
        if resource in rp_config['config']:
            resource_config[resource].update(rp_config.config[resource])
        resource_config[resource].update({
            'project': None,
            'queue': None,
            'schema': None,
            'cores': 1,
            'gpus': 0
        })

        pilot_description = dict(resource=resource,
                                 runtime=30,
                                 exit_on_error=True,
                                 project=resource_config[resource]['project'],
                                 queue=resource_config[resource]['queue'],
                                 cores=resource_config[resource]['cores'],
                                 gpus=resource_config[resource]['gpus'])

        pmgr = rp.PilotManager(session=session)
        umgr = rp.UnitManager(session=session)
        pilot = pmgr.submit_pilots(rp.ComputePilotDescription(pilot_description))

        # TODO: How will the scalems tool be loaded in the RP agent environment?
        with scalems.radical.RPExecutionContext(umgr) as director:
            # TODO: How will the record be provided to the scalems tool for deserialization?
            # TODO: How will the scalems tool reconcile data referenced in the work record
            #       with input data staged or not staged?

            # TODO: Use base from typing support / serialization module.
            task_record = {
                'label': 'test1',
                'operation': ['scalems', 'executable'],
                'argv': ['/bin/echo', 'hi', 'there'],
                'stdout': ['stdout.txt']
            }
            serialized = json.dumps(task_record)

            # task = umgr.submit_units(rp.ComputeUnitDescription(task_description))
            director.add(serialized)

            task_view = director.task(label='test1')

            # Wait for deserialized work to complete.
            result = task_view.result()
            assert task_view.done()
            assert result.exit_code == 0

            # Assert no remaining RP work.

        umgr.add_pilots(pilot)
        umgr.wait_units()

    assert session.closed



# Deferred: Test correct handling of work with execution dependencies.
# def test_pipeline_rp_executor(rp_config):

# Deferred: Test that we provide correct handling of work loads with external
# dependencies in accordance with the current middleware spec. External dependencies
# may indicate dependence on previous work loads, locally expired cached data
# (such as when recovering a partially executed work flow), or a malformed work record.
# def test_external_data_references_rp_exector(rp_config):

# Note: radical.pilot.Session creation causes several deprecation warnings.
# Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@pytest.mark.asyncio
@with_radical_only
async def test_trivial_exec_rp():
    original_context = scalems.context.get_context()
    # Test RPDispatcher context
    # Note that a coroutine object created from an `async def` function is only awaitable once.
    context = scalems.radical.RPWorkflowContext()
    async with context as session:
        cmd = scalems.executable(('/bin/echo',))
        await session.run()
    # Test active context scoping.
    assert scalems.context.get_context() is original_context


# TODO: Manage temporary directory for workflow.
# Note: radical.pilot.Session creation causes several deprecation warnings.
# Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@pytest.mark.asyncio
@with_radical_only
async def test_basic_cli_exec_rp():
    # Test RPDispatcher context
    # Note that a coroutine object created from an `async def` function is only awaitable once.
    context = scalems.radical.RPWorkflowContext()
    async with context as session:
        cmd = scalems.executable(('/bin/echo', 'hi', 'there'), stout='stdout.txt')
        # TODO: stdout file management
        # outfile = cmd.stdout.result()
        await session.run()
    # TODO: output checking
    # with open(outfile, 'r') as fh:
    #     words = fh.readline().rstrip().split()
    #     assert words[0] == "hi"
    #     assert words[1] == "there"


# TODO: Manage temporary directory for workflow.
# TODO: Test fixture for sample MDP input.
# TODO: Test fixture for sample topology input.
# TODO: Test fixture for sample GRO coordinates input.
# TODO: Test fixture for Gromacs entry point.
# TODO: scalems.outputfile annotator support.
# Note: radical.pilot.Session creation causes several deprecation warnings.
# Ref https://github.com/radical-cybertools/radical.pilot/issues/2185
@pytest.mark.xfail
@pytest.mark.filterwarnings('ignore::DeprecationWarning')
@pytest.mark.asyncio
@with_radical_only
async def test_gmxapi_rp(mdpfile, gmx, gmx_topology, gmx_gro):
    # Test RPDispatcher context
    # Note that a coroutine object created from an `async def` function is only awaitable once.
    context = scalems.radical.RPWorkflowContext()
    async with context as session:
        preprocess = scalems.executable((gmx, 'grompp', '-f', scalems.file(mdpfile), '-p', scalems.file(gmx_topology), '-c', scalems.file(gmx_gro)),
                                        outputs={'-o': scalems.outputfile(suffix='.tpr')})
        md = scalems.wrappers.gromacs.simulate(preprocess.file['-o'])
        # TODO: file management
        # assert os.path.exists(md.trajectory.result())
        await session.run()
