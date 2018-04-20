"""
Tests for Document classes and functions.
"""
import pytest
from shutil import copyfile

from disseminate.document import Document, DocumentError
from disseminate.dependency_manager import MissingDependency
from disseminate.labels import DuplicateLabel
from disseminate.tags.toc import process_context_toc
from disseminate.utils.tests import strip_leading_space


def test_basic_conversion_html(tmpdir):
    """Tests the conversion of a basic html file."""
    # Get a path to a temporary file
    temp_file = str(tmpdir.join("html")) + '/dummy.html'

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm",
                   str(tmpdir))
    doc.render()
    # Make sure the output matches the answer key
    with open(temp_file, 'r') as f, \
         open("tests/document/example1/test_basic_conversion_html.html") as g:
        assert f.read() == g.read()

    # An invalid file raises an error
    with pytest.raises(DocumentError):
        doc = Document("tests/document/missing.dm")


def test_number_property(tmpdir):
    """Tests the document number property."""
    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""---
include:
  file2.dm
  file3.dm
---""")
    src_filepath2.ensure()
    src_filepath3.ensure()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))

    doc_list = doc.documents_list(only_subdocuments=False)
    assert doc.number == 1
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath3)
    assert doc_list[2].number == 3

    # Reorder the documents and reload the ast.
    src_filepath1.write("""---
include:
  file3.dm
  file2.dm
