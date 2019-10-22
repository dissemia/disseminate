"""
Tests for Document classes and functions.
"""
import pathlib
from shutil import copy
import logging

import pytest
from jinja2.exceptions import TemplateNotFound

from disseminate.document import Document, exceptions
from disseminate.paths import SourcePath, TargetPath
from disseminate.utils.tests import strip_leading_space
from disseminate import settings


# Tests for document methods

def test_document_paths(tmpdir):
    """Tests the setting of paths for documents."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a test source file
    src_path = tmpdir / 'src'
    src_path.mkdir()
    src_filepath = src_path / 'file1.dm'
    src_filepath.write_text("""
    ---
    targets: html
    ---
    """)

    # Create the test document
    doc = Document(src_filepath, tmpdir)

    # Test the paths
    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == str(src_filepath)
    assert str(doc.src_filepath.project_root) == str(src_path)

    assert isinstance(doc.project_root, SourcePath)
    assert str(doc.project_root) == str(src_path)

    assert isinstance(doc.target_root, TargetPath)
    assert str(doc.target_root) == str(tmpdir)
    assert str(doc.target_root.target_root) == str(tmpdir)


def test_document_src_filepaths():
    """Test the src_filepaths of documents."""
    # 1. Example1 does not have markup source files in a src
    #    directory.
    doc = Document("tests/document/example1/dummy.dm")

    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == "tests/document/example1/dummy.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example1"
    assert str(doc.src_filepath.subpath) == "dummy.dm"

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert str(doc.src_filepath) == "tests/document/example4/src/file.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example4/src"
    assert str(doc.src_filepath.subpath) == "file.dm"

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")

    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == "tests/document/example5/index.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example5"
    assert str(doc.src_filepath.subpath) == "index.dm"

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]

    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub1/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub1/index.dm"

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub2/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub2/index.dm"

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub3/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub3/index.dm"


def test_document_targets():
    """Test the document targets method."""
    doc = Document("tests/document/example1/dummy.dm")

    # dummy.dm has the entry 'html, tex' set in the header.
    targets = doc.targets

    assert targets.keys() == {'.html', '.tex'}

    assert '.html' in targets
    assert isinstance(targets['.html'], TargetPath)
    assert str(targets['.html']) == 'tests/document/example1/html/dummy.html'
    assert str(targets['.html'].target_root) == 'tests/document/example1'
    assert str(targets['.html'].target) == 'html'
    assert str(targets['.html'].subpath) == 'dummy.html'

    assert '.tex' in targets
    assert str(targets['.tex']) == 'tests/document/example1/tex/dummy.tex'
    assert str(targets['.tex'].target_root) == 'tests/document/example1'
    assert str(targets['.tex'].target) == 'tex'
    assert str(targets['.tex'].subpath) == 'dummy.tex'

    # Test changing the targets from the context
    doc.context['targets'] = set()
    assert doc.targets.keys() == set()


def test_document_target_filepath():
    """Test the target_filepath method."""

    # 1. Example1 does not have markup source files in a source
    #    directory. Target files will be saved in the project directory
    doc = Document("tests/document/example1/dummy.dm")

    assert isinstance(doc.target_filepath('.html'), TargetPath)
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example1/html/dummy.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example1")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "dummy.html")

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example4/html/file.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example4")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "file.html")

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example5/html/index.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "index.html")

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub1/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub1/index.html")

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub2/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub2/index.html")

    subdoc = list(subdoc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub2/subsub2/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub2/subsub2/index.html")

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub3/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub3/index.html")


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

    # 1 load_required message
    assert doc.load() is True  # documents were loaded
    assert len(caplog.record_tuples) == 3
    assert not doc.load_required()

    # 3. Test load required when the source file is newer than the mtime in
    #    the context
    wait()  # sleep time offset needed for different mtimes
    doc.src_filepath.touch()
    assert doc.load_required()  # 1 load required message
    assert len(caplog.record_tuples) == 4
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-1][2])

    # 3 load_required messages. The parent (test1.dm) is reloaded so the
    # children (test2.dm, test3.dm) are reloaded because it has a later mtime.
    assert doc.load() is True  # documents were loaded

    assert len(caplog.record_tuples) == 7
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-3][2])  # test1.dm
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-2][2])  # test2.dm
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-1][2])  # test3.dm
    assert not doc.load_required()

    # 4. Test load required when the parent context's mtime is newer than the
    #    mtime in the context
    doc.context.parent_context['mtime'] = doc.context['mtime'] + 1.0
    assert doc.load_required()  # 1 load_required message
    assert len(caplog.record_tuples) == 8
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-1][2])

    del doc.context.parent_context['mtime']
    assert not doc.load_required()

    # 5. Test load required when the parent context' mtime is newer than the
    #    context mtime for subdocuments
    assert not doc2.load_required()
    assert not doc3.load_required()
    assert len(caplog.record_tuples) == 8  # same number of messages as before.

    # 6. Touch a subdocument, and it should be the only one that requires an
    #    update
    wait()  # sleep time offset needed for different mtimes
    doc2.src_filepath.touch()
    assert not doc.load_required()
    assert doc2.load_required()  # 1 load_required message
    assert not doc3.load_required()
    assert len(caplog.record_tuples) == 9
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-1][2])

    # 7. Touch the root document, and all 3 documents should need an update
    wait()  # sleep time offset needed for different mtimes
    doc.src_filepath.touch()

    # 3 load required messages
    assert doc.load() is True  # documents were loaded
    assert len(caplog.record_tuples) == 12
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-3][2])
    assert ("source file is newer than the loaded document" in
            caplog.record_tuples[-2][2])
    assert ("The parent document is newer than this document" in
            caplog.record_tuples[-1][2])


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

def test_document_target_list_update(tmpdir):
    """Tests the proper updating of the target list."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a test source document
    project_root = tmpdir / 'src'
    project_root.mkdir()
    src_filepath = project_root / 'test.dm'

    markup = """---
    targets: txt
    ---
    """
    src_filepath.write_text(strip_leading_space(markup))

    doc = Document(src_filepath, tmpdir)

    assert doc.targets.keys() == {'.txt'}

    # Update the header
    markup = """---
    targets: tex
    ---
    """
    src_filepath.write_text(strip_leading_space(markup))
    doc.load()

    assert doc.targets.keys() == {'.tex'}


