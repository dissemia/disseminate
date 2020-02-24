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

    # A build is needed
    decision = decider.decision
    kwargs = {'inputs': infilepaths, 'output': outfilepath}
    assert decision.build_needed(**kwargs)

    # Create the files and run the build
    for infilepath in infilepaths:
        infilepath.touch()
    outfilepath.touch()

    # The decision should now be that a build_needed is False
    assert not decision.build_needed(**kwargs)

    # But build is needed if we delete a file.
    infilepaths[0].unlink()
    assert decision.build_needed(**kwargs)  # cached value

    # 2. Try an example in which the build is interrupted
    with pytest.raises(Exception):
        assert decision.build_needed(**kwargs)
        raise Exception

    # A build is still needed
    assert decision.build_needed(**kwargs)
