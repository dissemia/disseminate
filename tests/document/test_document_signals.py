"""
Tests for document signals
"""
import pathlib

from disseminate.document import Document
from disseminate.signals import signal
from disseminate.paths import SourcePath


def test_document_creation_deletion_signals(env):
    """Test document creation and deletion signals"""
    tmpdir = env.project_root

    # 1. Try the delete document signal
    #   Get the signals and register some subscribers
    document_deleted = signal('document_deleted')
    signals_dict = dict()

    @document_deleted.connect_via(order=-1)
    def delete(document):
        signals_dict['delete'] = True

    # Create a test document
    src_filepath = SourcePath(project_root=tmpdir, subpath='test.dm')
    src_filepath.touch()

    doc = Document(src_filepath=src_filepath, environment=env)

    assert 'delete' not in signals_dict
    del doc
    assert 'delete' in signals_dict

    # 2. Try the create document create signal
    document_created = signal('document_created')

    @document_created.connect_via(order=-1)
    def create(document):
        signals_dict['created'] = True

    assert 'created' not in signals_dict
    doc = Document(src_filepath=src_filepath, environment=env)
    assert 'created' in signals_dict

    # Disconnect the signals
    del document_deleted.receivers[-1]
    del document_created.receivers[-1]


def test_document_tree_update_signal(env, wait):
    """Test the document_tree_update signal"""
    tmpdir = env.project_root
    src_dir = tmpdir / 'src'
    src_dir.mkdir()

    # Create a tree of documents
    markup1 = """
    ---
    include:
      file2.dm
      file3.dm
    ---
    """
    file1 = SourcePath(project_root=src_dir, subpath='file1.dm')
    file1.write_text(markup1)

    markup2 = "test2"
    file2 = SourcePath(project_root=src_dir, subpath='file2.dm')
    file2.write_text(markup2)

    markup3 = "test3"
    file3 = SourcePath(project_root=src_dir, subpath='file3.dm')
    file3.write_text(markup3)

    # Setup a receiver for the document_tree_update
    document_tree_updated = signal('document_tree_updated')

    def mark_document(root_document):
        marked = getattr(root_document, 'marked', 0) + 1
        root_document.marked = marked

    document_tree_updated.connect(mark_document, order=-1)

    # Create the root document and check that it was marked
    root_doc = Document(src_filepath=file1, environment=env)
    doc2, doc3 = root_doc.documents_list(only_subdocuments=True)

    assert root_doc.marked == 1  # run once
    assert hasattr(doc2, 'marked') is False
    assert hasattr(doc3, 'marked') is False

    # Reset the root document and try reloading. The signal is not emitted in
    # this case
    delattr(root_doc, 'marked')

    assert root_doc.load() is False  # documents were loaded already

    for doc in (root_doc, doc2, doc3):
        assert hasattr(doc, 'marked') is False

    # Update each of the documents, and make sure that the root document is
    # marked by the signal every time
    for doc in (doc2, doc3):
        wait()  # a time offset for filesystems
        doc.src_filepath.write_text('updated')

        assert root_doc.load() is True  # documents were loaded

        assert root_doc.marked == 1  # run once
        assert hasattr(doc2, 'marked') is False
        assert hasattr(doc3, 'marked') is False

        # Reset root_doc
        delattr(root_doc, 'marked')

    # The documents are loaded, so this shouldn't need to be loaded again
    assert root_doc.load() is False

    # Reset the signal
    del document_tree_updated.receivers[-1]
