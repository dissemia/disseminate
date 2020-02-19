import pytest
import pathlib

from disseminate.builders import Environment


@pytest.fixture
def env(tmpdir, context_cls):
    """A build environment"""
    # Setup the context and environment
    tmpdir = pathlib.Path(tmpdir)
    context = context_cls(target_root=tmpdir)

    # Create a new environment so that context is stored on the env instead as
    # weakref (default)
    class TestEnvironment(Environment):
        context = None
    env = TestEnvironment(context=context)
    return env
