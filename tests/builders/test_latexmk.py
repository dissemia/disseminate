"""
Test the Latexmk builder.
"""
from disseminate.builders.latexmk import Latexmk
from disseminate.paths import SourcePath, TargetPath


def test_latexmk_setup(env):
    """Test the setup of the Latexmk builder."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified and a subpath
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    latexmk = Latexmk(infilepaths=infilepath, env=env)

    assert str(latexmk.infilepaths[0].subpath) == 'tex_example1/example1.tex'
    assert str(latexmk.outfilepath.subpath) == 'tex_example1/example1.pdf'
    assert str(target_root) in str(latexmk.outfilepath)

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='mytest.pdf')
    latexmk = Latexmk(infilepaths=infilepath, outfilepath=outfilepath,
                       env=env)

    assert latexmk.infilepaths[0] == infilepath
    assert latexmk.outfilepath == outfilepath


def test_latexmk_simple(env):
    """A simple build for Latexmk."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified.
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    latexmk = Latexmk(infilepaths=infilepath, env=env)
    cache_path = latexmk.cache_path

    # Check the status of the build
    assert latexmk.status == 'ready'

    # Now run the build
    assert latexmk.build(complete=True) == 'done'

    # Check the state of the build
    assert latexmk.status == 'done'
    assert str(cache_path) in str(latexmk.outfilepath)
    assert latexmk.outfilepath.exists()

    # A new builder doesn't need to be run
    latexmk = Latexmk(infilepaths=infilepath, env=env)
    assert latexmk.status == 'done'

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='myfile.pdf')
    latexmk = Latexmk(infilepaths=infilepath, outfilepath=outfilepath, env=env)

    # Check the status of the build
    assert latexmk.status == 'ready'
    assert not outfilepath.exists()

    # Now run the build
    assert latexmk.build(complete=True) == 'done'

    # Check the state of the build
    assert latexmk.status == 'done'
    assert latexmk.outfilepath.exists()

    # Check that the output file is a pdf
    assert b'%PDF' in latexmk.outfilepath.read_bytes()
