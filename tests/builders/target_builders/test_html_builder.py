"""
Test the HtmlBuilder
"""
import pathlib
from collections import namedtuple
from shutil import copytree

import pytest

from disseminate.builders.exceptions import BuildError
from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.paths import SourcePath, TargetPath


# Setup paths for examples
ex1_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex1'
ex3_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex3'
ex3_srcdir = ex3_root / 'src'
ex4_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex4'
ex5_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex5'
ex8_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex8'


def test_html_builder_setup_html(env):
    """Test the setup of a HtmlBuilder when 'html' is listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath. In this case, 'html' is
    #    listed in the targets, so the outfilepath will *not* be in the cache
    #    directory
    context['targets'] |= {'html'}
    target_filepath = TargetPath(target_root=target_root, target='html',
                                 subpath='test.html')
    builder = HtmlBuilder(env, context=context)

    # check the build
    # don't use a cache path or media_path, use actual target path
    assert not builder.use_cache
    assert not builder.use_media
    assert context['builders']['.html'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].parameters == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].parameters) > 0
    assert builder.parameters == ["build 'HtmlBuilder'", src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 2. Setup the builder with an outfilepath
    target_filepath = TargetPath(target_root=target_root, target='other',
                                 subpath='final.tex')
    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].parameters == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].parameters) > 0
    assert builder.parameters == ["build 'HtmlBuilder'", src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 3. Test an add build
    img_filepath = SourcePath(project_root=ex1_root, subpath='sample.pdf')
    target_filepath = TargetPath(target_root=target_root,
                                 target='html', subpath='media/sample.svg')
    pdf2svg = builder.add_build(parameters=img_filepath)
    assert not pdf2svg.use_cache
    assert pdf2svg.use_media
    assert pdf2svg.parameters == [img_filepath]
    assert pdf2svg.outfilepath == target_filepath


def test_html_builder_setup(env):
    """Test the setup of a HtmlBuilder when 'html' is not listed as a target
    in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = context['target_root']

    # 1. Setup the builder without an outfilepath. In this case, 'html' is *not*
    #    listed in the targets, so the outfilepath will be in the cache
    #    directory
    context['targets'] -= {'html'}
    target_filepath = TargetPath(target_root=target_root / '.cache',
                                 target='html', subpath='test.html')
    builder = HtmlBuilder(env, context=context)

    # check the build
    # use a cache path but use a media_path
    assert builder.use_cache
    assert not builder.use_media
    assert context['builders']['.html'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 2

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].parameters == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].parameters) > 0
    assert builder.parameters == ["build 'HtmlBuilder'", src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 2. Test an add build
    img_filepath = SourcePath(project_root=ex1_root, subpath='sample.pdf')
    target_filepath = TargetPath(target_root=env.cache_path,
                                 target='html', subpath='media/sample.svg')
    pdf2svg = builder.add_build(parameters=img_filepath)

    assert pdf2svg.use_cache is True
    assert pdf2svg.parameters == [img_filepath]
    assert pdf2svg.outfilepath == target_filepath


def test_html_builder_simple(env):
    """Test a simple build with the HtmlBuilder """
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder with an outfilepath
    target_filepath = TargetPath(target_root=tmpdir, target='html',
                                 subpath='test.html')
    tag = namedtuple('tag', 'html')
    context['body'] = tag(html="My body")  # expects {{ body.html }}

    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not target_filepath.exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert target_filepath.exists()

    # Check the answer key
    assert 'My body' in target_filepath.read_text()

    # Check the copied files
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/pygments.css').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)
    assert builder.status == 'done'


def test_html_builder_simple_doc(load_example):
    """Test a simple build with the HtmlBuilder and a simple document."""
    # 1. example 1: tests/builders/examples/example3
    doc = load_example(ex3_srcdir / 'dummy.dm', cp_src=True)
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    builder = HtmlBuilder(env, context=doc.context)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.html'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.html'].exists()

    # Check the answer key
    key = pathlib.Path(ex3_root / 'dummy.html')
    assert doc.targets['.html'].read_text() == key.read_text()

    # Check the copied files
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/pygments.css').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_html_builder_simple_doc_build(load_example):
    """Test a build for a simple document."""
    # 1. example 1: tests/builders/examples/example3
    doc = load_example(ex3_srcdir / 'dummy.dm')
    target_root = doc.context['target_root']

    doc.build()

    # Check the copied and built files
    tgt_filepath = TargetPath(target_root=target_root, target='html',
                              subpath='dummy.html')
    assert tgt_filepath.exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/pygments.css').exists()
    assert ("<p>Here is <strong>my</strong> example file.</p>" in
            tgt_filepath.read_text())


def test_html_builder_inherited(env):
    """Test a build with the HtmlBuilder using an inherited template."""
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder. At least an outfilepath is needed and a content
    #    is needed
    target_filepath = TargetPath(target_root=tmpdir, target='html',
                                 subpath='test.html')
    tag = namedtuple('tag', 'html')
    context['body'] = tag(html="My body")  # expects {{ body.html }}
    context['template'] = 'books/tufte'

    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not target_filepath.exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert target_filepath.exists()

    # Check the answer key
    assert 'My body' in target_filepath.read_text()

    # Check the copied files
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/pygments.css').exists()
    assert TargetPath(target_root=tmpdir, target='html',
                      subpath='media/css/tufte.css').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)
    assert builder.status == 'done'


