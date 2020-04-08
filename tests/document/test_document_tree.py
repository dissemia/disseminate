"""
Test the function of document trees and subdocuments.
"""
import weakref
import os

from disseminate.document import Document
from disseminate.utils.tests import strip_leading_space
from disseminate import settings, SourcePath, TargetPath


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def test_documents_list(load_example):
    """Test the documents_list function."""

    # 1. Load documents from example7. Example7 has one target ('.html')
    #    specified in the root file, 'src/file1.dm'. This file also includes
    #    a file, 'sub1/file11.dm', which in turn includes
    #    'sub1/subsub1/file111.dm'. All 3 files have content
    src_filepath1 = SourcePath(project_root='tests/document/example7/src',
                               subpath='file1.dm')
    src_filepath2 = SourcePath(project_root='tests/document/example7/src',
                               subpath='sub1/file11.dm')
    src_filepath3 = SourcePath(project_root='tests/document/example7/src',
                               subpath='sub1/subsub1/file111.dm')
    doc = load_example(src_filepath1)

    # Get all files recursively, including the root document
    docs = doc.documents_list(only_subdocuments=False, recursive=True)
    assert len(docs) == 3
    assert docs[0].src_filepath == src_filepath1
    assert docs[1].src_filepath == src_filepath2
    assert docs[2].src_filepath == src_filepath3

    # Get only the sub-document and the root document
    docs = doc.documents_list(only_subdocuments=False, recursive=False)
    assert len(docs) == 2
    assert docs[0].src_filepath == src_filepath1
    assert docs[1].src_filepath == src_filepath2

    # Get online the sub-document
    docs = doc.documents_list(only_subdocuments=True, recursive=False)
    assert len(docs) == 1
    assert docs[0].src_filepath == src_filepath2


def test_document_tree1(doc, wait):
    """Test the loading of trees and sub-documents from a document."""

    # Setup the project_root in a temp directory
    env = doc.context['environment']
    project_root = env.project_root
    subdir = project_root / 'sub'
    subdir.mkdir()

    # Populate some files
    file1 = doc.src_filepath
    markup1 = """---
    include:
      sub/file2.dm
      sub/file3.dm
    targets: txt, html
    ---
    """
    markup2 = """---
    targets: pdf
    ---
    """
    markup3 = """---
    targets: pdf
    ---
    """

    file1.write_text(strip_leading_space(markup1))
    file2 = SourcePath(project_root=project_root, subpath='sub/file2.dm')
    file3 = SourcePath(project_root=project_root, subpath='sub/file3.dm')

    # Write to the subdocuments
    file2.write_text(markup2)
    file3.write_text(markup3)

    # Reload root document
    doc.load()

    # Test the paths
    assert len(doc.subdocuments) == 2
    assert doc.src_filepath == file1

    keys = list(doc.subdocuments.keys())
    assert doc.subdocuments[keys[0]].src_filepath == file2
    assert doc.subdocuments[keys[1]].src_filepath == file3

    # Test the targets
    assert doc.targets.keys() == {'.html', '.txt'}
    assert doc.get_renderer().targets == {'.html', '.txt'}

    # Update the root document and remove a file
    assert doc.load() is False  # no documents are not loaded yet
    wait()  # time offset for the filesystem
    markup = """---
    include:
      sub/file2.dm
    targets: txt, tex
    ---
    """
    file1.write_text(strip_leading_space(markup))
    assert doc.load() is True  # documents were loaded (doc changed)
    assert doc.load() is False  # documents don't need to be reloaded

    # Test the paths
    assert len(doc.subdocuments) == 1
    assert doc.src_filepath == file1

    keys = list(doc.subdocuments.keys())
    assert doc.subdocuments[keys[0]].src_filepath == file2

    # Test the targets
    assert doc.targets.keys() == {'.txt', '.tex'}
    assert doc.get_renderer().targets == {'.txt', '.tex'}

    # Now change file2 and reloading the root document, doc, should load
    # some new files since it has doc2 (file2) as a subdocument
    wait()
    file2.write_text('test2')

    assert doc.load() is True  # documents were loaded
    assert doc.load() is False  # documents already loaded


