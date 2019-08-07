"""
Test the OrderLabels class
"""
from disseminate.label_manager.processors import OrderLabels
from disseminate.label_manager.types import Label


def test_order_labels_processor(doctree):
    """Test the OrderLabels label processor."""

    # Retrieve the documents
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)

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

    # Setup the label processor. Add the 'TableLabel' to the excludes set
    # to test that these aren't assigned.
    processor = OrderLabels(context=doc1.context)
    processor.excludes = {TableLabel}

    # 1. Try setting the order of the labels. First, try it by excluding table
    #    labels
    registered_labels = [label1, label2, label3, label4, label5, label6]
    processor(registered_labels=registered_labels)

    # Check the order
    assert label1.order == (1, 1)
    assert label2.order == (2, 2)
    assert label3.order is None  # Not assigned yet
    assert label4.order == (3, 3)
    assert label5.order == (4, 4)
    assert label6.order is None  # Not assigned yet

    # 2. Try setting the order of the labels for all labels
    processor.excludes = None
    registered_labels = [label1, label2, label3, label4, label5, label6]
    processor(registered_labels=registered_labels)

    # Check the order
    assert label1.order == (1, 1)
    assert label2.order == (2, 2)
    assert label3.order == (3, 1)
    assert label4.order == (4, 3)
    assert label5.order == (5, 4)
    assert label6.order == (6, 2)


def test_order_labels_processor_empty_kind(doc):
    """Test the OrderLabels label processor with labels that have an empty
    kind."""

    # Make a test label class
    class TableLabel(Label):
        pass

    # Create some labels
    label1 = Label(doc_id=doc.doc_id, id='label1', kind=(), mtime=None)
    label2 = Label(doc_id=doc.doc_id, id='label2', kind=(), mtime=None)

    # Setup the label processor. Add the 'TableLabel' to the excludes set
    # to test that these aren't assigned.
    processor = OrderLabels(context=doc.context)
    processor.excludes = {TableLabel}

    # 1. Try setting the order of the labels. First, try it by excluding table
    #    labels
    registered_labels = [label1, label2]
    processor(registered_labels=registered_labels)

    # Check the order
    assert label1.order == ()
    assert label2.order == ()


def test_order_labels_reset(doctree):
    """Test the OrderLabels label processor with label resets specified in 
    the context."""

    # Retrieve the documents
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)

    # Specify the label_resets
    doc1.context['label_resets']['chapter'] = {'section', 'subsection'}

    # Create some labels
    label1 = Label(doc_id=doc1.doc_id, id='label1', kind=('heading', 'chapter'),
                   mtime=None)
    label2 = Label(doc_id=doc1.doc_id, id='label2', kind=('heading', 'section'),
                   mtime=None)
    label3 = Label(doc_id=doc2.doc_id, id='label4', kind=('heading', 'chapter'),
                   mtime=None)
    label4 = Label(doc_id=doc2.doc_id, id='label4', kind=('heading', 'section'),
                   mtime=None)
    label5 = Label(doc_id=doc2.doc_id, id='label5', kind=('heading', 'section'),
                   mtime=None)

    # Setup the label processor.
    processor = OrderLabels(context=doc1.context)

    # 1. Try setting the order of the labels. First, try it by excluding table
    #    labels
    registered_labels = [label1, label2, label3, label4, label5]
    processor(registered_labels=registered_labels)

    # Check the orders
    assert label1.order == (1, 1)  # Heading #1, Chapter #1
    assert label2.order == (2, 1)  # Heading #2, Section #1
    assert label3.order == (3, 2)  # Heading #3, Chapter #2
    assert label4.order == (4, 1)  # Heading #4, Section #1
    assert label5.order == (5, 2)  # Heading #5, Section #2

    # 2. Try it again, without the label_resets specified.
    del doc1.context['label_resets']['chapter']

    registered_labels = [label1, label2, label3, label4, label5]
    processor(registered_labels=registered_labels)

    # Check the orders
    assert label1.order == (1, 1)  # Heading #1, Chapter #1
    assert label2.order == (2, 1)  # Heading #2, Section #1
    assert label3.order == (3, 2)  # Heading #3, Chapter #2
    assert label4.order == (4, 2)  # Heading #4, Section #2
    assert label5.order == (5, 3)  # Heading #5, Section #3
