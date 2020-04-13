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
            'template_b9b44d13de71.tex')

    assert pdfrender.subbuilders[1].__class__.__name__ == 'Latexmk'
    assert (pdfrender.subbuilders[1].infilepaths[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (str(pdfrender.subbuilders[1].outfilepath.subpath) ==
            'template_b9b44d13de71.pdf')

    assert pdfrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert (pdfrender.subbuilders[2].infilepaths[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert pdfrender.subbuilders[2].outfilepath == outfilepath

    # The rendered string should be in the infilepaths
    assert any("My test body" in str(f) for f in pdfrender.infilepaths)

    # And the outfilepath should match the one given
    assert pdfrender.outfilepath == outfilepath


def test_pdfrender_chain_subbuilders(env):
    """Test the chain_subbuilders method for the PdfRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.pdf')
    pdfrender = PdfRender(env=env, context=context)
    pdfrender.outfilepath = outfilepath
    pdfrender.chain_subbuilders()

    # Check the paths
    assert len(pdfrender.subbuilders[0].infilepaths) == 3
    assert (str(pdfrender.subbuilders[0].outfilepath.subpath) ==
            'template_b9b44d13de71.tex')
    assert (pdfrender.subbuilders[1].infilepaths[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (str(pdfrender.subbuilders[1].outfilepath.subpath) ==
            'template_b9b44d13de71.pdf')
    assert (pdfrender.subbuilders[2].infilepaths[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert pdfrender.subbuilders[2].outfilepath == outfilepath

    assert any("My test body" in str(f) for f in pdfrender.infilepaths)
    assert pdfrender.outfilepath == outfilepath


def test_pdfrender_setup_without_outfilepath(env):
    """Test the setup of the PdfRender builder without an outfilepath."""
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build without an outfilepath
    pdfrender = PdfRender(env=env, context=context)

    assert len(pdfrender.infilepaths) == 3
    assert str(pdfrender.outfilepath.subpath) == 'template_b9b44d13de71.pdf'


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

    # 2. Test a build without an outfilepath. Since we use template.tex, it
    #    will be used for the outfilepath
    pdfrender = PdfRender(env=env, context=context)

    assert pdfrender.build(complete=True) == 'done'
    assert pdfrender.outfilepath.target_root == env.cache_path
    assert str(pdfrender.outfilepath.target) == '.'
    assert str(pdfrender.outfilepath.subpath) == 'template_e343d4a49636.pdf'
    assert pdfrender.outfilepath.exists()

    # 3. Test a build without an outfilepath but a document target specified.
    pdfrender = PdfRender(env=env, target='.pdf', context=context)

    assert pdfrender.build(complete=True) == 'done'
    assert pdfrender.outfilepath.target_root == env.cache_path
    assert str(pdfrender.outfilepath.target) == 'pdf'
    assert str(pdfrender.outfilepath.subpath) == 'template_e343d4a49636.pdf'
    assert pdfrender.outfilepath.exists()
