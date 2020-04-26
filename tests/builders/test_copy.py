"""
Test the Copy Builder
"""
from disseminate.builders.copy import Copy
from disseminate.paths import SourcePath, TargetPath


def test_copy_with_find_builder_cls():
    """Test the Copy builder access with the find_builder_cls."""

    builder_cls = Copy.find_builder_cls(in_ext='.*', out_ext='.*')
    assert builder_cls.__name__ == "Copy"


def test_copy_no_outfilepath(env):
    """Test the copy builder without an outfilepath specified"""

    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')

    # If not outfilepath is specified, a file in the cache directory is created
    targetpath = TargetPath(target_root=env.cache_path, subpath='media/in.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, parameters=infilepath)

    assert cp.build(complete=True) == 'done'
    assert cp.outfilepath == targetpath


def test_copy_build(env):
    """Test the Copy builder build"""
    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='out.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile'

    # 2. Try modifying the contents of the outfile. Now the outfile is newer
    #    than the infile, but its contents don't match the hash
    targetpath.write_text('outfile')

    cp = Copy(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.build() == 'done'
    assert targetpath.read_text() == 'infile'


def test_copy_build_infilepath_missing(env):
    """Test the Copy builder build with a missing infilepath"""
    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='out.txt')

    # 1. Test a build that copies the file
    cp = Copy(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.status == 'missing (parameters)'
    assert cp.build(complete=True) == 'missing (parameters)'
    assert cp.status == 'missing (parameters)'


def test_copy_samefile(env):
    """Test the copy builder using the same file."""
    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='in.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, parameters=infilepath, outfilepath=targetpath)

    assert cp.status == 'done'
    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile'

