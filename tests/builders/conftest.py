import pytest
import pathlib

from disseminate.builders import Environment
from disseminate.paths import SourcePath, TargetPath


@pytest.fixture
def env(tmpdir):
    """A build environment"""
    # Setup the paths
    tmpdir = pathlib.Path(tmpdir)
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=tmpdir, subpath='test.dm')
    src_filepath.touch()

    # Create a new environment so that context is stored on the env instead as
    # weakref (default)
    class TestEnvironment(Environment):
        context = None

    env = TestEnvironment(src_filepath=src_filepath, target_root=target_root)
    return env
