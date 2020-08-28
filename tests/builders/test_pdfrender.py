"""
Test the PdfRender builder.
"""
from disseminate.builders.pdfrender import PdfRender
from disseminate.paths import TargetPath
from disseminate.tags import Tag


def test_pdfrender_with_find_builder_cls():
    """Test the PdfRender builder access with the find_builder_cls."""

    builder_cls = PdfRender.find_builder_cls(in_ext='.render', out_ext='.pdf')
    assert builder_cls.__name__ == "PdfRender"


def test_pdfrender_setup(env):
    """Test the setup of the PdfRender builder."""
    target_root = env.target_root
    cache_path = env.cache_path
    context = env.context

    # Create a tag and template
    context['body'] = Tag(name='body', content='My test body', attributes='',
                          context=context)

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.pdf')
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)

    # Test the paths for the subbuilders
    assert len(pdfrender.subbuilders) == 3
    assert not pdfrender.use_cache

    assert pdfrender.subbuilders[0].__class__.__name__ == 'JinjaRender'
    assert pdfrender.subbuilders[0].use_cache
    assert len(pdfrender.subbuilders[0].parameters) == 4
    assert (pdfrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.tex')

    assert pdfrender.subbuilders[1].__class__.__name__ == 'Latexmk'
    assert pdfrender.subbuilders[1].use_cache
    assert (pdfrender.subbuilders[1].parameters[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (pdfrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.pdf')

    assert pdfrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert not pdfrender.subbuilders[2].use_cache
    assert (pdfrender.subbuilders[2].parameters[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert pdfrender.subbuilders[2].outfilepath == outfilepath

    # And the outfilepath should match the one given
    assert pdfrender.outfilepath == outfilepath


def test_pdfrender_setup_without_outfilepath(env):
    """Test the setup of the PdfRender builder without an outfilepath."""
    context = env.context
    cache_path = env.cache_path
    target_root = env.target_root

    # Create a tag and template
    context['body'] = Tag(name='body', content='My test body', attributes='',
                          context=context)

    # 1. Setup a build without an outfilepath
    pdfrender = PdfRender(env=env, context=context, use_cache=False)

    assert not pdfrender.use_cache
    assert (pdfrender.outfilepath ==
            target_root / 'media' / 'template_8e0eae27545c.pdf')

    # Test the paths for the subbuilders
    assert len(pdfrender.subbuilders) == 3

    assert pdfrender.subbuilders[0].__class__.__name__ == 'JinjaRender'
    assert pdfrender.subbuilders[0].use_cache
    assert len(pdfrender.subbuilders[0].parameters) == 4
    assert (pdfrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.tex')

    assert pdfrender.subbuilders[1].__class__.__name__ == 'Latexmk'
    assert pdfrender.subbuilders[1].use_cache
    assert (pdfrender.subbuilders[1].parameters[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (pdfrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.pdf')

    assert pdfrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert not pdfrender.subbuilders[2].use_cache
    assert (pdfrender.subbuilders[2].parameters[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert (pdfrender.subbuilders[2].outfilepath ==
            target_root / 'media' / 'template_8e0eae27545c.pdf')

    assert pdfrender.outfilepath == (target_root / 'media' /
                                     'template_8e0eae27545c.pdf')

    # 2. Test an example with modification attributes. The final filename should
    #    change.
    pdfrender = PdfRender(parameters=[('scale', 2.0)], env=env, context=context)
    assert pdfrender.outfilepath.target_root == target_root
    assert pdfrender.outfilepath.name != 'template_8e0eae27545c.pdf'
    assert pdfrender.outfilepath.name == 'template_6d2ea7ca1604.pdf'


def test_pdfrender_setup_without_outfilepath_use_cache(env):
    """Test the setup of the PdfRender builder without an outfilepath and
    with the use_cache flag set."""
    context = env.context
    cache_path = env.cache_path
    target_root = env.target_root

    # Create a tag and template
    context['body'] = Tag(name='body', content='My test body', attributes='',
                          context=context)

    # 1. Setup a build without an outfilepath
    pdfrender = PdfRender(env=env, context=context, use_cache=True)

    assert pdfrender.use_cache
    assert (pdfrender.outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.pdf')

    # Test the paths for the subbuilders. There is no copy builder.
    assert len(pdfrender.subbuilders) == 3

    assert pdfrender.subbuilders[0].__class__.__name__ == 'JinjaRender'
    assert pdfrender.subbuilders[0].use_cache
    assert len(pdfrender.subbuilders[0].parameters) == 4
    assert (pdfrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.tex')

    assert pdfrender.subbuilders[1].__class__.__name__ == 'Latexmk'
    assert pdfrender.subbuilders[1].use_cache
    assert (pdfrender.subbuilders[1].parameters[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (pdfrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.pdf')

    assert pdfrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert pdfrender.subbuilders[2].use_cache
    assert (pdfrender.subbuilders[2].parameters[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert (pdfrender.subbuilders[2].outfilepath ==
            cache_path / 'media' / 'template_8e0eae27545c.pdf')

    # 2. Test an example with modification attributes. The final filename should
    #    change.
    pdfrender = PdfRender(parameters=[('scale', 2.0)], env=env, context=context,
                          use_cache=True)
    assert pdfrender.outfilepath.target_root == cache_path
    assert pdfrender.outfilepath.name != 'template_8e0eae27545c.pdf'
    assert pdfrender.outfilepath.name == 'template_6d2ea7ca1604.pdf'


def test_pdfrender_chain_subbuilders(env):
    """Test the chain_subbuilders method for the PdfRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a tag and template
    context['body'] = Tag(name='body', content='My test body', attributes='',
                          context=context)

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.pdf')
    pdfrender = PdfRender(env=env, context=context)
    pdfrender.outfilepath = outfilepath
    pdfrender.chain_subbuilders()

    # Check the paths
    assert len(pdfrender.subbuilders[0].parameters) == 4
    assert (str(pdfrender.subbuilders[0].outfilepath.subpath) ==
            'media/template_8e0eae27545c.tex')
    assert (pdfrender.subbuilders[1].parameters[0] ==
            pdfrender.subbuilders[0].outfilepath)
    assert (str(pdfrender.subbuilders[1].outfilepath.subpath) ==
            'media/template_8e0eae27545c.pdf')
    assert (pdfrender.subbuilders[2].parameters[0] ==
            pdfrender.subbuilders[1].outfilepath)
    assert pdfrender.subbuilders[2].outfilepath == outfilepath
    assert pdfrender.outfilepath == outfilepath


def test_pdfrender_simple(env):
    """Test a simple build with the PdfRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a tag and template
    context['body'] = Tag(name='body', content='My test body', attributes='',
                          context=context)

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
    # Create a tag and template
    context['body'] = Tag(name='body', content='My new test body',
                          attributes='', context=context)
    pdfrender = PdfRender(env=env, context=context, outfilepath=outfilepath)
    assert pdfrender.status == 'ready'

    # 2. Test a build without an outfilepath. Since we use template.tex, it
    #    will be used for the outfilepath
    pdfrender = PdfRender(env=env, context=context)

    assert pdfrender.build(complete=True) == 'done'
    assert (pdfrender.outfilepath ==
            target_root / 'media' / 'template_29f92505a7b8.pdf')
    assert pdfrender.outfilepath.exists()

    # 3. Test a build without an outfilepath but a document target specified.
    pdfrender = PdfRender(env=env, target='.pdf', context=context)

    assert pdfrender.build(complete=True) == 'done'
    assert (pdfrender.outfilepath ==
            target_root / 'pdf' / 'media' / 'template_29f92505a7b8.pdf')
    assert pdfrender.outfilepath.exists()
