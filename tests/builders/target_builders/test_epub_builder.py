"""
Test the EpubBuilder
"""
from collections import namedtuple
import pathlib

import epubcheck

from disseminate.builders.target_builders import EpubBuilder
from disseminate.paths import TargetPath

# Paths for examples
ex3_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex3'
ex6_root = pathlib.Path('tests') / 'builders' / 'examples' / 'ex6'


def test_epub_builder_find_or_create_xhtml_builders(doctree):
    """Test the find_or_create_xhtml_builders EpubBuilder method."""
    # Setup variables
    context = doctree.context
    env = context['environment']
    cache_path = env.cache_path
    doc1, doc2, doc3 = doctree.documents_list(only_subdocuments=False,
                                              recursive=True)

    # Create an EpubBuilder
    epub_builder = EpubBuilder(env=env, context=context)

    # There should be 3 xhtml_builders created for the 3 documents
    xhtml_builders = epub_builder.find_or_create_xhtml_builders()
    assert len(xhtml_builders) == 3

    # Make sure the contexts were correctly set to their respective documents
    for xhtml_builder, doc in zip(xhtml_builders, [doc1, doc2, doc3]):
        assert id(xhtml_builder.context) == id(doc.context)

    # Make sure the outfilepaths are correctly set
    assert xhtml_builders[0].outfilepath == cache_path / 'xhtml' / 'test.xhtml'
    assert xhtml_builders[1].outfilepath == cache_path / 'xhtml' / 'test2.xhtml'
    assert xhtml_builders[2].outfilepath == cache_path / 'xhtml' / 'test3.xhtml'

    # Retrieving the xhtml_builders again returns the same objects
    new_xhtml_builders = epub_builder.find_or_create_xhtml_builders()
    for builder1, builder2 in zip(xhtml_builders, new_xhtml_builders):
        assert id(builder1) == id(builder2)


def test_epub_builder_xhtml_filepaths(doctree):
    """Test the xhtml_filepaths EpubBuilder method."""
    # Setup variables
    context = doctree.context
    env = context['environment']
    cache_path = env.cache_path

    # Create an EpubBuilder
    epub_builder = EpubBuilder(env=env, context=context)

    # There should be 3 xhtml_filepaths created for the 3 documents
    xhtml_filepaths = epub_builder.xhtml_filepaths()
    assert len(xhtml_filepaths) == 4

    assert xhtml_filepaths[0] == cache_path / 'xhtml' / 'test.xhtml'
    assert xhtml_filepaths[1] == cache_path / 'xhtml' / 'test2.xhtml'
    assert xhtml_filepaths[2] == cache_path / 'xhtml' / 'test3.xhtml'
    assert (xhtml_filepaths[3] == cache_path / 'xhtml' /
            'media' / 'css' / 'epub.css')


def test_epub_builder_create_toc_xhtml_builder(doctree):
    """Test the create_toc_xhtml_builder EpubBuilder method"""
    # Setup variables
    context = doctree.context
    env = context['environment']
    cache_path = env.cache_path

    # Create an EpubBuilder
    epub_builder = EpubBuilder(env=env, context=context)

    # There aren't toc.xhtml files in the doctree
    assert not epub_builder.has_toc_xhtml()

    # Try creating an XHtmlBuilder for the toc
    xhtml_builder = epub_builder.create_toc_xhtml_builder()

    # Check this builder and its build
    assert xhtml_builder.outfilepath == cache_path / 'xhtml' / 'toc.xhtml'
    assert xhtml_builder.build(complete=True) == 'done'

    # Check the contents of the toc.xhtml
    xhtml = xhtml_builder.outfilepath.read_text()
    assert "test.xhtml" in xhtml
    assert "test2.xhtml" in xhtml
    assert "test3.xhtml" in xhtml