def test_document_ast_caching(tmpdir):
    """Tests the caching of the AST based on file modification times."""
    tmpdir = pathlib.Path(tmpdir)

    # Load the document and render it with no template. Opening the document
    # loads the ast.
    doc = Document("tests/document/example1/dummy.dm", tmpdir)

    body_attr = settings.body_attr
    ast = doc.context[body_attr]
    mtime = doc.mtime
    assert ast is not None
    assert mtime is not None

    # Try loading the AST again. At this point, it shouldn't be different
    doc.load()
    assert ast == doc.context[body_attr]
    assert mtime == doc.mtime


def test_document_label_mtime(tmpdir):
    """Test the label mtime method."""
    # 1. Setup a document with 3 chapters
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('test.dm')

    src_filepath.write("""
    ---
    targets: html
    ---
    @chapter[id=chapter-1]{Chapter 1}
    @ref{chapter-3}
    @chapter[id=chapter-2]{Chapter 2}
    @chapter[id=chapter-3]{Chapter 3}
    """)

    # Load the document
    doc = Document(str(src_filepath), str(tmpdir))
    doc.render()

    # Check that the labels were correctly loaded: 1 for the document and 1
    # for each of the 3 chapters.
    label_manager = doc.context['label_manager']

    labels = label_manager.get_labels()
    assert len(labels) == 4

    # Check that the labels were properly set
    assert label_manager.labels[0].title == 'test'
    assert label_manager.labels[1].title == 'Chapter 1'
    assert label_manager.labels[2].title == 'Chapter 2'
    assert label_manager.labels[3].title == 'Chapter 3'

    # The labels have been created and not modified yet. In this case, their
    # mtime attributes should match that of the source document
    doc_mtime = src_filepath.mtime()
    assert doc.context['mtime'] == doc_mtime
    assert label_manager.labels[0].mtime == doc_mtime  # document label
    assert label_manager.labels[1].mtime == doc_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime == doc_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime == doc_mtime  # chapter 3 label

    for label in label_manager.labels:
        assert label.doc_id == doc.doc_id

    # Determine the ids for the labels
    ids = [id(label) for label in label_manager.labels]

    # Change the first chapter. The labels should all now have an updated mtime
    src_filepath.write("""
    ---
    targets: html
    ---
    @chapter[id=chapter-1-intro]{Chapter 1}
    @ref{chapter-3}
    @chapter[id=chapter-2]{Chapter Two}
    @chapter[id=chapter-3]{Chapter 3}
    """)

    # Reload the document
    doc.load()

    # Check to see which labels have been created new.
    # The chapter 1 label has a new id, so its a new label
    # The chapter 2 label has the same id, but its title has changed and it
    # has been modified
    new_ids = [id(label) for label in label_manager.get_labels()]
    assert ids[0] == new_ids[0]  # document label
    assert ids[1] != new_ids[1]  # chapter 1 label (new label)
    assert ids[2] == new_ids[2]  # chapter 2 label
    assert ids[3] == new_ids[3]  # chapter 3 label

    # Check that the labels were properly set
    assert label_manager.labels[0].title == 'test'
    assert label_manager.labels[1].title == 'Chapter 1'
    assert label_manager.labels[2].title == 'Chapter Two'
    assert label_manager.labels[3].title == 'Chapter 3'

    # Check the label modification times. All the labels should have the new
    # mtime of the updated document.
    new_doc_mtime = src_filepath.mtime()
    assert doc.context['mtime'] == new_doc_mtime
    assert label_manager.labels[0].mtime == new_doc_mtime  # document label
    assert label_manager.labels[1].mtime == new_doc_mtime  # chapter 1 label
    assert label_manager.labels[2].mtime == new_doc_mtime  # chapter 2 label
    assert label_manager.labels[3].mtime == new_doc_mtime  # chapter 3 label