def test_document_tree2(load_example):
    """Test the loading of trees and sub-documents from a document."""

    # Now test Example5. Example5 has a file in the root directory, a file in
    # the 'sub1', 'sub2' and 'sub3' directories and a file in the 'sub2/subsub2'
    # directory
    doc = load_example("tests/document/example5/index.dm")
    project_root = doc.project_root
    target_root = doc.target_root

    # Setup paths of subdocuments
    src_filepath1 = SourcePath(project_root=project_root,
                               subpath='sub1/index.dm')
    src_filepath2 = SourcePath(project_root=project_root,
                               subpath='sub2/index.dm')
    src_filepath3 = SourcePath(project_root=project_root,
                               subpath='sub3/index.dm')
    src_filepath22 = SourcePath(project_root=project_root,
                                subpath='sub2/subsub2/index.dm')

    assert len(doc.subdocuments) == 3  # Only subdocuments of doc
    assert len(doc.documents_list(recursive=True)) == 5  # all subdocuments

    sub_docs = list(doc.subdocuments.values())
    assert sub_docs[0].src_filepath == src_filepath1
    assert sub_docs[1].src_filepath == src_filepath2
    assert sub_docs[2].src_filepath == src_filepath3

    all_docs = doc.documents_list(recursive=True)
    assert len(all_docs) == 5
    assert all_docs[0].src_filepath == doc.src_filepath
    assert all_docs[1].src_filepath == src_filepath1
    assert all_docs[2].src_filepath == src_filepath2
    assert all_docs[3].src_filepath == src_filepath22
    assert all_docs[4].src_filepath == src_filepath3

    # Check that the targets are rendered in the right locations
    doc.render()

    for doc in all_docs:
        target_filepath = doc.target_filepath('.html')
        assert target_filepath.suffix == '.html'
        assert target_filepath.is_file()


def test_document_garbage_collection(doc):
    """Test the garbage collection of document trees."""

    # Setup the project_root in a temp directory
    env = doc.context['environment']
    project_root = env.project_root

    # Populate some files
    file1 = doc.src_filepath
    markup = """---
    include:
      sub/file2.dm
      sub/file3.dm
    targets: txt, tex
    ---
    """
    file1.write_text(strip_leading_space(markup))

    # Create the subdocuments
    subdir = SourcePath(project_root=project_root, subpath='sub')
    subdir.mkdir()
    file2 = SourcePath(project_root=project_root, subpath='sub/file2.dm')
    file3 = SourcePath(project_root=project_root, subpath='sub/file3.dm')

    file2.write_text('file2')
    file3.write_text('file3')

    # Reload the document
    doc.load()

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


def test_document_tree_matching_filenames(doc):
    """Test the loading of trees with matching filenames in sub-directories."""

    # Setup the project_root in a temp directory
    env = doc.context['environment']
    project_root = env.project_root

    # Populate some files
    file1 = doc.src_filepath
    markup = """---
    include:
      sub/file1.dm
    targets: txt, tex
    ---
    """
    file1.write_text(strip_leading_space(markup))

    subdir = SourcePath(project_root, 'sub')
    subdir.mkdir()
    file2 = SourcePath(project_root=project_root, subpath='sub/file1.dm')

    markup = """test"""
    file2.write_text(strip_leading_space(markup))

    # Reload root document
    doc.load()
    doc.render()


def test_document_tree_updates(doc, wait):
    """Test the updates to the document tree and labels.

    Note that this test was previously conducted by checking the python 'id' of
    objects to determine whether a new document object was created. However,
    when an old object was deleted, there was a small change (~2%) that the new
    object would get the same id, making this test fail. Instead, the document
    objects are marked with a 'test_object' attribute, which disappears when
    a new object is created.
    """
    # Create a document tree.
    env = doc.context['environment']
    project_root = env.project_root
    src_filepath1 = doc.src_filepath

    src_filepath2 = SourcePath(project_root=project_root, subpath='file2.dm')
    src_filepath3 = SourcePath(project_root=project_root, subpath='file3.dm')

    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")
    src_filepath2.touch()
    src_filepath3.touch()

    # 1. Reload the root document
    doc.load()

    # There should now be 3 total documents and 3 sets of labels, one for each
    # document. Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    # Mark the document objects by setting a test attribute
    for d in doc_list:
        assert not hasattr(d, 'test_object')

    doc_list[0].test_object = 1
    doc_list[1].test_object = 1
    doc_list[2].test_object = 1

    # 2. Now change the order of the sub-documents and reload the ast
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""---
    include:
      file3.dm
      file2.dm
    ---""")
    doc.load()

    # Check the ordering of documents
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # Check that the document objects are the same by making sure they still
    # have their attribute marking
    for d in doc_list:
        assert hasattr(d, 'test_object')

    # 3. Now remove one document
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""---
    include:
      file2.dm
    ---""")

    # The documents shouldn't change until the ast is reloaded
    doc_list = doc.documents_list()
    assert len(doc_list) == 3

    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath3
    assert doc_list[2].src_filepath == src_filepath2

    # Reload the ast
    doc.load()

    doc_list = doc.documents_list()
    assert len(doc_list) == 2
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2

    # Check that the two remaining objects have their attribute marking
    for d in doc_list:
        assert hasattr(d, 'test_object')

    # 4. Now add the document back
    wait()  # sleep time offset needed for different mtimes
    src_filepath1.write_text("""---
    include:
      file2.dm
      file3.dm
    ---""")

    # Reload the ast
    doc.load()
    doc_list = doc.documents_list()
    assert len(doc_list) == 3
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[2].src_filepath == src_filepath3

    # Check that the objects are all the same, except for the 3rd document,
    # which was re-created. This 3rd object shouldn't have the test attribute.
    assert hasattr(doc_list[0], 'test_object')
    assert hasattr(doc_list[1], 'test_object')
    assert not hasattr(doc_list[2], 'test_object')


