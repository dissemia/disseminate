"""
Test the HtmlBuilder
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.paths import SourcePath, TargetPath


def test_html_builder_setup_in_targets(env):
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
    assert context['builders']['.html'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 6

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'

    # 2. Setup the builder with an outfilepath
    target_filepath = TargetPath(target_root=target_root, target='other',
                                 subpath='final.tex')
    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)

    # check the build
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 6

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'


def test_html_builder_setup_not_in_targets(env):
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
    assert context['builders']['.html'] == builder  # builder in context
    assert not target_filepath.exists()
    assert len(builder.subbuilders) == 6

    assert builder.subbuilders[0].__class__.__name__ == 'ParallelBuilder'
    assert builder.subbuilders[0].infilepaths == []
    assert builder.subbuilders[1].__class__.__name__ == 'JinjaRender'
    assert len(builder.subbuilders[1].infilepaths) > 0
    assert builder.infilepaths == [src_filepath]
    assert builder.outfilepath == target_filepath

    assert builder.build_needed()
    assert builder.status == 'ready'


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
    doc = load_example('tests/builders/examples/ex3/dummy.dm')
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
    key = pathlib.Path('tests/builders/examples/ex3/dummy.html')
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
    doc = load_example('tests/builders/examples/ex4/dummy.dm')
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
    key = pathlib.Path('tests/builders/examples/ex4/dummy.html')
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

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, context=doc.context)
    assert builder.status == 'done'


def test_html_builder_add_build(load_example):
    """Test the HtmlBuilder with an added dependency through add_build."""

    # 1. Example 3 includes a media file that must be converted from pdf->svg
    #    for html
    #    tests/builders/examples/ex5/
    #     └── src
    #         ├── index.dm
    #         └── media
    #             └── images
    #                 └── NMR
    #                     └── hsqc_bw.pdf
    doc = load_example('tests/builders/examples/ex5/src/index.dm')
    env = doc.context['environment']
    target_root = doc.context['target_root']

    # Setup the builder
    html_builder = HtmlBuilder(env, context=doc.context)

    # Add a dependency for the media file
    build = html_builder.add_build(infilepaths='media/images/NMR/hsqc_bw.pdf',
                                   context=doc.context)

    sp = SourcePath(project_root='tests/builders/examples/ex5/src',
                    subpath='media/images/NMR/hsqc_bw.pdf')
    tp = TargetPath(target_root=target_root, target='html',
                    subpath='media/images/NMR/hsqc_bw.svg')
    assert build.infilepaths[0] == sp
    assert build.infilepaths[0].subpath == sp.subpath
    assert build.outfilepath == tp
    assert build.outfilepath.subpath == tp.subpath

    assert build.status == 'ready'
    assert html_builder.status == 'ready'

    # Now run the build
    assert html_builder.build(complete=True) == 'done'
    assert html_builder.status == 'done'
    assert build.status == 'done'

    # Check that the files were created
    assert tp.is_file()
    assert "<svg xmlns" in tp.read_text()  # make sure it's an svg