def test_document_custom_template(tmpdir, wait):
    """Tests the loading of custom templates from the yaml header."""
    tmpdir = pathlib.Path(tmpdir)

    # 1. Write a temporary file. We'll use the tree.html template, which
    # contains the text "Disseminate Project Index"
    project_root = tmpdir / 'src'
    project_root.mkdir()
    in_file = project_root / "index.dm"
    out_file = tmpdir / 'html' / "index.html"

    # Create a mock template
    template = project_root / "mytemplate.html"
    template.write_text("""This is my template""")

    markup = """
    ---
    template: mytemplate
    targets: html
    ---
    """
    in_file.write_text(strip_leading_space(markup))

    # Make document
    doc = Document(in_file)
    doc.render()
    assert "This is my template" in out_file.read_text()

    # 2. Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "This is my template"
    wait()  # sleep time offset needed for different mtimes
    markup = """
    ---
    template: mytemplate
    targets: html
    ---
    New file
    """
    in_file.write_text(markup)

    target_filepath = doc.targets['.html']
    assert doc.render_required(target_filepath=target_filepath)
    doc.render()
    assert "This is my template" in out_file.read_text()

    # 3. Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "This is my template"
    wait()  # sleep time offset needed for different mtimes
    in_file.write_text("test")

    target_filepath = doc.targets['.html']
    assert doc.render_required(target_filepath=target_filepath)
    doc.render()
    assert "This is my template" not in out_file.read_text()


def test_document_template_updates(tmpdir, wait):
    """Tests the update of rendered targets when the template changes."""
    tmpdir = pathlib.Path(tmpdir)

    # Create the markup source file and a test template
    project_root = tmpdir / 'src'
    project_root.mkdir()
    template = project_root / "index.html"
    in_file = project_root / "index.dm"
    target = tmpdir / 'html'
    target.mkdir()
    out_file = target / "index.html"

    template.write_text("""test1""")
    in_file.write_text("""---
    targets: html
    template: index
    ---""")

    # Load the document and test its contents
    doc = Document(in_file)
    doc.render()

    assert not doc.render_required(out_file)
    assert out_file.read_text() == 'test1'

    # Change the template and see if the rendered output changes
    wait()  # sleep time offset needed for different mtimes
    template.write_text("""test2""")

    assert doc.render_required(out_file)
    doc.render()
    assert out_file.read_text() == 'test2'


