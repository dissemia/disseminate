"""
Test the HtmlBuilder
"""
import pathlib

from disseminate.builders.target_builders.html_builder import HtmlBuilder
from disseminate.paths import TargetPath


def test_html_builder_setup(setup_example):
    """Test the setup of the HtmlBuilder"""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    # Setup the builder
    builder = HtmlBuilder(env, document=doc)

    # Check the infilepaths. These should be SourcePaths with correctly set
    # project_root / subpath
    assert len(builder.infilepaths) == 1
    assert builder.infilepaths[0].match('dummy.dm')
    assert (str(builder.infilepaths[0].subpath) ==
            'dummy.dm')
    assert builder.outfilepath.match('html/dummy.html')
    assert str(builder.outfilepath.subpath) == 'dummy.html'


def test_html_builder_simple(setup_example):
    """Test a simple build with the HtmlBuilder."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example1',
                             'dummy.dm')

    # Setup the builder
    builder = HtmlBuilder(env, document=doc)

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
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/pygments.css').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, document=doc)
    assert builder.status == 'done'


def test_html_builder_inherited(setup_example):
    """Test a build with the HtmlBuilder using an inherited template."""
    # 1. example 1: tests/builders/target_builders/example1
    env, doc = setup_example('tests/builders/target_builders/example2',
                             'dummy.dm')

    # Setup the builder
    builder = HtmlBuilder(env, document=doc)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not doc.targets['.html'].exists()

    # Try the build
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'
    assert doc.targets['.html'].exists()
    print(doc.targets['.html'])
    # Check the answer key
    key = pathlib.Path('tests/builders/target_builders/example2/dummy.html')
    assert doc.targets['.html'].read_text() == key.read_text()

    # Check the copied files
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/bootstrap.min.css').exists()
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/base.css').exists()
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/pygments.css').exists()
    assert TargetPath(target_root=doc.target_root, target='html',
                      subpath='media/css/tufte.css').exists()

    # New builders don't need to rebuild.
    builder = HtmlBuilder(env, document=doc)
    assert builder.status == 'done'
