"""
Test the function of document trees and subdocuments.
"""
import weakref

import pytest

from disseminate.document import Document
from disseminate.labels import DuplicateLabel
from disseminate.utils.tests import strip_leading_space


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
    assert len(doc.subdocuments) == 2
    assert doc.src_filepath == str(file1)

    keys = list(doc.subdocuments.keys())
    assert doc.subdocuments[keys[0]].src_filepath == str(file2)
    assert doc.subdocuments[keys[1]].src_filepath == str(file3)

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
    assert len(doc.subdocuments) == 1
    assert doc.src_filepath == str(file1)

    keys = list(doc.subdocuments.keys())
    assert doc.subdocuments[keys[0]].src_filepath == str(file2)

    # Now test Example5. Example5 has a file in the root directory, a file in
    # the 'sub1', 'sub2' and 'sub3' directories and a file in the 'sub2/subsub2'
    # directory
    doc = Document('tests/document/example5/index.dm',
                   target_root=str(tmpdir))

    assert len(doc.subdocuments) == 3  # Only subdocuments of doc
    assert len(doc.documents_list(recursive=True)) == 5  # all subdocuments

    sub_docs = list(doc.subdocuments.values())
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


def test_document_garbage_collection(tmpdir):
    """Test the garbage collection of document trees."""

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
    doc = Document(src_filepath=str(file1), target_root=str(tmpdir))

    # We can create weakrefs to the sub-documents
    doc2, doc3 = doc.documents_list(only_subdocuments=True)
    doc2_ref = weakref.ref(doc2)
    doc3_ref = weakref.ref(doc3)

    doc2, doc3 = None, None
    assert doc2_ref() is not None
    assert doc3_ref() is not None

    # Try rendering the document, then delete the subdocuments and they
    # should no longer exist
    doc.render()
    doc.subdocuments.clear()

    assert doc2_ref() is None
    assert doc3_ref() is None


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

    # Create the root document. The file2 subdocument *should not* have file1
    # as a subdocument
    doc1 = Document(src_filepath=str(file1))
    assert doc1.src_filepath == str(file1)

    assert len(doc1.subdocuments) == 1

    doc2 = doc1.documents_list(only_subdocuments=True)[0]
    assert doc2.src_filepath == str(file2)

    assert len(doc2.subdocuments) == 0


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
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[2].src_filepath == str(src_filepath2)

    # Reload the ast
    doc.get_ast()

    doc_list = doc.documents_list()
    assert len(doc_list) == 2
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)

    assert len(label_manager.labels) == 2
    label_list = label_manager.get_labels()
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'

    # 4. Now add the document back
    src_filepath1.write("""---
    include:
      file2.dm
      file3.dm
    ---""")

    # Reload the ast
    doc.get_ast()
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[2].src_filepath == str(src_filepath3)

    assert len(label_manager.labels) == 3
    label_list = label_manager.get_labels()
    assert label_list[0].id == 'doc:file1.dm'
    assert label_list[1].id == 'doc:file2.dm'
    assert label_list[2].id == 'doc:file3.dm'


def test_document_tree_updates_with_labels(tmpdir):
    """Test how updating the document tree impacts the numbering of labels."""

    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""
    ---
    include:
      file2.dm
      file3.dm
    targets: html
    ---
    @chapter{file1}
    """)
    src_filepath2.write("""
    @chapter{file2}
    """)
    src_filepath3.write("""
    @chapter{file3}
    """)

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath3)
    assert doc_list[2].number == 3

    # Check the ordering of labels
    label_manager = doc.context['label_manager']
    chapter_labels = label_manager.get_labels(kinds='chapter')

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(label_manager.labels) == 6

    assert len(chapter_labels) == 3  # one for each file
    assert chapter_labels[0].id == 'chapter:file1'
    assert chapter_labels[1].id == 'chapter:file2'
    assert chapter_labels[2].id == 'chapter:file3'

    # Render the files and check their mtimes
    doc.render()
    mtime1 = tmpdir.join('html').join('file1.html').mtime()
    mtime2 = tmpdir.join('html').join('file2.html').mtime()
    mtime3 = tmpdir.join('html').join('file3.html').mtime()

    # Now try reordering the files and see if the labels are reordered
    src_filepath1.write("""
    ---
    include:
      file3.dm
      file2.dm
    ---
    @chapter{file1}
    """)
    doc.get_ast()  # reload the file

    # Check the order of the documents
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath2)
    assert doc_list[2].number == 3

    # Check the number of labels: 3 for documents, 3 for chapters
    assert len(label_manager.labels) == 6

    chapter_labels = label_manager.get_labels(kinds='chapter')
    assert len(chapter_labels) == 3  # one for each file
    assert chapter_labels[0].id == 'chapter:file1'
    assert chapter_labels[1].id == 'chapter:file3'
    assert chapter_labels[2].id == 'chapter:file2'

    # A render should be required since the labels have changed
    doc1, doc2, doc3 = doc.documents_list(only_subdocuments=False,
                                          recursive=True)

    assert doc1.render_required(str(tmpdir.join('html').join('file1.html')))
    assert doc2.render_required(str(tmpdir.join('html').join('file2.html')))
    assert doc3.render_required(str(tmpdir.join('html').join('file3.html')))

    # The files have therefore been updated
    doc.render()
    assert mtime1 != tmpdir.join('html').join('file1.html').mtime()
    assert mtime2 != tmpdir.join('html').join('file2.html').mtime()
    assert mtime3 != tmpdir.join('html').join('file3.html').mtime()
