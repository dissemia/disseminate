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

    # Run the build
    kwargs = {'inputs': infilepaths, 'output': outfilepath, 'args': ()}
    with decider.decision(**kwargs) as d:
        # A build should be needed because the files don't exist
        assert d.build_needed

        # Create the files
        for count, infilepath in enumerate(infilepaths):
            infilepath.write_text(str(count))
        outfilepath.write_text('out')

    # The decision should now be that a build_needed is False
    assert not decider.decision(**kwargs).build_needed

    # Touch the files. Since the contents remain the same, a build should not
    # be needed
    for count, infilepath in enumerate(infilepaths):
        infilepath.touch()
    outfilepath.touch()

    # The decision should now be that a build_needed is False
    assert not decider.decision(**kwargs).build_needed

    # Changing the arguments will change the build decision
    old_args = kwargs['args']
    kwargs['args'] = ('new',)
    assert decider.decision(**kwargs).build_needed

    kwargs['args'] = old_args
    assert not decider.decision(**kwargs).build_needed

    # Changing one of the files will change its build decision
    for count, infilepath in enumerate(infilepaths):
        infilepath.write_text(str(count + 1))
    assert decider.decision(**kwargs).build_needed

    # 2. Try an example in which the build is interrupted. First, change an
    #    input file so that a build is needed.
    infilepaths[0].write_text('test2')
    with pytest.raises(Exception):
        with decider.decision(**kwargs) as d:
            assert d.build_needed

            raise Exception

    # A build is still needed
    assert decider.decision(**kwargs).build_needed

    # But a build without an exception will work
    with decider.decision(**kwargs) as d:
        assert d.build_needed
        # Exiting this context will set the build_needed to false

    # A build is not needed
    assert not decider.decision(**kwargs).build_needed
