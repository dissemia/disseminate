"""
Tests for the SvgRender builder.
"""
from collections import namedtuple

from disseminate.builders.svgrender import SvgRender
from disseminate.paths import TargetPath


def test_svgrender_with_find_builder_cls():
    """Test the SvgRender builder access with the find_builder_cls."""

    builder_cls = SvgRender.find_builder_cls(in_ext='.render', out_ext='.svg')
    assert builder_cls.__name__ == "SvgRender"


def test_svgrender_setup(env):
    """Test the setup of the SvgRender builder."""
    target_root = env.context['target_root']
    context = env.context
    target_root = env.target_root
    cache_path = env.cache_path

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.svg')
    svgrender = SvgRender(env=env, context=context, outfilepath=outfilepath)

    # Test the paths for the subbuilders
    assert len(svgrender.subbuilders) == 3
    assert not svgrender.use_cache

    assert svgrender.subbuilders[0].__class__.__name__ == 'PdfRender'
    assert svgrender.subbuilders[0].use_cache
    assert (svgrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.pdf')

    assert svgrender.subbuilders[1].__class__.__name__ == 'Pdf2SvgCropScale'
    assert svgrender.subbuilders[1].use_cache
    assert (svgrender.subbuilders[1].parameters[0] ==
            svgrender.subbuilders[0].outfilepath)
    assert (svgrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.svg')

    assert svgrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert not svgrender.subbuilders[2].use_cache
    assert (svgrender.subbuilders[2].parameters[0] ==
            svgrender.subbuilders[1].outfilepath)
    assert svgrender.subbuilders[2].outfilepath == outfilepath

    # The outfilepath should match the one given
    assert svgrender.outfilepath == outfilepath

    # The rendered string should be in the parameters
    assert any(["My test body" in str(f) for f in svgrender.parameters])


def test_svgrender_setup_without_outfilepath(env):
    """Test the setup of the SvgRender builder without an outfilepath."""
    context = env.context
    cache_path = env.cache_path
    target_root = env.target_root

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build without an outfilepath
    svgrender = SvgRender(env=env, context=context, use_cache=False)

    assert not svgrender.use_cache
    assert (svgrender.outfilepath ==
            target_root / 'media' / 'template_b9b44d13de71.svg')

    # Test the paths for the subbuilders
    assert len(svgrender.subbuilders) == 3

    assert svgrender.subbuilders[0].__class__.__name__ == 'PdfRender'
    assert svgrender.subbuilders[0].use_cache
    assert len(svgrender.subbuilders[0].parameters) == 3
    assert (svgrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.pdf')

    assert svgrender.subbuilders[1].__class__.__name__ == 'Pdf2SvgCropScale'
    assert svgrender.subbuilders[1].use_cache
    assert (svgrender.subbuilders[1].parameters[0] ==
            svgrender.subbuilders[0].outfilepath)
    assert (svgrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.svg')

    assert svgrender.subbuilders[2].__class__.__name__ == 'Copy'
    assert not svgrender.subbuilders[2].use_cache
    assert (svgrender.subbuilders[2].parameters[0] ==
            svgrender.subbuilders[1].outfilepath)
    assert (svgrender.subbuilders[2].outfilepath ==
            target_root / 'media' / 'template_b9b44d13de71.svg')

    assert svgrender.outfilepath == (target_root / 'media' /
                                     'template_b9b44d13de71.svg')

    # 2. Test an example with modification attributes. The final filename should
    #    change.
    svgrender = SvgRender(parameters=[('scale', 2.0)], env=env, context=context)
    assert svgrender.outfilepath.target_root == target_root
    assert str(svgrender.outfilepath.subpath) != ('media/template_'
                                                  'b9b44d13de71.svg')
    assert str(svgrender.outfilepath.subpath) == ('media/template_'
                                                  '1b0167b8955c.svg')


def test_svgrender_setup_without_outfilepath_use_cache(env):
    """Test the setup of the SvgRender builder without an outfilepath and
    with the use_cache flag set."""
    context = env.context
    cache_path = env.cache_path
    target_root = env.target_root

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build without an outfilepath
    svgrender = SvgRender(env=env, context=context, use_cache=True)

    assert svgrender.use_cache
    assert (svgrender.outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.svg')

    # Test the paths for the subbuilders. There is no copy builder.
    assert len(svgrender.subbuilders) == 2

    assert svgrender.subbuilders[0].__class__.__name__ == 'PdfRender'
    assert svgrender.subbuilders[0].use_cache
    assert len(svgrender.subbuilders[0].parameters) == 3
    assert (svgrender.subbuilders[0].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.pdf')

    assert svgrender.subbuilders[1].__class__.__name__ == 'Pdf2SvgCropScale'
    assert svgrender.subbuilders[0].use_cache
    assert (svgrender.subbuilders[1].parameters[0] ==
            svgrender.subbuilders[0].outfilepath)
    assert (svgrender.subbuilders[1].outfilepath ==
            cache_path / 'media' / 'template_b9b44d13de71.svg')

    # 2. Test an example with modification attributes. The final filename should
    #    change.
    svgrender = SvgRender(parameters=[('scale', 2.0)], env=env, context=context,
                          use_cache=True)
    assert svgrender.outfilepath.target_root == cache_path
    assert str(svgrender.outfilepath.subpath) != ('media/template_'
                                                  'b9b44d13de71.svg')
    assert str(svgrender.outfilepath.subpath) == ('media/template_'
                                                  '1b0167b8955c.svg')


def test_svgrender_chain_subbuilders(env):
    """Test the chain_subbuilders method for the SvgRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Setup a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.svg')
    svgrender = SvgRender(env=env, context=context)
    svgrender.outfilepath = outfilepath
    svgrender.chain_subbuilders()

    # Test the paths
    assert (str(svgrender.subbuilders[0].outfilepath.subpath) ==
            'media/template_b9b44d13de71.pdf')
    assert (svgrender.subbuilders[1].parameters[0] ==
            svgrender.subbuilders[0].outfilepath)
    assert (str(svgrender.subbuilders[1].outfilepath.subpath) ==
            'media/template_b9b44d13de71.svg')
    assert (svgrender.subbuilders[2].parameters[0] ==
            svgrender.subbuilders[1].outfilepath)
    assert svgrender.subbuilders[2].outfilepath == outfilepath

    assert any(["My test body" in str(f) for f in svgrender.parameters])
    assert svgrender.outfilepath == outfilepath


def test_svgrender_simple(env):
    """Test a simple build with the SvgRender builder."""
    target_root = env.context['target_root']
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Test a build with an outfilepath
    outfilepath = TargetPath(target_root=target_root,
                             subpath='final.svg')
    svgrender = SvgRender(env=env, context=context, outfilepath=outfilepath)

    # Check the builder status
    assert not outfilepath.exists()
    assert svgrender.status == 'ready'

    # Run the build
    assert svgrender.build(complete=True) == 'done'
    assert svgrender.status == 'done'
    assert outfilepath.exists()

    # A new builder shouldn't need a build
    svgrender = SvgRender(env=env, context=context, outfilepath=outfilepath)
    assert svgrender.status == 'done'

    # 2. Changing the render contents should trigger a new build
    context['body'] = Tag(tex='My new test body')
    svgrender = SvgRender(env=env, context=context, outfilepath=outfilepath)
    assert svgrender.status == 'ready'


def test_svgrender_simple_without_outfilepath(env):
    """Test a simple build with the SvgRender builder without an outfilepath."""
    target_root = env.target_root
    cache_path = env.cache_path
    context = env.context

    # Create a mock tag and template
    Tag = namedtuple("Tag", "tex")
    context['body'] = Tag(tex='My test body')

    # 1. Test a build without an outfilepath. Since we use template.tex, it
    #    will be used for the outfilepath
    svgrender = SvgRender(env=env, context=context)

    assert svgrender.status == 'ready'
    assert svgrender.build(complete=True) == 'done'
    assert (svgrender.outfilepath ==
            target_root / 'media' / 'template_b9b44d13de71.svg')
    assert svgrender.outfilepath.exists()

    # A new build should not be needed
    svgrender = SvgRender(env=env, context=context)
    assert svgrender.status == 'done'

    # 2. Changing the rendered contents changes the outfilepath
    context['body'] = Tag(tex='My new test body')

    svgrender = SvgRender(env=env, context=context)

    assert svgrender.status == 'ready'
    assert svgrender.build(complete=True) == 'done'
    assert (svgrender.outfilepath ==
            target_root / 'media' / 'template_e343d4a49636.svg')
    assert svgrender.outfilepath.exists()

    # A new build should not be needed
    svgrender = SvgRender(env=env, context=context)
    assert svgrender.status == 'done'

    # 4. Adding a document target places files in that subdirectory
    svgrender = SvgRender(env=env, target='html', context=context)

    assert svgrender.status == 'ready'
    assert svgrender.build(complete=True) == 'done'
    assert (svgrender.outfilepath ==
            target_root / 'html' / 'media' / 'template_e343d4a49636.svg')
    assert svgrender.outfilepath.exists()

    # A new build should not be needed
    svgrender = SvgRender(env=env, context=context)
    assert svgrender.status == 'done'
