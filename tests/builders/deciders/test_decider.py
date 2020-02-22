"""
Test the base Decider
"""
import pytest

from disseminate.builders.deciders import Decider
from disseminate.paths import SourcePath, TargetPath


def test_decider(env):
    """Test the base decider. The base decider only checks that files exist."""
    tmpdir = env.context['target_root']

    # 1. Try an example with input files, output files
    infilepaths = [SourcePath(project_root=tmpdir, subpath='test1.txt'),
                   SourcePath(project_root=tmpdir, subpath='test2.txt')]
    outfilepath = TargetPath(target_root=tmpdir, subpath='out.txt')
    decider = Decider(env=env)

    # Run the build
    kwargs = {'inputs': infilepaths, 'output': outfilepath, 'args': ()}
    with decider.decision(**kwargs) as d:
        # A build should be needed because the files don't exist
        assert d.build_needed

        # Create the files
        for infilepath in infilepaths:
            infilepath.touch()
        outfilepath.touch()

    # The decision should now be that a build_needed is False
    assert not decider.decision(**kwargs).build_needed

    # But build is needed if we delete a file
    infilepaths[0].unlink()
    assert decider.decision(**kwargs).build_needed

    # 2. Try an example in which the build is interrupted
    with pytest.raises(Exception):
        with decider.decision(**kwargs) as d:
            assert d.build_needed

            raise Exception

    # A build is still needed
    assert decider.decision(**kwargs).build_needed

