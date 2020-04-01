"""
Test the Copy Builder
"""
from disseminate.builders.copy import Copy
from disseminate.paths import SourcePath, TargetPath


def test_copy(env):
    """Test the copy builder"""
    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='out.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile'

    # 2. Try modifying the contents of the outfile. Now the outfile is newer
    #    than the infile, but its contents don't match the hash
    targetpath.write_text('outfile')

    cp = Copy(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.build() == 'done'
    assert targetpath.read_text() == 'infile'


def test_copy_no_outfilepath(env):
    """Test the copy builder without an outfilepath specified"""

    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')

    # If not outfilepath is specified, a file in the cache directory is created
    targetpath = TargetPath(target_root=tmpdir / '.cache', subpath='in.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, infilepaths=infilepath)

    assert cp.build(complete=True) == 'done'
    assert cp.outfilepath == targetpath


def test_copy_samefile(env):
    """Test the copy builder using the same file."""
    tmpdir = env.context['target_root']
    infilepath = SourcePath(project_root=tmpdir, subpath='in.txt')
    targetpath = TargetPath(target_root=tmpdir, subpath='in.txt')

    # 1. Test a build that copies the file
    infilepath.write_text('infile')
    cp = Copy(env=env, infilepaths=infilepath, outfilepath=targetpath)

    assert cp.status == 'done'
    assert cp.build(complete=True) == 'done'
    assert targetpath.read_text() == 'infile'

