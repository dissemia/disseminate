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

    # Initially the files are missing
    decision.build_needed(**kwargs)

    # Create the input files. The output file doesn't exist, so a build is
    # needed
    for infilepath in infilepaths:
        infilepath.touch()

    assert decision.build_needed(**kwargs)

    # Now create the output file and a build is no longer be needed
    outfilepath.touch()
    assert not decision.build_needed(**kwargs)

    # But build is needed if we delete the output file
    outfilepath.unlink()
    assert decision.build_needed(**kwargs)  # cached value

    # 2. Try an example in which the build is interrupted
    with pytest.raises(Exception):
        assert decision.build_needed(**kwargs)
        raise Exception

    # A build is still needed
    assert decision.build_needed(**kwargs)
