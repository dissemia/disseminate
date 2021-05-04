"""
Tests for Document classes and functions.
"""
from pathlib import Path
import logging

import pytest
from jinja2.exceptions import TemplateNotFound

from disseminate.document import Document
from disseminate.paths import SourcePath, TargetPath
from disseminate.utils.tests import strip_leading_space
from disseminate import settings


# Setup example paths
ex1_root = Path("tests") / "document" / "examples" / "ex1"
ex1_subpath = Path("dummy.dm")
ex2_root = Path("tests") / "document" / "examples" / "ex2"
ex2_subpath_noheader = Path("noheader.dm")
ex2_subpath_withheader = Path("withheader.dm")
ex4_root = Path("tests") / "document" / "examples" / "ex4" / "src"
ex4_subpath = Path("file.dm")
ex5_root = Path("tests") / "document" / "examples" / "ex5"
ex5_subpath = Path("index.dm")
ex10_root = Path("tests") / "document" / "examples" / "ex10" / "src"
ex10_subpath = Path("index.dm")
ex11_root = Path("tests") / "document" / "examples" / "ex11" / "src"
ex11_subpath = Path("root.file.dm")


# Tests for document methods

def test_document_paths(doc):
    """Tests the setting of paths for documents."""

    # Create a test source file
    project_root = doc.project_root
    target_root = doc.target_root

    src_filepath = doc.src_filepath
    src_filepath.write_text("""
    ---
    targets: html
    ---
    """)

    # Reload the test document
    doc.load()

    # Test the paths
    assert isinstance(doc.src_filepath, SourcePath)
    assert doc.src_filepath.project_root == project_root
    assert isinstance(doc.project_root, SourcePath)
    assert isinstance(doc.target_root, TargetPath)
    assert doc.target_root == target_root


def test_document_src_filepaths(load_example):
    """Test the src_filepaths of documents to see if they're correctly loaded
    and parsed into SourcePaths with a project_root and subpath."""
    # 1. Example1 does not have markup source files in a src
    #    directory.
    doc = load_example(ex1_root / ex1_subpath)

    assert isinstance(doc.src_filepath, SourcePath)
    assert doc.src_filepath == ex1_root / ex1_subpath
    assert doc.src_filepath.project_root == ex1_root
    assert doc.src_filepath.subpath == ex1_subpath

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = load_example(ex4_root / ex4_subpath)

    assert doc.src_filepath == ex4_root / ex4_subpath
    assert doc.src_filepath.project_root == ex4_root
    assert doc.src_filepath.subpath == ex4_subpath

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = load_example(ex5_root / ex5_subpath)

    assert isinstance(doc.src_filepath, SourcePath)
    assert doc.src_filepath == ex5_root / ex5_subpath
    assert doc.src_filepath.project_root == ex5_root
    assert doc.src_filepath.subpath == ex5_subpath

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]

    assert isinstance(subdoc.src_filepath, SourcePath)
    assert subdoc.src_filepath == ex5_root / "sub1" / "index.dm"
    assert subdoc.src_filepath.project_root == ex5_root
    assert subdoc.src_filepath.subpath == Path("sub1") / "index.dm"

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert subdoc.src_filepath == ex5_root / "sub2" / "index.dm"
    assert subdoc.src_filepath.project_root == ex5_root
    assert subdoc.src_filepath.subpath == Path("sub2") / "index.dm"

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert subdoc.src_filepath == ex5_root / "sub3" / "index.dm"
    assert subdoc.src_filepath.project_root == ex5_root
    assert subdoc.src_filepath.subpath == Path("sub3") / "index.dm"


def test_document_targets(doc):
    """Test the document targets method."""
    env = doc.context['environment']
    target_root = doc.target_root
    cache_path = env.cache_path

    # 1. Try an example with an 'html' target
    doc.src_filepath.write_text("""
    ---
    targets: html
    ---
    Test1
    """)
    doc.load()

    targets = doc.targets
    assert targets.keys() == {'.html'}

    assert '.html' in targets
    assert isinstance(targets['.html'], TargetPath)
    assert targets['.html'] == target_root / 'html' / 'test.html'

    # 2. Try an example with a cached target
    doc.src_filepath.write_text("""
    ---
    targets: pdf
    ---
    Test1
    """)
    doc.load()

    targets = doc.targets
    assert targets.keys() == {'.tex', '.pdf'}

    assert '.tex' in targets  # located in the cache directory
    assert isinstance(targets['.tex'], TargetPath)
    assert targets['.tex'] == cache_path / 'tex' / 'test.tex'

    assert '.pdf' in targets
    assert isinstance(targets['.pdf'], TargetPath)
    assert targets['.pdf'] == target_root / 'pdf' / 'test.pdf'


