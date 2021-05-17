"""Tests for the XHtmlBuilder"""
from collections import namedtuple

from disseminate.builders.target_builders.xhtml_builder import XHtmlBuilder
from disseminate.paths import SourcePath, TargetPath


def test_xhtml_builder_setup(env):
    """Test the setup of a HtmlBuilder when 'xhtml' is not listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    cache_path = env.cache_path

    # 1. Setup the builder without an outfilepath. In this case, 'html' is
    #    *not* listed in the targets, so the outfilepath will be in the cache
    #    directory
    context['targets'] -= {'xhtml'}
    target_filepath = TargetPath(target_root=cache_path,
                                 target='xhtml', subpath='test.xhtml')
    builder = XHtmlBuilder(env, context=context)

    # check the build
    # use a cache path but use a media_path
    assert builder.use_cache
    assert not builder.use_media
    assert context['builders']['.xhtml'] == builder  # builder in context
    assert not target_filepath.exists()
    assert builder.outfilepath == target_filepath
    assert len(builder.subbuilders) == 2

    parallel_builder = builder.subbuilders[0]
    assert parallel_builder.__class__.__name__ == 'ParallelBuilder'
    assert parallel_builder.parameters == []
    assert (parallel_builder.subbuilders[0].outfilepath ==
            cache_path / 'xhtml' / 'media' / 'css' / 'epub.css')

    render_builder = builder.subbuilders[1]
    assert render_builder.__class__.__name__ == 'JinjaRender'
    assert len(render_builder.parameters) > 0

    # Check that the correct template was loaded
    assert render_builder.parameters[0].project_root.match('templates/default/'
                                                           'xhtml/')
    assert render_builder.parameters[0].subpath.match('template.xhtml')

    assert builder.parameters == ["build 'XHtmlBuilder'", src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 2. Test an add build
    img_filepath = SourcePath(project_root='tests/builders//examples/ex1',
                              subpath='sample.pdf')
    target_filepath = TargetPath(target_root=env.cache_path,
                                 target='xhtml', subpath='media/sample.svg')
    pdf2svg = builder.add_build(parameters=img_filepath)

    assert pdf2svg.use_cache is True
    assert pdf2svg.parameters == [img_filepath]
    assert pdf2svg.outfilepath == target_filepath


def test_xhtml_builder_simple(env):
    """Test a simple build with the HtmlBuilder"""
    context = env.context
    cache_path = env.cache_path

    # 1. Setup the builder with an outfilepath
    tag = namedtuple('tag', 'xhtml')
    context['body'] = tag(xhtml="My body")  # expects {{ body.html }}

    builder = XHtmlBuilder(env, context=context, use_cache=True)

    # Check the paths
    target_filepath = TargetPath(target_root=cache_path, target='xhtml',
                                 subpath='test.xhtml')

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert builder.outfilepath == target_filepath
    assert not target_filepath.exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert target_filepath.exists()

    # Check the answer key
    assert 'My body' in target_filepath.read_text()

    # Check the copied files
    assert TargetPath(target_root=cache_path, target='xhtml',
                      subpath='media/css/epub.css').exists()

    # New builders don't need to rebuild.
    builder = XHtmlBuilder(env, context=context, use_cache=True)
    assert builder.status == 'done'
