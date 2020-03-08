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


#
#
# def test_html_builder_simple(env):
#     """Test simple builds with the HtmlBuilder"""
#     assert False
#
#
# def test_html_builder_paths(env):
#     """Test builds with different paths for infilepaths"""
#
#     # Create an html builder
#     html_builder = HtmlBuilder(env)
#
#     # Add build
#     html_builder.add_build(infilepath='', outfilepath='', context=context)
#
#
# def test_html_builder_document(env):
#     """Test access to the HtmlBuilder from the document context"""
#     context = env.context
#     env = context['environment']
#
#     # Get the HtmlBuilder
#     html_builder = env.get_target_builder('.html')
#
#     # Load document, check if build is needed
#
#     # Add builds (Tags)
#     environment = context['environment']
#     html_builder = environment.get_builder(document_target='.html',
#                                            context=context)
#     html_builder.add_build(infilepaths='', outfilepath='')
#
#     # Write html file (document)