def test_document_target_filepath(load_example):
    """Test the target_filepath method."""

    # 1. Example1 does not have markup source files in a source
    #    directory. Target files will be saved in the project directory
    doc = load_example(ex1_root / ex1_subpath)
    target_root = doc.target_root

    assert isinstance(doc.target_filepath('.html'), TargetPath)
    assert doc.target_filepath('.html').target_root == target_root
    assert doc.target_filepath('.html').target == Path("html")
    assert doc.target_filepath('.html').subpath == Path("dummy.html")

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = load_example(ex4_root / ex4_subpath)
    target_root = doc.target_root

    assert doc.target_filepath('.html').target_root == target_root
    assert doc.target_filepath('.html').target == Path("html")
    assert doc.target_filepath('.html').subpath == Path("file.html")

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = load_example(ex5_root / ex5_subpath)
    target_root = doc.target_root

    assert doc.target_filepath('.html').target_root == target_root
    assert doc.target_filepath('.html').target == Path("html")
    assert doc.target_filepath('.html').subpath == Path("index.html")

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert subdoc.target_root == target_root
    assert subdoc.target_filepath('.html').target_root == target_root
    assert subdoc.target_filepath('.html').target == Path("html")
    assert (subdoc.target_filepath('.html').subpath ==
            Path("sub1") / "index.html")

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.target_root, TargetPath)
    assert subdoc.target_root == target_root
    assert subdoc.target_filepath('.html').target_root == target_root
    assert subdoc.target_filepath('.html').target == Path("html")
    assert (subdoc.target_filepath('.html').subpath ==
            Path("sub2") / "index.html")

    subdoc = list(subdoc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert subdoc.target_root == target_root
    assert subdoc.target_filepath('.html').target_root == target_root
    assert subdoc.target_filepath('.html').target == Path("html")
    assert (subdoc.target_filepath('.html').subpath ==
            Path("sub2") / "subsub2" / "index.html")

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.target_root, TargetPath)
    assert subdoc.target_root == target_root
    assert subdoc.target_filepath('.html').target_root == target_root
    assert subdoc.target_filepath('.html').target == Path("html")
    assert (subdoc.target_filepath('.html').subpath ==
            Path("sub3") / "index.html")


def test_document_load_required(doctree, wait, caplog):
    """Tests the load_required method for documents."""
    # Capture DEBUG logging messages
    caplog.set_level(logging.DEBUG)
    caplog.clear()

    # Setup the documents in the doctree. The setup has 3 load_required messages
    doc = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True,
                                        recursive=True)

    # Check that the doc was succesfully loaded
    assert not doc.load_required()

    # 1. Test load required when not successfully loaded
    doc._succesfully_loaded = False
    assert doc.load_required()  # 1 load required logging message
    assert len(caplog.record_tuples) == 1  # only 1 DEBUG message
    assert ("The document was not previously loaded successfully" in
            caplog.record_tuples[-1][2])

    doc._succesfully_loaded = True
    assert not doc.load_required()  # 1 load_required logging messages

    # 2. Test load required when body attribute hasn't been set
    del doc.context[settings.body_attr]
    assert doc.load_required()  # 1 load_required logging messages
    assert len(caplog.record_tuples) == 2
    assert "tag has not been loaded yet" in caplog.record_tuples[-1][2]

    # 1 load_required message for each document, 1 "add target builder" message
    # for each document
    assert doc.load() is True  # documents were loaded
    assert len(caplog.record_tuples) == 6
    assert not doc.load_required()

    # 3. Test load required when the source file is newer than the mtime in
    #    the context
    wait()  # sleep time offset needed for different mtimes
    doc.src_filepath.touch()
    assert doc.load_required()  # 1 load required message
    assert len(caplog.record_tuples) == 7
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-1][2])

    # 3 load_required messages and 3 add target builder messages. The parent
    # (test1.dm) is reloaded so the children (test2.dm, test3.dm) are reloaded
    # because it has a later mtime.
    assert doc.load() is True  # documents were loaded

    assert len(caplog.record_tuples) == 13
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-6][2])  # test1.dm
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-5][2])  # test2.dm
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-4][2])  # test3.dm
    assert not doc.load_required()

    # 4. Test load required when the parent context's mtime is newer than the
    #    mtime in the context
    doc.context.parent_context['mtime'] = doc.context['mtime'] + 1.0
    assert doc.load_required()  # 1 load_required message
    assert len(caplog.record_tuples) == 14
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-1][2])

    del doc.context.parent_context['mtime']
    assert not doc.load_required()

    # 5. Test load required when the parent context' mtime is newer than the
    #    context mtime for subdocuments
    assert not doc2.load_required()
    assert not doc3.load_required()
    assert len(caplog.record_tuples) == 14  # same number of messages as before.

    # 6. Touch a subdocument, and it should be the only one that requires an
    #    update
    wait()  # sleep time offset needed for different mtimes
    doc2.src_filepath.touch()
    assert not doc.load_required()
    assert doc2.load_required()  # 1 load_required message
    assert not doc3.load_required()
    assert len(caplog.record_tuples) == 15
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-1][2])

    # 7. Touch the root document, and all 3 documents should need an update
    wait()  # sleep time offset needed for different mtimes
    doc.src_filepath.touch()

    # 3 load required messages, 3 target build added messages
    assert doc.load() is True  # documents were loaded
    assert len(caplog.record_tuples) == 21
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-6][2])
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-5][2])
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-4][2])


