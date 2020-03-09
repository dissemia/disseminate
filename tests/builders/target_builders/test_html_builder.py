"""
Test the HtmlBuilder
"""
import pathlib
from collections import namedtuple

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.paths import TargetPath


def test_html_builder_setup(env):
    """Test the setup of the HtmlBuilder """
    context = env.context
    tmpdir = context['target_root']

    # 1. Setup the builder. At least an outfilepath is needed and a content
    #    is needed
    target_filepath = TargetPath(target_root=tmpdir, subpath='test.html')
    context['body'] = 'My test'

    builder = HtmlBuilder(env, context=context, outfilepath=target_filepath)

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(builder.infilepaths) == 0
    assert builder.outfilepath == target_filepath


def test_html_builder_setup_doc(setup_example):
    """Test the setup of the HtmlBuilder with a Document"""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    # Setup the builder
    builder = HtmlBuilder(env, context=doc.context)

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(builder.infilepaths) == 1
    assert builder.infilepaths[0].match('dummy.dm')
    assert (str(builder.infilepaths[0].subpath) ==
            'dummy.dm')
    assert builder.outfilepath.match('html/dummy.html')
    assert str(builder.outfilepath.subpath) == 'dummy.html'


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
    target_root =doc.context['target_root']

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
