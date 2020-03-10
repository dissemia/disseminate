"""
Test the PdfRender builder.
"""
from collections import namedtuple

from disseminate.builders.pdfrender import PdfRender
from disseminate.paths import TargetPath


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

    # The rendered string should be in the infilepath
    assert any("My test body" in str(f) for f in pdfrender.infilepaths)

    # And the outfilepath should match the one given
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