def test_document_update_mtime(doctree):
    """Test the _update_mtime method."""

    # Find the maximum mtime for all documents
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(recursive=False, only_subdocuments=True)
    mtime = max((doc1.mtime, doc2.mtime, doc3.mtime))

    # Increase the mtime and check that all documents are updated
    mtime += 10.0
    Document._update_mtime(doc1, mtime=mtime)

    assert all([doc.mtime == mtime for doc in (doc1, doc2, doc3)])


# Tests for other functionality

def test_document_target_list_update(doc):
    """Tests the proper updating of the target list."""
    markup = """---
    targets: html
    ---
    """
    doc.src_filepath.write_text(strip_leading_space(markup))
    doc.load()

    assert doc.targets.keys() == {'.html'}

    # Update the header
    markup = """---
    targets: tex
    ---
    """
    doc.src_filepath.write_text(strip_leading_space(markup))
    doc.load()

    assert doc.targets.keys() == {'.tex'}


def test_document_context_update(load_example):
    """Tests that the context is properly updated in subsequent renders."""
    # First load a file with a header
    doc = load_example(ex2_root / ex2_subpath_withheader)

    # Check the contents of the context.
    # The title entry is converted to a tag.
    assert 'title' in doc.context
    assert doc.context['title'] == 'My first title'

    # The author entry is converted to a tag.
    assert 'author' in doc.context
    assert doc.context['author'] == 'Justin L Lorieau'

    # The target 'tex' is specified. It should not match the default setting,
    # for the later test.
    assert 'targets' in doc.context
    assert doc.context['targets'] != settings.default_context['targets']
    assert doc.context['targets'] == {'html', 'tex'}
    assert doc.context.targets == {'.html', '.tex'}

    assert '@macro' in doc.context

    # Get the local_context id to make sure it stays the same
    context_id = id(doc.context)

    # Now switch to a file without a header and make sure the header values
    # are removed
    doc.src_filepath = SourcePath(project_root=ex2_root,
                                  subpath=ex2_subpath_noheader)
    doc.load(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.context
    assert 'author' not in doc.context
    assert 'macro' not in doc.context

    # The 'targets' entry should revert to the default
    assert doc.context['targets'] == settings.default_context['targets']

    assert id(doc.context) == context_id


def test_document_macros(load_example):
    """Tests that macros defined in the header of a document are properly
    processed."""

    # First load a file with a header
    doc = load_example(ex2_root / ex2_subpath_withheader)

    # Build the document for the html and tex  targets
    assert doc.build() == 'done'
    # See if the macro was properly replaced
    html_filepath = doc.targets['.html']
    rendered_html = html_filepath.read_text()
    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


def test_document_load_on_render(doc):
    """Test the proper loading of an updated source file on render."""

    # The initial document has the targets listed in the example document
    # created from the 'doc' fixture (conftest.py)
    assert doc.targets.keys() == {'.html', '.tex', '.pdf', '.xhtml'}

    # Change the source file, and run the render function. The targets should
    # be updated to the new values in the updated header.
    src = """
    ---
    targets: html, tex
    ---
    """
    doc.src_filepath.write_text(src)

    # Build the document for the html, tex and pdf targets
    assert doc.build() == 'done'
    assert doc.targets.keys() == {'.html', '.tex'}


def test_document_recursion(env_cls, tmpdir):
    """Test the loading of a document with itself as the subdocument
    (recursion)."""

    # 1. Create a test document that references itself
    src_filepath1 = SourcePath(project_root=tmpdir, subpath='test1.dm')
    target_root = TargetPath(target_root=tmpdir)

    src_filepath1.write_text("""
    ---
    include: test1.dm
    ---
    @chapter{one}
    """)

    env = env_cls(src_filepath1, target_root=tmpdir)
    doc = env.root_document

    # The document should not have itself as a subdocument
    assert len(doc.subdocuments) == 0

    # 2. Create 2 test documents that reference each other
    src_filepath1 = SourcePath(project_root=tmpdir, subpath='test-a.dm')
    src_filepath2 = SourcePath(project_root=tmpdir, subpath='test-b.dm')

    src_filepath1.write_text("""
    ---
    include: test-b.dm
    ---
    @chapter{one}
    """)
    src_filepath2.write_text("""
    ---
    include: test-a.dm
    ---
    @chapter{one}
    """)
    env1 = env_cls(src_filepath1, target_root=tmpdir)
    doc1 = env1.root_document
    env2 = env_cls(src_filepath2, target_root=tmpdir)
    doc2 = env2.root_document

    # The document should not have itself as a subdocument, but it can have
    # the other as a root document.
    assert len(doc1.subdocuments) == 1  # test-b as subdoc
    assert len(doc2.subdocuments) == 1  # test-a as subdoc


def test_document_render_missing_template(doc):
    """Tests the rendering of a document when a specified templates is
    missing."""

    # 1. Prepare the document with a missing template
    src = ("---\n"
           "targets: html, tex, pdf\n"
           "template: missing\n"
           "---\n"
           "test\n")
    doc.src_filepath.write_text(src)

    # Raises a template not found error
    with pytest.raises(TemplateNotFound):
        doc.load()


def test_document_unusual_filenames(load_example):
    """Test the rendering of projects that use unusual filenames."""

    # Test example 11. Example 11 has unusual filenames that need to be loaded
    #
    # tests/document/examples/ex11
    # └── src
    #     ├── ch1.1
    #     │   ├── ch1.1.dm
    #     │   └── ?\215ísla
    #     │       ├── fig1.1.1.png
    #     │       └── img.one.asy
    #     └── root.file.dm
    doc = load_example(ex11_root / ex11_subpath)
    target_root = doc.target_root
    html_root = target_root / 'html'
    tex_root = target_root / 'tex'
    pdf_root = target_root / 'pdf'

    # Build the document for the html, tex and pdf targets
    assert doc.build() == 'done'

    subdocs = doc.documents_list(only_subdocuments=True)
    assert len(subdocs) == 1

    # Check that the src_filepaths are correctly set
    assert doc.src_filepath == ex11_root / ex11_subpath
    assert subdocs[0].src_filepath == ex11_root / 'ch1.1' / 'ch1.1.dm'

    # Check the creation of dependencies (html)
    html_key = {html_root / 'ch1.1',  # dirs
                html_root / 'media',
                html_root / 'media' / 'ch1.1',
                html_root / 'media' / 'ch1.1' / 'čísla',
                html_root / 'media' / 'css',
                html_root / 'media' / 'icons',

                html_root / 'root.file.html',  # files
                html_root / 'ch1.1' / 'ch1.1.html',
                html_root / 'media' / 'ch1.1' / 'čísla' / 'fig1.1.1.png',
                html_root / 'media' / 'ch1.1' / 'čísla' / 'img.one.svg',
                html_root / 'media' / 'css' / 'base.css',
                html_root / 'media' / 'css' / 'bootstrap.min.css',
                html_root / 'media' / 'css' / 'default.css',
                html_root / 'media' / 'css' / 'pygments.css',
                html_root / 'media' / 'icons' / 'menu_inactive.svg',
                html_root / 'media' / 'icons' / 'menu_active.svg',
                html_root / 'media' / 'icons' / 'dm_icon.svg',
                html_root / 'media' / 'icons' / 'txt_icon.svg',
                html_root / 'media' / 'icons' / 'tex_icon.svg',
                html_root / 'media' / 'icons' / 'pdf_icon.svg',
                html_root / 'media' / 'icons' / 'epub_icon.svg',
                }

    html_actual = set(html_root.glob('**/*'))
    assert html_key == html_actual

    tex_key = {tex_root / 'ch1.1',  # dirs
               tex_root / 'media',
               tex_root / 'media' / 'ch1.1',
               tex_root / 'media' / 'ch1.1' / 'čísla',

               tex_root / 'root.file.tex',  # files
               tex_root / 'ch1.1' / 'ch1.1.tex',
               tex_root / 'media' / 'ch1.1' / 'čísla' / 'fig1.1.1.png',
               tex_root / 'media' / 'ch1.1' / 'čísla' / 'img.one.pdf',
               }
    tex_actual = set(tex_root.glob('**/*'))
    assert tex_key == tex_actual

    pdf_key = {pdf_root / 'ch1.1',  # dirs

               pdf_root / 'root.file.pdf',  # files
               pdf_root / 'ch1.1' / 'ch1.1.pdf',
               }
    pdf_actual = set(pdf_root.glob('**/*'))
    assert pdf_key == pdf_actual


def test_document_multiple_dependency_locations(load_example):
    """Test the addition of dependencies from multiple locations."""

    # 1. Test example10, which has an image file local to a sub-directory, one
    #    in the root directory and template files
    # tests/document/example10
    # └── src
    #     ├── chapter1
    #     │   ├── figures
    #     │   │   └── local_img.png
    #     │   └── index.dm
    #     ├── index.dm
    #     └── media
    #         └── ch1
    #             └── root_img.png
    # Load the root document and subdocument
    doc = load_example(ex10_root / ex10_subpath)
    target_root = doc.target_root
    subdoc = doc.documents_list(only_subdocuments=True)[0]

    # Build the document for the html, tex and pdf targets
    assert doc.build() == 'done'

    # Check the creation of dependencies (html)
    html_root = target_root / 'html'
    html_key = {html_root / 'chapter1',  # dirs
                html_root / 'media',
                html_root / 'media' / 'css',
                html_root / 'media' / 'icons',
                html_root / 'media' / 'ch1',
                html_root / 'media' / 'chapter1',
                html_root / 'media' / 'chapter1' / 'figures',

                html_root / 'index.html',  # files
                html_root / 'chapter1' / 'index.html',
                html_root / 'media' / 'ch1' / 'root_img.png',
                html_root / 'media' / 'chapter1' / 'figures' / 'local_img.png',
                html_root / 'media' / 'css' / 'base.css',
                html_root / 'media' / 'css' / 'bootstrap.min.css',
                html_root / 'media' / 'css' / 'default.css',
                html_root / 'media' / 'css' / 'pygments.css',
                html_root / 'media' / 'icons' / 'menu_active.svg',
                html_root / 'media' / 'icons' / 'menu_inactive.svg',
                html_root / 'media' / 'icons' / 'dm_icon.svg',
                html_root / 'media' / 'icons' / 'txt_icon.svg',
                html_root / 'media' / 'icons' / 'tex_icon.svg',
                html_root / 'media' / 'icons' / 'pdf_icon.svg',
                html_root / 'media' / 'icons' / 'epub_icon.svg',
                }
    html_actual = set(html_root.glob('**/*'))
    assert html_actual == html_key

    tex_root = target_root / 'tex'
    tex_key = {tex_root / 'chapter1',  # dirs
               tex_root / 'media',
               tex_root / 'media' / 'ch1',
               tex_root / 'media' / 'chapter1',
               tex_root / 'media' / 'chapter1' / 'figures',

               tex_root / 'index.tex',  # files
               tex_root / 'chapter1' / 'index.tex',
               tex_root / 'media' / 'ch1' / 'root_img.png',
               tex_root / 'media' / 'chapter1' / 'figures' / 'local_img.png',
               }
    tex_actual = set(tex_root.glob('**/*'))
    assert tex_actual == tex_key

    pdf_root = target_root / 'pdf'
    pdf_key = {pdf_root / 'chapter1',  # dirs

               pdf_root / 'index.pdf',  # files
               pdf_root / 'chapter1' / 'index.pdf'}
    pdf_actual = set(pdf_root.glob('**/*'))
    assert pdf_actual == pdf_key
