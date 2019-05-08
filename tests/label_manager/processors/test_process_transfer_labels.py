"""
Test the TransferLabels class
"""
from disseminate.label_manager.processors import TransferLabels
from disseminate.label_manager.types import Label


def test_transfer_labels_processor(doctree):
    """Test the TransferLabels label processor."""

    # Retrieve the documents
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)

    # Create some labels
    label1 = Label(doc_id=doc1.doc_id, id='label1', kind='label', mtime=None)
    label2 = Label(doc_id=doc2.doc_id, id='label2', kind='label', mtime=None)

    # Create a transfer label processor
    processor = TransferLabels(context=doc1.context)

    # Try transferring the labels
    registered_labels = []
    collected_labels = {doc1.doc_id: [label1],
                        doc2.doc_id: [label2]}
    processor(registered_labels=registered_labels,
              collected_labels=collected_labels)

    # The labels are transferred and should have been removed from
    # collected_labels
    assert len(collected_labels) == 0

    # Check that the labels have been transfered to the list of registered
    # labels
    assert registered_labels == [label1, label2]
