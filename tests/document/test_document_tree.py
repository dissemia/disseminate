"""
Test the function of document trees and subdocuments.
"""
import weakref
import os

from disseminate.document import Document
from disseminate.utils.tests import strip_leading_space


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


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


# Change in behavior: When a recursion exists, a recursion limit exception is
# raised. This is the desired behavior, rather than silently remove the
# recursion
#
# def test_document_tree_recursive_reference(tmpdir):
#     """Test the loading of trees and sub-documents with recursive references."""
#
#     # Setup the project_root in a temp directory
#     project_root = tmpdir.join('src').mkdir()
#
#     # Populate some files
#     file1 = project_root.join('file1.dm')
#     markup = """---
#     include:
#       file2.dm
#     targets: txt, tex
#     ---
#     """
#     file1.write(strip_leading_space(markup))
#
#     file2 = project_root.join('file2.dm')
#     markup = """---
#     include:
#       file1.dm
#     targets: txt, tex
#     ---
#     """
#     file2.write(strip_leading_space(markup))
#
#     # Create the root document. The file2 subdocument *should not* have file1
#     # as a subdocument
#     doc1 = Document(src_filepath=str(file1))
#     assert doc1.src_filepath == str(file1)
#
#     assert len(doc1.subdocuments) == 1
#
#     doc2 = doc1.documents_list(only_subdocuments=True)[0]
#     assert doc2.src_filepath == str(file2)
#
#     assert len(doc2.subdocuments) == 0


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
    # document. Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[2].src_filepath == str(src_filepath3)

    # Get the python ids for the document objects
    id_1 = id(doc_list[0])
    id_2 = id(doc_list[1])
    id_3 = id(doc_list[2])

    # 2. Now change the order of the sub-documents and reload the ast
    src_filepath1.write("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.get_ast()

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[1].src_filepath == str(src_filepath3)
    assert doc_list[2].src_filepath == str(src_filepath2)

    # Check that the document objects are the same
    assert id_1 == id(doc_list[0])
    assert id_3 == id(doc_list[1])
    assert id_2 == id(doc_list[2])

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

    assert id_1 == id(doc_list[0])
    assert id_2 == id(doc_list[1])

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

    # Check that the objects are all the same, except for the 3rd document,
    # which was re-created
    assert id_1 == id(doc_list[0])
    assert id_2 == id(doc_list[1])
    assert id_3 != id(doc_list[2])


def test_render_required(tmpdir):
    """Tests the render_required method with multiple files."""
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

    # Load the root document. This will load the AST for all documents,
    # but not render (and therefore create) the target files, so a render is
    # required.
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))
    label_manager = doc.context['label_manager']

    # 1. Test that a render is required when the target file hasn't been created
    assert not tmpdir.join('html').join('file1.html').exists()
    assert not tmpdir.join('html').join('file2.html').exists()
    assert not tmpdir.join('html').join('file3.html').exists()

    # Check that all documents need to be rendered
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert len(doc_list) == 3

    # Check the mtimes of the tags and labels
    mtime1 = doc_list[0].mtime
    mtime2 = doc_list[1].mtime
    mtime3 = doc_list[2].mtime

    # The problem here is that the register_labels is run for the root doc
    # and sub docs, reordering the local_order every time.
    assert mtime1 < mtime2 < mtime3
    assert doc_list[0].get_ast().mtime == mtime1
    assert doc_list[1].get_ast().mtime == mtime2
    assert doc_list[2].get_ast().mtime == mtime3

    # All three documents have a render_required
    for d in doc_list:
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath)

    # Now render the targets and a render should not be required
    # Altogether 6 invocations of the render_required method
    for d in doc_list:
        target_filepath = d.targets['.html']
        d.render()
        assert not d.render_required(target_filepath)

    # The target files should exist
    assert tmpdir.join('html').join('file1.html').exists()
    assert tmpdir.join('html').join('file2.html').exists()
    assert tmpdir.join('html').join('file3.html').exists()

    # 2. Test that a render is required when the source file modification time
    #    is updated. We'll update the 2nd document, and only its mtime should
    #    get updated once we get_ast()

    old_mtime = src_filepath2.mtime()
    touch(str(src_filepath2))
    assert old_mtime < src_filepath2.mtime()

    assert doc_list[0].get_ast().mtime == mtime1
    assert doc_list[1].get_ast().mtime != mtime2
    assert doc_list[2].get_ast().mtime == mtime3

    # Check the mtimes of the tags and labels
    mtime1 = doc_list[0].mtime
    mtime2 = doc_list[1].mtime
    mtime3 = doc_list[2].mtime

    assert doc_list[0].get_ast().mtime == mtime1
    assert doc_list[1].get_ast().mtime == mtime2
    assert doc_list[2].get_ast().mtime == mtime3

    for d, answer in zip(doc_list, [False, True, False]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render the 2nd document, and a the render_required should not longer be
    # True.
    doc_list[1].render()
    for d in doc_list:
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # 3. A render is required if the tags have been updated.
    #    In this case, place a reference in the 2nd document for the 3rd.
    src_filepath2.write("""
    @chapter{file2}
    @ref{ch:file3}
    """)

    # Now the 2nd document needs to be rendered
    for d, answer in zip(doc_list, [False, True, False]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render the document and all three documents do not require a rendering
    doc_list[1].render()
    for d in doc_list:
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # Touch the 3rd document. Now the @ref tag in the second document will
    # trigger a required rendering for the 2nd document, in addition to the 3rd
    # document becoming stale.
    touch(str(src_filepath3))

    for d, answer in zip(doc_list, [False, True, True]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render all documents
    for d in doc_list:
        d.render()
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # 4. A render is required if the document depends on a template that has
    #    been updated. We'll make document3 dependent on a template and update
    #    that template.
    template_filepath = src_path.join('test.html')

    template_filepath.write("""
    <html></html>
    """)
    src_filepath3.write("""
    ---
    template: test
    ---
    @chapter{file3}
    """)

    # Documents 2 and 3 require a render; document 3 because it was just written
    # and document 2 because it has a tag that depends on document 3.
    for d, answer in zip(doc_list, [False, True, True]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render all documents
    for d in doc_list:
        d.render()
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # Make sure the right template file was loaded
    template = doc_list[2].get_template(target='.html')
    assert template.filename == str(template_filepath)
    assert template.is_up_to_date

    # Now update the template, and the 3rd document will require a render
    template_filepath.write("""
    <html><body></body></html>
    """)
    assert not template.is_up_to_date

    for d, answer in zip(doc_list, [False, False, True]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer
