"""
Tests for document signals
"""
import pathlib

from disseminate.document import Document
from disseminate.signals import signal


def test_document_creation_deletion_signals(tmpdir):
    """Test document creation and deletion signals"""
    tmpdir = pathlib.Path(tmpdir)

    # 1. Try the delete document signal
    #   Get the signals and register some subscribers
    document_deleted = signal('document_deleted')
    signals_dict = dict()

    @document_deleted.connect_via(order=1)
    def delete(document):
        signals_dict['delete'] = True

    # Create a test document
    src_filepath = tmpdir / 'test.dm'
    src_filepath.touch()

    doc = Document(src_filepath=src_filepath, target_root=tmpdir)

    assert 'delete' not in signals_dict
    del doc
    assert 'delete' in signals_dict

    # 2. Try the create document create signal
    document_created = signal('document_created')

    @document_created.connect_via(order=1)
    def create(document):
        signals_dict['created'] = True

    assert 'created' not in signals_dict
    doc = Document(src_filepath=src_filepath, target_root=tmpdir)
    assert 'created' in signals_dict

    # Disconnect the signals
    document_deleted.reset()
    document_created.reset()
