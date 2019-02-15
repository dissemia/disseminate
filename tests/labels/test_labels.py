"""
Tests the label manager and label classes.
"""
import pytest
import weakref

from disseminate.labels.labels import (Label, DuplicateLabel, find_duplicates,
                                       transfer_labels, order_labels)


def test_label_find_duplicates():
    """Test the find_duplicates function."""
    class TestLabel(Label):
        pass

    # Create a set of registered labels and collected labels
    label1 = Label(doc_id='a', id='1', kind='label', mtime=None)
    label2 = Label(doc_id='a', id='2', kind='label', mtime=None)
    label3 = Label(doc_id='a', id='3', kind='label', mtime=None)
    label4 = TestLabel(doc_id='b', id='1', kind='label', mtime=None)  # duplicate label

    # Try running find_duplicates without a duplicate label
    find_duplicates(registered_labels=[label1, label2],
                    collected_labels={'a': [label3]})  # no duplicates

    # Try running find_duplicates with a duplicate label
    with pytest.raises(DuplicateLabel):
        find_duplicates(registered_labels=[label1, label2],
                        collected_labels={'a': [label3], 'b': [label4]})

    # But no exception is raised if the kind is listed in the exclude_kinds
    find_duplicates(registered_labels=[label1, label2],
                    collected_labels={'a': [label3], 'b': [label4]},
                    exclude_labels=TestLabel)


def test_label_transfer_labels():
    """Test the transfer_labels function."""
    # Create test (mock) documents
    class MockDock(object):
        doc_id = None

    doc1 = MockDock()
    doc2 = MockDock()

    doc1.doc_id = 'doc1'
    doc1.documents_list = [doc1, doc2]
    doc2.doc_id = 'doc2'

    # Create some labels
    label1 = Label(doc_id=doc1.doc_id, id='label1', kind='label', mtime=None)
    label2 = Label(doc_id=doc2.doc_id, id='label2', kind='label', mtime=None)

    # Try transferring the labels
    registered_labels = []
    collected_labels = {doc1.doc_id: [label1], doc2.doc_id: [label2]}
    transfer_labels(registered_labels=registered_labels,
                    collected_labels=collected_labels,
                    doc_ids=[doc1.doc_id, doc2.doc_id])

    # The labels are transferred and should have been removed from
    # collected_labels
    assert len(collected_labels) == 0

    # Check that the labels have been transfered to the list of registered
    # labels
    assert registered_labels == [label1, label2]


def test_label_order_labels(context_cls):
    """Test the order_labels function."""
    # Create test (mock) documents
    class MockDock(object):
        doc_id = None

    doc1 = MockDock()
    doc2 = MockDock()

    doc1.doc_id = 'doc1'
    doc1.documents_list = [doc1, doc2]
    doc2.doc_id = 'doc2'

    context = context_cls(document=weakref.ref(doc1))

    # Make a test label class
    class TableLabel(Label):
        pass

    # Create some labels
    label1 = Label(doc_id=doc1.doc_id, id='label1', kind=('content', 'figure'),
                   mtime=None)
    label2 = Label(doc_id=doc1.doc_id, id='label2', kind=('content', 'figure'),
                   mtime=None)
    label3 = TableLabel(doc_id=doc1.doc_id, id='label3',
                        kind=('content', 'table'), mtime=None)

    label4 = Label(doc_id=doc2.doc_id, id='label4', kind=('content', 'figure'),
                   mtime=None)
    label5 = Label(doc_id=doc2.doc_id, id='label5', kind=('content', 'figure'),
                   mtime=None)
    label6 = TableLabel(doc_id=doc2.doc_id, id='label6',
                        kind=('content', 'table'), mtime=None)

    # 1. Try setting the local_order and global_order of the labels.
    #    First, try it by excluding table labels
    order_labels(registered_labels=[label1, label2, label3, label4, label5,
                                    label6],
                 exclude_labels=TableLabel)

    # Check the global_order
    assert label1.global_order == (1, 1)
    assert label2.global_order == (2, 2)
    assert label3.global_order is None  # Not assigned yet

    assert label4.global_order == (3, 3)
    assert label5.global_order == (4, 4)
    assert label6.global_order is None  # Not assigned yet

    # Check the local_order
    assert label1.local_order == (1, 1)
    assert label2.local_order == (2, 2)
    assert label3.local_order is None  # Not assigned yet

    assert label4.local_order == (1, 1)
    assert label5.local_order == (2, 2)
    assert label6.local_order is None  # Not assigned yet

    # 2. Try setting the local_order and global_order of the labels for all
    #    labels
    order_labels(registered_labels=[label1, label2, label3, label4, label5,
                                    label6])

    # Check the global_order
    assert label1.global_order == (1, 1)
    assert label2.global_order == (2, 2)
    assert label3.global_order == (3, 1)

    assert label4.global_order == (4, 3)
    assert label5.global_order == (5, 4)
    assert label6.global_order == (6, 2)

    # Check the local_order
    assert label1.local_order == (1, 1)
    assert label2.local_order == (2, 2)
    assert label3.local_order == (3, 1)

    assert label4.local_order == (1, 1)
    assert label5.local_order == (2, 2)
    assert label6.local_order == (3, 1)
