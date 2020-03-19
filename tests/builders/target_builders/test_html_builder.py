"""
Test the HtmlBuilder
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.paths import SourcePath, TargetPath


def test_html_builder_simple(env):
    """Test a simple build with the HtmlBuilder """
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder. At least an outfilepath is needed and a content
    #    is needed
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


def test_html_builder_simple_doc(setup_example):
    """Test a simple build with the HtmlBuilder and a simple document."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')
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
    key = pathlib.Path('tests/builders/target_builders/example1/dummy.html')
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


def test_html_builder_inherited_doc(setup_example):
    """Test a build with the HtmlBuilder using an inherited template and a
    simple doc."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example2',
                             'dummy.dm')
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
    key = pathlib.Path('tests/builders/target_builders/example2/dummy.html')
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


def test_html_builder_add_build(setup_example):
    """Test the HtmlBuilder with an added dependency through add_build."""

    # 1. Example 3 includes a media file that must be converted from pdf->svg
    #    for html
    #    tests/builders/target_builders/example3/
    #     └── src
    #         ├── index.dm
    #         └── media
    #             └── images
    #                 └── NMR
    #                     └── hsqc_bw.pdf
    env, doc = setup_example('tests/builders/target_builders/example3/src',
                             'index.dm')
    target_root = doc.context['target_root']

    # Setup the builder
    html_builder = HtmlBuilder(env, context=doc.context)

    # Add a dependency for the media file
    build = html_builder.add_build(infilepaths='media/images/NMR/hsqc_bw.pdf',
                                   context=doc.context)

    sp = SourcePath(project_root='tests/builders/target_builders/example3/src',
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