---""")
    doc.get_ast()

    doc_list = doc.documents_list(only_subdocuments=False)
    assert doc.number == 1
    assert doc_list[0].number == 1
    assert doc_list[1].number == 2
    assert doc_list[2].number == 3


def test_ast_caching(tmpdir):
    """Tests the caching of the AST based on file modification times."""
    # Get a path to a temporary file
    temp_file = str(tmpdir.join("html")) + '/dummy.html'

    # Load the document and render it with no template. Opening the document
    # loads the ast.
    doc = Document("tests/document/example1/dummy.dm",
                   str(tmpdir))

    ast = doc._ast
    mtime = doc._mtime
    assert ast is not None
    assert mtime is not None

    # Try loading the AST again. At this point, it shouldn't be different
    doc.get_ast()
    assert ast == doc._ast
    assert mtime == doc._mtime


def test_target_list():
    """Test the setting of the target_list property."""
    doc = Document("tests/document/example1/dummy.dm")

    # dummy.dm has the entry 'html, tex' set in the header.
    assert doc.target_list == ['.html', '.tex']


def test_target_filepath():
    """Test the target_filepath method."""

    # 1. Example1 does not have markup source files in a source
    #    directory. Target files will be saved in the project directory
    doc = Document("tests/document/example1/dummy.dm")

    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example1/html/dummy.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "dummy.html")
    assert (doc.target_filepath('.tex', render_path=True) ==
            "tests/document/example1/tex/dummy.tex")
    assert (doc.target_filepath('.tex', render_path=False) ==
            "dummy.tex")

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example4/html/file.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "file.html")

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")
    assert doc.target_root == 'tests/document/example5'
    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/index.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "index.html")

    # Check the sub_documents
    sub_document = list(doc.sub_documents.values())[0]
    assert sub_document.target_root == 'tests/document/example5'
    assert (sub_document.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub1/index.html")

    sub_document = list(doc.sub_documents.values())[1]
    assert sub_document.target_root == 'tests/document/example5'
    assert (sub_document.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub2/index.html")

    sub_document = list(sub_document.sub_documents.values())[0]
    assert sub_document.target_root == 'tests/document/example5'
    assert (sub_document.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub2/subsub2/index.html")

    sub_document = list(doc.sub_documents.values())[2]
    assert sub_document.target_root == 'tests/document/example5'
    assert (sub_document.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub3/index.html")


def test_documents_list():
    """Test the documents_list function."""

    # 1. Load documents from example7. Example7 has one target ('.html')
    #    specified in the root file, 'src/file1.dm'. This file also includes
    #    a file, 'sub1/file11.dm', which in turn includes
    #    'sub1/subsub1/file111.dm'. All 3 files have content
    doc = Document('tests/document/example7/src/file1.dm')

    # Get all files recursively, including the root document
    docs = doc.documents_list(only_subdocuments=False, recursive=True)
    assert len(docs) == 3
    assert docs[0].src_filepath == 'tests/document/example7/src/file1.dm'
    assert docs[1].src_filepath == 'tests/document/example7/src/sub1/file11.dm'
    assert (docs[2].src_filepath ==
            'tests/document/example7/src/sub1/subsub1/file111.dm')

    # Get only the sub-document and the root document
    docs = doc.documents_list(only_subdocuments=False, recursive=False)
    assert len(docs) == 2
    assert docs[0].src_filepath == 'tests/document/example7/src/file1.dm'
    assert docs[1].src_filepath == 'tests/document/example7/src/sub1/file11.dm'

    # Get online the sub-document
    docs = doc.documents_list(only_subdocuments=True, recursive=False)
    assert len(docs) == 1
    assert docs[0].src_filepath == 'tests/document/example7/src/sub1/file11.dm'


def test_get_grouped_asts(tmpdir):
    """Test the get_grouped_asts function."""

    # 1. Load documents from example7. Example7 has one target ('.html')
    #    specified in the root file, 'src/file1.dm'. This file also includes
    #    a file, 'sub1/file11.dm', which in turn includes
    #    'sub1/subsub1/file111.dm'. All 3 files have content.
    target_root7 = tmpdir.join('example7')
    target_root7.mkdir()

    doc = Document('tests/document/example7/src/file1.dm', str(target_root7))

    # A non-existent target should return an empty ast
    ast = doc.get_grouped_asts(target='.tex')

    assert ast.content == []

    # An existing target should include all the asts.
    ast = doc.get_grouped_asts(target='.html')
    assert ast[0].content == 'file1.dm'
    assert ast[1].content == 'file11.dm'
    assert ast[2].content == 'file111.dm'


def test_render_collection(tmpdir):
    """Test the rendering of a collection of documents."""
    # 1. Load documents from example7. Example7 has one target ('.html')
    #    specified in the root file, 'src/file1.dm'. This file also includes
    #    a file, 'sub1/file11.dm', which in turn includes
    #    'sub1/subsub1/file111.dm'. All 3 files have content.
    target_root7 = tmpdir.join('example7')
    target_root7.mkdir()

    doc = Document('tests/document/example7/src/file1.dm', str(target_root7))

    # Try rendering the file. By default only the root document is rendered
    doc.render()

    assert target_root7.join('html').join('file1.html').check()

    html = target_root7.join('html').join('file1.html').read()
    assert '<p>file1.dm</p>' in html
    assert '<p>file11.dm</p>' not in html
    assert '<p>file111.dm</p>' not in html

    # Render the collection. Since the source file hasn't changed, we have to
    # delete the target to trigger a render.
    doc.context['render'] = 'collection'
    target_root7.join('html').join('file1.html').remove()
    doc.render()

    assert target_root7.join('html').join('file1.html').check()

    html = target_root7.join('html').join('file1.html').read()
    assert '<p>file1.dm</p>' in html
    assert '<p>file11.dm</p>' in html
    assert '<p>file111.dm</p>' in html


def test_custom_template(tmpdir):
    """Tests the loading of custom templates from the yaml header."""
    # Write a temporary file. We'll use the tree.html template, which contains
    # the text "Disseminate Project Index"
    tmpdir.mkdir('src')
    in_file = tmpdir.join('src').join("index.dm")
    out_file = tmpdir.join('html').join("index.html")

    markup = """
    ---
    template: tree
    targets: html
    ---
    """
    in_file.write(strip_leading_space(markup))

    # Make document
    doc = Document(str(in_file))
    doc.render()
    assert "Disseminate Project Index" in out_file.read()

    # Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "Disseminate Project Index"
    in_file.write("test")
    doc.render()
    assert "Disseminate Project Index" not in out_file.read()


def test_context_update(tmpdir):
    """Tests that the context is properly updated in subsequent renders."""
    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", str(tmpdir))
    doc.get_ast()

    # Check the contents  of the local_context
    assert 'title' in doc.context
    assert doc.context['title'] == 'My first title'

    assert 'author' in doc.context
    assert doc.context['author'] == 'Justin L Lorieau'

    assert 'macros' in doc.context

    # Get the local_context id to make sure it stays the same
    context_id = id(doc.context)
    # Now switch to a file without a header and make sure the header values
    # are removed
    doc.src_filepath = "tests/document/example2/noheader.dm"
    doc.get_ast(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.context
    assert 'author' not in doc.context
    assert 'macros' not in doc.context

    assert id(doc.context) == context_id


def test_target_list_update(tmpdir):
    """Tests the proper updating of the target list."""

    # Create a test source document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('test.dm')

    markup = """---
    targets: txt
    ---
    """
    src_filepath.write(strip_leading_space(markup))

    doc = Document(src_filepath, str(tmpdir))

    assert doc.target_list == ['.txt']

    # Update the header
    markup = """---
        targets: tex
        ---
        """
    src_filepath.write(strip_leading_space(markup))
    doc.get_ast()

    assert doc.target_list == ['.tex']


def test_macros(tmpdir):
    """Tests that macros defined in the header of a document are properly
    processed."""
    temp_file = tmpdir.join('html').join('withheader.html')

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm",
                   str(tmpdir))
    doc.render()

    # See if the macro was properly replaced
    rendered_html = temp_file.read()

    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


def test_dependencies_img(tmpdir):
    """Tests that the image dependencies are correctly reset when the AST is
    reprocessed."""
    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src')
    project_root.mkdir()
    target_root = str(tmpdir)

    # Copy a dependency image file to this directory
    img_path = str(project_root.join('sample.png'))
    copyfile('tests/document/example3/sample.png',
             img_path)

    # Make a document source file
    markup = """
    ---
    targets: html
    ---
    @img{sample.png}
    """

    src_filepath = project_root.join('test.dm')
    src_filepath.write(strip_leading_space(markup))

    # Create a document
    doc = Document(str(src_filepath), tmpdir)

    # Check that the document and dependency manager paths are correct
    assert doc.project_root == str(project_root)
    assert doc.target_root == str(target_root)

    dep = doc.context['dependency_manager']
    assert dep.project_root == str(project_root)
    assert dep.target_root == str(target_root)

    # Render the document
    doc.render()

    # The img file should be a dependency in the '.html' target
    d = dep.get_dependency(target='.html', src_filepath=img_path)
    assert d.dep_filepath == 'sample.png'

    # Rewrite the document source file without the dependency
    markup = ""
    src_filepath.write(markup)

    # Render the document and the dependency should have been removed.
    doc.render()

    # A missing dependency raises a MissingDependency exception
    with pytest.raises(MissingDependency):
        d = dep.get_dependency(target='.html', src_filepath=img_path)


def test_document_labels(tmpdir):
    """Test the correct assignment of labels for a document."""

    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src')
    project_root.mkdir()
    target_root = tmpdir

    # Make a document source file
    src_filepath = project_root.join('test.dm')
    src_filepath.ensure(file=True)  # touch the file

    # Create a document
    doc = Document(str(src_filepath), str(target_root))

    # 1. Test the label when the '_project_root' value is not assigned in the
    #    global_context. In this case, the label is identified by the document's
    #    src_filepath

    # The label should have been created on document creation and calling the
    # get_ast method
    man = doc.context['label_manager']
    assert len(man.labels) == 1
    label = man.get_label(id="doc:test.dm")
    assert label.id == "doc:test.dm"
    assert label.kind == ('document', 'document-level-1')


def test_document_tree(tmpdir):
    """Test the loading of trees and sub-documents from a document."""

    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src').mkdir()

    # Populate some files
    file1 = project_root.join('main.dm')
    markup = """---
    include:
      sub/file2.dm
      sub/file3.dm
    targets: txt, tex
    ---
    """
    file1.write(strip_leading_space(markup))
    file2 = project_root.join('sub').join('file2.dm').ensure(file=True)
    file3 = project_root.join('sub').join('file3.dm').ensure(file=True)

    for text, f in (('file2', file2), ('file3', file3)):
        f.write(text)

    # Create the root document
    doc = Document(src_filepath=str(file1))

    # Test the paths
    assert len(doc.sub_documents) == 2
    assert doc.src_filepath == str(file1)

    keys = list(doc.sub_documents.keys())
    assert doc.sub_documents[keys[0]].src_filepath == str(file2)
    assert doc.sub_documents[keys[1]].src_filepath == str(file3)

    # Update the root document and remove a file
    markup = """---
    include:
      sub/file2.dm
    targets: txt, tex
    ---
    """
    file1.write(strip_leading_space(markup))
    doc.get_ast()

    # Test the paths
    assert len(doc.sub_documents) == 1
    assert doc.src_filepath == str(file1)

    keys = list(doc.sub_documents.keys())
    assert doc.sub_documents[keys[0]].src_filepath == str(file2)

    # Now test Example5. Example5 has a file in the root directory, a file in
    # the 'sub1', 'sub2' and 'sub3' directories and a file in the 'sub2/subsub2'
    # directory
    doc = Document('tests/document/example5/index.dm',
                   target_root=str(tmpdir))

    assert len(doc.sub_documents) == 3  # Only sub_documents of doc
    assert len(doc.documents_list(recursive=True)) == 5  # all sub_documents

    sub_docs = list(doc.sub_documents.values())
    assert sub_docs[0].src_filepath == 'tests/document/example5/sub1/index.dm'
    assert sub_docs[1].src_filepath == 'tests/document/example5/sub2/index.dm'
    assert sub_docs[2].src_filepath == 'tests/document/example5/sub3/index.dm'

    all_docs = doc.documents_list(recursive=True)
    assert all_docs[0].src_filepath == 'tests/document/example5/index.dm'
    assert all_docs[1].src_filepath == 'tests/document/example5/sub1/index.dm'
    assert all_docs[2].src_filepath == 'tests/document/example5/sub2/index.dm'
    assert all_docs[3].src_filepath == ('tests/document/example5/sub2/subsub2/'
                                        'index.dm')
    assert all_docs[4].src_filepath == 'tests/document/example5/sub3/index.dm'

    # Check that the targets are rendered in the right locations
    doc.render()

    assert tmpdir.join('html').join('index.html').exists()
    assert tmpdir.join('html').join('sub1').join('index.html').exists()
    assert tmpdir.join('html').join('sub2').join('index.html').exists()
    assert (tmpdir.join('html').join('sub2').join('subsub2')
            .join('index.html').exists())
    assert tmpdir.join('html').join('sub3').join('index.html').exists()


def test_document_tree_recursive_reference(tmpdir):
    """Test the loading of trees and sub-documents with recursive references."""

    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src').mkdir()

    # Populate some files
    file1 = project_root.join('file1.dm')
    markup = """---
    include:
      file2.dm
    targets: txt, tex
    ---
    """
    file1.write(strip_leading_space(markup))

    file2 = project_root.join('file2.dm')
    markup = """---
    include:
      file1.dm
    targets: txt, tex
    ---
    """
    file2.write(strip_leading_space(markup))

    # Create the root document. This will raise a DuplicateLabel error since
    # a document is loaded twice.
    with pytest.raises(DuplicateLabel):
        doc = Document(src_filepath=str(file1))


def test_document_tree_matching_filenames(tmpdir):
    """Test the loading of trees with matching filenames in sub-directories."""

    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src').mkdir()

    # Populate some files
    file1 = project_root.join('file1.dm')
    markup = """---
    include:
      sub/file1.dm
    targets: txt, tex
    ---
    """
    file1.write(strip_leading_space(markup))

    project_root.join('sub').mkdir()
    file2 = project_root.join('sub').join('file1.dm')
    markup = """test"""
    file2.write(strip_leading_space(markup))

    # Create the root document
    doc = Document(src_filepath=str(file1))
    doc.render()


def test_document_tree_updates(tmpdir):
    """Test the updates to the document tree and labels."""
    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""---
include:
  file2.dm
  file3.dm
---""")
    src_filepath2.ensure()
    src_filepath3.ensure()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))

    # There should now be 3 total documents and 3 sets of labels, one for each
    # document
    assert len(doc.documents_list()) == 3

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[2].src_filepath == str(src_filepath3)

    # There should be 3 labels, one for each document. Check them and their
    # ordering
    label_manager = doc.context['label_manager']

    assert len(label_manager.labels) == 3
    label_list = label_manager.get_labels()
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'
    assert label_list[2].id == 'doc:file3.dm'

    # 2. Now change the order of the sub-documents and reload the ast
    src_filepath1.write("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.get_ast()

    # Check the ordering of documents
    doc_list = doc.documents_list()

    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[2].src_filepath == str(src_filepath2)

    # Check the ordering of labels
    assert len(label_manager.labels) == 3
    label_list = label_manager.get_labels()
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file3.dm'
    assert label_list[2].id == 'doc:file2.dm'

    # 3. Now remove one document
    src_filepath1.write("""---
include:
  file2.dm
---""")

    # The documents shouldn't change until the ast is reloaded
    assert len(doc.documents_list()) == 3

    # Reload the ast
    doc.get_ast()
    assert len(doc.documents_list()) == 2
    assert len(label_manager.labels) == 2


def test_document_toc(tmpdir):
    """Test the generation of a toc from the header of a document."""
    # Load example4, which has a file.dm with a 'toc' entry in the heading
    # for documents.
    doc = Document('tests/document/example4/src/file.dm',
                   target_root=str(tmpdir))

    # Render the doc
    doc.render()

    # Make sure the 'toc' context entry is correct
    assert doc.context['toc'] == 'documents'

    # Make a context and process the toc
    context = dict(doc.context)
    process_context_toc(context, target='.html')

    key = """<ol class="toc-document">
      <li class="li-document-level-1">
        <a class="document-level-1-ref" href="/file.html">My first title</a>
      </li>
    </ol>
    """

    assert strip_leading_space(key) == context['toc']
