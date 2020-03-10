"""
Test the pdflatex builder.
"""
from collections import namedtuple

from disseminate.builders.pdflatex import Pdflatex, PdfRender
from disseminate.paths import SourcePath, TargetPath


def test_pdflatex_setup(env):
    """Test the setup of the Pdflatex builder."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified and a subpath
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    pdflatex = Pdflatex(infilepaths=infilepath, env=env)

    assert str(pdflatex.infilepaths[0].subpath) == 'tex_example1/example1.tex'
    assert str(pdflatex.outfilepath.subpath) == 'tex_example1/example1.pdf'
    assert str(target_root) in str(pdflatex.outfilepath)

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='mytest.pdf')
    pdflatex = Pdflatex(infilepaths=infilepath, outfilepath=outfilepath,
                        env=env)

    assert pdflatex.infilepaths[0] == infilepath
    assert pdflatex.outfilepath == outfilepath


def test_pdflatex_simple(env):
    """A simple build for pdflatex."""
    target_root = env.context['target_root']

    # 1. Test example with the infilepath specified.
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    pdflatex = Pdflatex(infilepaths=infilepath, env=env)
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
    pdflatex = Pdflatex(infilepaths=infilepath, env=env)
    assert pdflatex.status == 'done'

    # 2. Test example with the infilepath and outfilepath specified
    infilepath = SourcePath(project_root='tests/builders',
                            subpath='tex_example1/example1.tex')
    outfilepath = TargetPath(target_root=target_root,
                             subpath='myfile.pdf')
    pdflatex = Pdflatex(infilepaths=infilepath, outfilepath=outfilepath,
                        env=env)

    # Check the status of the build
    assert pdflatex.status == 'ready'
    assert not outfilepath.exists()

    # Now run the build
    assert pdflatex.build(complete=True) == 'done'

    # Check the state of the build
    assert pdflatex.status == 'done'
    assert pdflatex.outfilepath.exists()


def test_pdfrender_setup(env):
    """Test the setup of the PdfRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.pdf')
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)

    # Test the paths for the subbuilders
    assert len(pdfrender.subbuilders) == 3

    assert pdfrender.subbuilders[0].__class__.__name__ == 'JinjaRender'
    assert len(pdfrender.subbuilders[0].infilepaths) == 3
    assert (str(pdfrender.subbuilders[0].outfilepath.subpath) ==
            'a635d8caba43.tex')

    assert pdfrender.subbuilders[1].__class__.__name__ == 'Pdflatex'
    assert (pdfrender.subbuilders[1].infilepaths[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (str(pdfrender.subbuilders[1].outfilepath.subpath) ==
            'a635d8caba43.pdf')

    assert pdfrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert (pdfrender.subbuilders[2].infilepaths[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert pdfrender.subbuilders[2].outfilepath == outfilepath

    assert len(pdfrender.infilepaths) == 3
    assert pdfrender.outfilepath == outfilepath


def test_pdfrender_simple(env):
    """Test a simple build with the PdfRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Test a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.pdf')
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)

    # Check the builder status
    assert not outfilepath.exists()
    assert pdfrender.status == 'ready'

    # Run the build
    assert pdfrender.build(complete=True) == 'done'
    assert pdfrender.status == 'done'
    assert outfilepath.exists()

    # A new builder shouldn't need a build
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)
    assert pdfrender.status == 'done'

    # 2. Changing the render contents should trigger a new build
    context['body'] = Tag(tex='My new test body')
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)
    assert pdfrender.status == 'ready'


    # 2. Test a build without an outfilepath