def test_epub_builder_setup_epub_in_targets(env):
    """Test the setup of a PdfBuilder when 'epub' (but not 'xhtml') is listed as
    a target in the context['targets']"""
    context = env.context
    src_filepath = context['src_filepath']
    target_root = env.target_root
    cache_path = env.cache_path

    # 1. Setup the builder without an outfilepath.  In this case, 'tex' is not
    #    listed in the targets but 'pdf' is, so the outfilepath will *not*
    #    be in the cache directory
    context['targets'] -= {'xhtml'}
    context['targets'] |= {'epub'}
    context['builders'].clear()  # Reset the builders

    target_cache_epub_filepath = TargetPath(target_root=target_root / '.cache',
                                           target='epub', subpath='test.epub')
    target_epub_filepath = TargetPath(target_root=target_root,
                                     target='epub', subpath='test.epub')
    builder = EpubBuilder(env, context=context)

    # check the build
    assert context['builders']['.epub'] == builder  # builder in context
    assert not target_epub_filepath.exists()

    # Create the subbuilders. This needs to be done after the docs are loaded,
    # which is why it these aren't created on instantiation of the builder
    builder.create_subbuilders()
    assert len(builder.subbuilders) == 4

    # Check the subbuilders

    # 1. Check the builders for the xhtml file for the root document
    xhtml_builder1 = builder.subbuilders[0]
    assert xhtml_builder1.__class__.__name__ == 'XHtmlBuilder'
    assert xhtml_builder1.use_cache
    assert xhtml_builder1.target == 'xhtml'
    assert xhtml_builder1.outfilepath == cache_path / 'xhtml' / 'test.xhtml'

    # 2. Check the toc_xhtml builder
    xhtml_builder2 = builder.subbuilders[1]
    assert xhtml_builder2.__class__.__name__ == 'JinjaRender'
    assert xhtml_builder2.use_cache
    assert xhtml_builder2.target == 'xhtml'
    assert xhtml_builder2.outfilepath == cache_path / 'xhtml' / 'toc.xhtml'

    # 3. Check the xhtml2epub builder
    epub_builder = builder.subbuilders[2]
    assert epub_builder.__class__.__name__ == 'XHtml2Epub'
    assert epub_builder.use_cache
    assert epub_builder.target == 'epub'
    assert epub_builder.outfilepath == cache_path / 'epub' / 'test.epub'

    # 4. Check the copy builder
    cp_builder = builder.subbuilders[3]
    assert cp_builder.__class__.__name__ == 'Copy'
    assert not cp_builder.use_cache
    assert cp_builder.target == 'epub'
    assert cp_builder.outfilepath == target_root / 'epub' / 'test.epub'

    # Check the EpubBuilder
    assert builder.parameters == ["build 'EpubBuilder'", src_filepath]
    assert builder.outfilepath == target_root / 'epub' / 'test.epub'

    assert builder.build_needed()
    assert builder.status == 'ready'


def test_epub_builder_simple1(env):
    """Test a simple build with the EpubBuilder with epub target"""
    context = env.context
    target_root = env.target_root
    cache_path = env.cache_path

    # Setup the document with a heading
    doc = env.root_document
    doc.src_filepath.write_text("""
    ---
    targets: epub
    ---
    @chapter{Chapter One}
    """)

    # Setup the builders
    context['targets'] |= {'epub'}
    context['targets'] -= {'xhtml'}
    context['builders'].clear()  # Reset the builders

    # Setup the paths
    epub_filepath = TargetPath(target_root=target_root, target='epub',
                               subpath='test.epub')
    xhtml_filepath = TargetPath(target_root=cache_path, target='xhtml',
                                subpath='test.xhtml')

    # 1. Setup the builder without an outfilepath
    tag = namedtuple('tag', 'xhtml')
    context['body'] = tag(xhtml="My body")  # expects {{ body.tex }}

    builder = EpubBuilder(env, context=context)

    # check the build
    assert builder.build_needed()
    assert builder.status == 'ready'
    assert not epub_filepath.exists()
    assert not xhtml_filepath.exists()

    # Try the build
    builder.build(complete=True)
    assert builder.build(complete=True) == 'done'
    assert builder.status == 'done'

    # Check to make sure the target directory has the final file and nothing
    # else
    assert epub_filepath.exists()
    assert xhtml_filepath.exists()
    assert len(list(epub_filepath.parent.glob('*'))) == 1  # only test.epub

    # Check the epub file
    assert epubcheck.validate(epub_filepath)

    # New builders don't need to rebuild.
    builder = EpubBuilder(env, context=context)
    assert builder.status == 'done'


def test_epub_builder_simple_doc_build(load_example):
    """Test a build of a simple document with the EPubBuilder."""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example(ex3_root / 'dummy.dm')
    target_root = doc.target_root

    doc.build()

    # Check the copied and built files
    tgt_filepath = TargetPath(target_root=target_root, target='epub',
                              subpath='dummy.epub')
    assert tgt_filepath.exists()
    assert len(list(tgt_filepath.parent.glob('*'))) == 1  # only test.epub

    # Check that the file is a valid epub
    assert epubcheck.validate(tgt_filepath)


def test_epub_builder_doctree_build(load_example):
    """Test a build of a document tree with the EPubBuilder."""
    # 1. example 1: tests/builders/examples/ex3
    doc = load_example(ex6_root / 'index.dm')
    target_root = doc.target_root

    assert doc.build() == 'done'

    # Check the copied and built files
    tgt_filepath = TargetPath(target_root=target_root, target='epub',
                              subpath='index.epub')
    assert tgt_filepath.exists()
    assert len(list(tgt_filepath.parent.glob('*'))) == 1  # only test.epub

    # Check that the file is a valid epub
    assert epubcheck.validate(tgt_filepath)

