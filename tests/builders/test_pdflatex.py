"""
Test the Pdflatex builder.
"""
from disseminate.builders.pdflatex import Pdflatex
from disseminate.paths import SourcePath, TargetPath


def test_pdflatex_setup(env):
    """Test the setup of the Pdflatex builder."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified and a subpath
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    pdflatex = Pdflatex(parameters=infilepath, env=env)

    assert str(pdflatex.parameters[0].subpath) == 'ex3/dummy.tex'
    assert str(pdflatex.outfilepath.subpath) == 'media/ex3/dummy.pdf'
    assert str(target_root) in str(pdflatex.outfilepath)

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='mytest.pdf')
    pdflatex = Pdflatex(parameters=infilepath, outfilepath=outfilepath,
                        env=env)

    assert pdflatex.parameters[0] == infilepath
    assert pdflatex.outfilepath == outfilepath


def test_pdflatex_simple(env):
    """A simple build for Pdflatex."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified.
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    pdflatex = Pdflatex(parameters=infilepath, env=env)
    cache_path = pdflatex.cache_path

    # Check the status of the build
    assert pdflatex.status == 'ready'

    # Now run the build
    assert pdflatex.build(complete=True) == 'done'

    # Check the state of the build
    assert pdflatex.status == 'done'
    assert str(cache_path) in str(pdflatex.outfilepath)
    assert pdflatex.outfilepath.exists()

    # A new builder doesn't need to be run
    pdflatex = Pdflatex(parameters=infilepath, env=env)
    assert pdflatex.status == 'done'

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders/examples',
                            subpath='ex3/dummy.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='myfile.pdf')
    pdflatex = Pdflatex(parameters=infilepath, outfilepath=outfilepath,
                        env=env)

    # Check the status of the build
    assert pdflatex.status == 'ready'
    assert not outfilepath.exists()

    # Now run the build
    assert pdflatex.build(complete=True) == 'done'

    # Check the state of the build
    assert pdflatex.status == 'done'
    assert pdflatex.outfilepath.exists()

    # Check that the output file is a pdf
    assert b'%PDF' in pdflatex.outfilepath.read_bytes()