def test_html_builder_inherited_doc(load_example):
    """Test a build with the HtmlBuilder using an inherited template and a
    simple doc."""
    # 1. example 1: tests/builders/examples/ex4
    doc = load_example(ex4_root / 'dummy.dm', cp_src=True)
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    builder = HtmlBuilder(env, context=doc.context)

    # check the build
    # don't use a cache path or media_path, use actual target path
    assert not builder.use_cache
    assert not builder.use_media
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.html'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.html'].exists()

    # Check the answer key
    key = ex4_root / 'dummy.html'
    print(doc.targets['.html'])
    assert doc.targets['.html'].read_text() == key.read_text()

    # Check the copied files
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/pygments.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/css/tufte.css').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/icons/menu_active.svg').exists()
    assert TargetPath(target_root=target_root, target='html',
                      subpath='media/icons/menu_inactive.svg').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_html_builder_add_build_pdf2svg(load_example, svg_dims):
    """Test the HtmlBuilder with an added dependency through add_build
     (Pdf2SvgCropScale)."""

    # 1. Example 5 includes a media file that must be converted from pdf->svg
    #    for html
    #    tests/builders/examples/ex5/
    #     └── src
    #         ├── index.dm
    #         └── media
    #             └── images
    #                 └── NMR
    #                     └── hsqc_bw.pdf
    doc = load_example(ex5_root / 'src' / 'index.dm')
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    html_builder = HtmlBuilder(env, context=doc.context)

    # Check the builder
    # don't use a cache path or media_path, use actual target path
    assert not html_builder.use_cache
    assert not html_builder.use_media

    # Add a dependency for the media file
    build = html_builder.add_build(parameters='media/images/NMR/hsqc_bw.pdf',
                                   context=doc.context)

    sp = SourcePath(project_root=ex5_root / 'src',
                    subpath='media/images/NMR/hsqc_bw.pdf')
    tp = TargetPath(target_root=target_root, target='html',
                    subpath='media/images/NMR/hsqc_bw.svg')

    # Check the subbuilder
    # don't use a cache path but use media path
    assert not build.use_cache
    assert build.use_media
    assert build.parameters[0] == sp
    assert build.parameters[0].subpath == sp.subpath
    assert build.outfilepath == tp
    assert build.outfilepath.subpath == tp.subpath
    assert build.status == 'ready'
    assert html_builder.status == 'ready'

    # Now run the build
    assert html_builder.build(complete=True) == 'done'
    assert html_builder.status == 'done'
    assert build.status == 'done'

    # Check that the svg file and dimensions
    assert svg_dims(tp, width='227.4', abs=0.3)


def test_html_builder_add_build_pdf2svgcropscale(load_example, svg_dims):
    """Test the HtmlBuilder with an added dependency through add_build
     (Pdf2SvgCropScale)."""

    # 1. Example 5 includes a media file that must be converted from pdf->svg
    #    for html
    #    tests/builders/examples/ex5/
    #     └── src
    #         ├── index.dm
    #         └── media
    #             └── images
    #                 └── NMR
    #                     └── hsqc_bw.pdf
    doc = load_example(ex5_root / 'src' / 'index.dm')
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    html_builder = HtmlBuilder(env, context=doc.context)

    # Add a dependency for the media file (with crop)
    crop_params = ('crop', 0)
    build = html_builder.add_build(parameters=['media/images/NMR/hsqc_bw.pdf',
                                               crop_params],
                                   context=doc.context)

    tp = TargetPath(target_root=target_root, target='html',
                    subpath='media/images/NMR/hsqc_bw.svg')

    # Check the subbuilder
    # don't use a cache path but use media path
    assert build.outfilepath == tp

    # Now run the build
    assert html_builder.build(complete=True) == 'done'
    assert html_builder.status == 'done'
    assert build.status == 'done'

    # Check that the svg file and dimensions
    assert svg_dims(tp, width='134', abs=1.0)

    # Add a dependency for the media file (with scale and crop)
    scale_params = ('scale', 1.2)
    build = html_builder.add_build(parameters=['media/images/NMR/hsqc_bw.pdf',
                                               crop_params,
                                               scale_params],
                                   context=doc.context)

    tp = TargetPath(target_root=target_root, target='html',
                    subpath='media/images/NMR/hsqc_bw.svg')

    # Check the subbuilder
    # don't use a cache path but use media path
    assert build.outfilepath == tp

    # Now run the build
    assert html_builder.build(complete=True) == 'done'
    assert html_builder.status == 'done'
    assert build.status == 'done'

    # Check that the files were created
    assert tp.is_file()
    svg = tp.read_text()

    # Check that the svg file and dimensions
    assert svg_dims(tp, width='200', abs=1)


def test_html_builder_add_build_invalid(load_example):
    """Test the HtmlBuilder with an invalid added dependency through
    add_build."""

    # 1. Example 7 includes a media file that must be converted from pdf->svg
    #    for html
    #    tests/builders/examples/ex8
    #    ├── invalid.pdf
    #    └── main.dm
    doc = load_example(ex8_root / 'main.dm')
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    html_builder = HtmlBuilder(env, context=doc.context)

    # Check the builder
    # don't use a cache path or media_path, use actual target path
    assert not html_builder.use_cache
    assert not html_builder.use_media

    # Add a dependency for the media (invalid) file
    build = html_builder.add_build(parameters='invalid.pdf',
                                   context=doc.context)

    # Check the subbuilder
    assert build.status == 'ready'
    assert html_builder.status == 'ready'

    # Now run the build. It won't work
    with pytest.raises(BuildError):
        html_builder.build(complete=True)

    with pytest.raises(BuildError):
        html_builder.status

    with pytest.raises(BuildError):
        assert build.status

    # Check that the files were not created
    assert not build.outfilepath.exists()