def test_render_required(doc, wait):
    """Tests the render_required method with multiple files."""
    # Create a document tree.
    env = doc.context['environment']
    project_root = env.project_root
    src_filepath1 = doc.src_filepath

    src_filepath2 = SourcePath(project_root=project_root, subpath='file2.dm')
    src_filepath3 = SourcePath(project_root=project_root, subpath='file3.dm')

    src_filepath1.write_text("""
    ---
    include:
      file2.dm
      file3.dm
    targets: html
    ---
    @chapter{file1}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath2.write_text("""
    @chapter{file2}
    """)
    wait()  # sleep time offset needed for different mtimes

    src_filepath3.write_text("""
    @chapter{file3}
    """)
    wait()  # sleep time offset needed for different mtimes

    # Load the root document.
    doc.load()

    # 1. Test that a render is required when the target file hasn't been
    #    created
    # Check that all documents need to be rendered
    doc_list = doc.documents_list(only_subdocuments=False, recursive=True)
    assert len(doc_list) == 3

    for d in doc_list:
        target_filepath = d.targets['.html']
        assert not target_filepath.is_file()

    # Check the mtimes of the document
    body_attr = settings.body_attr
    mtime1 = doc_list[0].mtime
    mtime2 = doc_list[1].mtime
    mtime3 = doc_list[2].mtime

    # Check that these match the modification times for the body tag in the
    # context
    assert mtime1 < mtime2 < mtime3
    assert doc_list[0].context[body_attr].mtime == mtime1
    assert doc_list[1].context[body_attr].mtime == mtime2
    assert doc_list[2].context[body_attr].mtime == mtime3

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
    for d in doc_list:
        target_filepath = d.targets['.html']
        assert target_filepath.is_file()

    # 2. Test that a render is required when the source file modification time
    #    is updated. We'll update the 2nd document, and only its mtime should
    #    get updated once we load the document

    src_filepath2.touch()
    assert mtime2 < src_filepath2.stat().st_mtime

    for doc in doc_list:
        doc.load()

    # The modification time (mtime) for the body tag in the second document
    # is now updated to the new mtime.
    assert doc_list[0].context[body_attr].mtime == mtime1
    assert doc_list[1].context[body_attr].mtime != mtime2
    assert doc_list[1].context[body_attr].mtime == src_filepath2.stat().st_mtime
    assert doc_list[2].context[body_attr].mtime == mtime3

    # Update the mtimes and check that the body tag now matches the new mtimes
    mtime2 = src_filepath2.stat().st_mtime

    assert doc_list[0].context[body_attr].mtime == mtime1
    assert doc_list[1].context[body_attr].mtime == mtime2
    assert doc_list[2].context[body_attr].mtime == mtime3

    # The doc2 requires a render now.
    for d, answer in zip(doc_list, [False, True, False]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render the documents
    for d in doc_list:
        d.render()
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # 3. A render is required if the tags have been updated.
    #    In this case, place a reference in the 2nd document for the 3rd.
    wait()  # sleep time offset needed for different mtimes
    src_filepath2.write_text("""
    @chapter{file2}
    @ref{ch:file3-dm-file3}
    """)

    # Now the 2nd document needs to be rendered.
    for d, answer in zip(doc_list, [False, True, False]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render the documents and the documents will not require a rendering
    for d in doc_list:
        d.render()
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)

    # Touch the 3rd document. Now the @ref tag in the second document has
    # changed
    wait()  # offset time for filesystem
    src_filepath3.touch()

    for d, answer in zip(doc_list, [False, True, True]):
        target_filepath = d.targets['.html']
        assert d.render_required(target_filepath) is answer

    # Render all documents
    for d in doc_list:
        d.render()
        target_filepath = d.targets['.html']
        assert not d.render_required(target_filepath)
