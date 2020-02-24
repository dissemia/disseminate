"""
Test the Md5Decider
"""
import pytest

from disseminate.builders.deciders import Md5Decider
from disseminate.paths import SourcePath, TargetPath


def test_md5decider(env):
    """Test the functionality of the md5decider"""
    tmpdir = env.context['target_root']

    # 1. Try an example with input files, output files
    infilepaths = [SourcePath(project_root=tmpdir, subpath='test1.txt'),
                   SourcePath(project_root=tmpdir, subpath='test2.txt')]
    outfilepath = TargetPath(target_root=tmpdir, subpath='out.txt')
    decider = Md5Decider(env=env)

    # The files aren't created yet, so a build is needed
    kwargs = {'inputs': infilepaths, 'output': outfilepath}
    decision = decider.decision
    assert decision.build_needed(**kwargs)

    # Run the build. Create the files
    for count, infilepath in enumerate(infilepaths):
        infilepath.write_text(str(count))
    outfilepath.write_text('out')

    # The decision has a cached hash, and it will still find that a build is
    # needed
    assert decision.build_needed(**kwargs)

    # However, resetting the decision will load the current value: a build is
    # not needed
    assert not decision.build_needed(**kwargs, reset=True)

    # And a new decision will report the same.
    decision = decider.decision
    assert not decision.build_needed(**kwargs)

    # Touch the files. Since the contents remain the same, a build should not
    # be needed
    for count, infilepath in enumerate(infilepaths):
        infilepath.touch()
    outfilepath.touch()

    # The decision should now be that a build_needed is False
    assert not decision.build_needed(**kwargs)

    # Changing the arguments will change the build decision
    kwargs['inputs'] = kwargs['inputs'] + ['new']
    assert not decision.build_needed(**kwargs)  # Cache value
    decision = decider.decision                 # new decision needed
    assert decision.build_needed(**kwargs)

    kwargs['inputs'] = infilepaths
    assert decision.build_needed(**kwargs)  # Cache value
    decision = decider.decision             # new decision needed
    assert not decision.build_needed(**kwargs)

    # Changing one of the files will change its build decision
    for count, infilepath in enumerate(infilepaths):
        infilepath.write_text(str(count + 1))

    decision = decider.decision  # new decision needed
    assert decision.build_needed(**kwargs)

    # 2. Try an example in which the build is interrupted. First, change an
    #    input file so that a build is needed.
    decision = decider.decision

    with pytest.raises(Exception):
        infilepaths[0].write_text('test2')
        raise Exception
        decision.build_needed(**kwargs, reset=True)

    # A build is still needed
    assert decision.build_needed(**kwargs)

    # But a the decision can still be reset
    assert not decision.build_needed(**kwargs, reset=True)