def test_document_context_update(tmpdir):
    """Tests that the context is properly updated in subsequent renders."""
    tmpdir = pathlib.Path(tmpdir)

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", tmpdir)

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
    doc.src_filepath = SourcePath(project_root="tests/document/example2",
                                  subpath="noheader.dm")
    doc.load(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.context
    assert 'author' not in doc.context
    assert 'macro' not in doc.context

    # The 'targets' entry should revert to the default
    assert doc.context['targets'] == settings.default_context['targets']

    assert id(doc.context) == context_id


def test_document_macros(tmpdir):
    """Tests that macros defined in the header of a document are properly
    processed."""
    tmpdir = pathlib.Path(tmpdir)

    temp_file = TargetPath(target_root=tmpdir,
                           target='html',
                           subpath='withheader.html')

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", tmpdir)

    doc.render()
    # See if the macro was properly replaced
    rendered_html = temp_file.read_text()
    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


def test_document_load_on_render(doc):
    """Test the proper loading of an updated source file on render."""

    # The initial document has the targets listed in the settings.py
    assert doc.targets.keys() == {'.html'}

    # Change the source file, and run the render function. The targets should
    # be updated to the new values in the updated header.
    src = """
    ---
    targets: html, txt
    ---
    """
    doc.src_filepath.write_text(src)
    doc.render()

    assert doc.targets.keys() == {'.html', '.txt'}


def test_document_recursion(tmpdir):
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

    doc = Document(src_filepath1, target_root)

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
    doc1 = Document(src_filepath1, target_root)
    doc2 = Document(src_filepath2, target_root)

    # The document should not have itself as a subdocument, but it can have
    # the other as a root document.
    assert len(doc1.subdocuments) == 1  # test-b as subdoc
    assert len(doc2.subdocuments) == 1  # test-a as subdoc


# Test targets
@pytest.fixture(params=['.html', '.tex'])
def target(request):
    return request.param


def test_document_render(tmpdir, target):
    """Tests the conversion of a basic html file."""
    tmpdir = pathlib.Path(tmpdir)

    ext = target
    stripped_ext = ext.strip('.')

    # Get a path to a temporary file
    temp_file = TargetPath(target_root=tmpdir,
                           target=stripped_ext,
                           subpath='dummy' + ext)

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm", tmpdir)

    targets = {k: v for k, v in doc.targets.items() if k == ext}
    doc.render(targets=targets)

    # Make sure the output matches the answer key
    render_file = doc.target_filepath(target=ext)
    assert temp_file.read_text() == render_file.read_text()

    # An invalid file raises an error
    with pytest.raises(exceptions.DocumentException):
        doc = Document("tests/document/missing.dm")


def test_document_render_missing_template(tmpdir):
    """Tests the rendering of a document when a specified templates is
    missing."""
    tmpdir = pathlib.Path(tmpdir)

    # 1. Prepare the document with a missing template
    src_filepath = tmpdir / 'test.dm'
    src = ("---\n"
           "targets: html, tex, pdf\n"
           "template: missing\n"
           "---\n"
           "test\n")
    src_filepath.write_text(src)

    # Raises a template not found error
    with pytest.raises(TemplateNotFound):
        doc = Document(src_filepath=src_filepath, target_root=tmpdir)


def test_document_example8(tmpdir):
    """Test the example8 document directory."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the paths
    src_path = tmpdir / 'src'
    src_path.mkdir()
    src_filepath = src_path / 'inept.dm'

    # Copy the source tree
    copy("tests/document/example8/src/fundamental_solnNMR/inept/inept.dm",
         src_filepath)

    # Load the document and render it with no template
    doc = Document(src_filepath, tmpdir)

    targets = {'.html': doc.target_filepath(target='.html'),
               '.tex': doc.target_filepath(target='.tex')}
    doc.render(targets=targets)

    # Check the rendered html
    key = pathlib.Path('tests/document/example8/html/inept.html').read_text()
    assert targets['.html'].read_text() == key
