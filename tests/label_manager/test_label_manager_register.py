"""
Test the label manager register functionality.
"""
from collections import OrderedDict

import pytest

from disseminate.label_manager.types import ContentLabel, DocumentLabel
from disseminate.label_manager.register_orders import register_orders
from disseminate.label_manager.register_content_labels \
    import register_content_labels


def test_label_manager_register_orders(doctree):
    """Test the register_orders function."""

    # Create some labels
    context = doctree.context
    doc_id1, doc_id2, doc_id3 = doctree.doc_ids

    label1 = ContentLabel(doc_id=doc_id1, id='lbl1', title='title 1',
                          kind=('content', 'figure'))
    label2 = ContentLabel(doc_id=doc_id1, id='lbl2', title='title 2',
                          kind=('content', 'figure'))
    label3 = ContentLabel(doc_id=doc_id2, id='lbl3', title='title 3',
                          kind=('content', 'figure'))
    label4 = ContentLabel(doc_id=doc_id2, id='lbl4', title='title 4',
                          kind=('content', 'figure'))

    # 1. Try setting the order of the labels. First, try it by excluding table
    #    labels
    labels = OrderedDict()
    for label in [label1, label2, label3, label4]:
        labels[(label.doc_id, label.id)] = label

    register_orders(labels=labels, root_context=context)

    # Check the order
    assert label1.order == (1, 1)
    assert label2.order == (2, 2)
    assert label3.order == (3, 3)
    assert label4.order == (4, 4)

    # 2. Check that doc_ids no longer listed are removed
    label3.doc_id = 'missing'

    assert len(labels) == 4
    register_orders(labels=labels, root_context=context)
    assert len(labels) == 3
    assert set(labels.values()) == {label1, label2, label4}


def test_label_manager_register_orders_empty_kind(context):
    """Test the register_orders with labels that have an empty kind."""

    # Create some labels
    doc_id = context['doc_id']
    label1 = ContentLabel(doc_id=doc_id, id='label1', title='title 1', kind=())
    label2 = ContentLabel(doc_id=doc_id, id='label2', title='title 2', kind=())

    # 1. Try setting the order of the labels
    labels = OrderedDict()
    for label in [label1, label2]:
        labels[(label.doc_id, label.id)] = label
    register_orders(labels=labels, root_context=context)

    # Check the order
    assert label1.order == ()
    assert label2.order == ()


def test_label_manager_register_orders_reset(doctree):
    """Test the register_orders with label resets specified in the context."""

    # Specify the label_resets. This will reset section and subsection counters
    # whenever a chapter label is encountered.
    context = doctree.context
    context['label_resets']['chapter'] = {'section', 'subsection'}

    # Create some labels
    doc_id1, doc_id2, doc_id3 = doctree.doc_ids
    label1 = ContentLabel(doc_id=doc_id1, id='label1', title='chapter 1',
                          kind=('heading', 'chapter'))
    label2 = ContentLabel(doc_id=doc_id1, id='label2', title='section 1.1',
                          kind=('heading', 'section'))
    label3 = ContentLabel(doc_id=doc_id1, id='label3', title='chapter 2',
                          kind=('heading', 'chapter'))
    label4 = ContentLabel(doc_id=doc_id1, id='label4', title='section 2.1',
                          kind=('heading', 'section'))
    label5 = ContentLabel(doc_id=doc_id1, id='label5', title='section 2.2',
                          kind=('heading', 'section'))

    # 1. Try setting the order of the labels.
    labels = OrderedDict()
    for label in [label1, label2, label3, label4, label5]:
        labels[(label.doc_id, label.id)] = label
    register_orders(labels=labels, root_context=context)

    # Check the orders
    assert label1.order == (1, 1)  # Heading #1, Chapter #1
    assert label2.order == (2, 1)  # Heading #2, Section #1
    assert label3.order == (3, 2)  # Heading #3, Chapter #2
    assert label4.order == (4, 1)  # Heading #4, Section #1
    assert label5.order == (5, 2)  # Heading #5, Section #2

    # 2. Try an example with labels from different documents
    label3.doc_id = doc_id2
    label4.doc_id = doc_id2
    label5.doc_id = doc_id2

    register_orders(labels=labels, root_context=context)

    # Check the orders
    assert label1.order == (1, 1)  # Heading #1, Chapter #1
    assert label2.order == (2, 1)  # Heading #2, Section #1
    assert label3.order == (3, 2)  # Heading #3, Chapter #2
    assert label4.order == (4, 1)  # Heading #4, Section #1
    assert label5.order == (5, 2)  # Heading #5, Section #2

    # 3. Try it again, without the label_resets specified.
    del context['label_resets']['chapter']

    register_orders(labels=labels, root_context=context)

    # Check the orders
    assert label1.order == (1, 1)  # Heading #1, Chapter #1
    assert label2.order == (2, 1)  # Heading #2, Section #1
    assert label3.order == (3, 2)  # Heading #3, Chapter #2
    assert label4.order == (4, 2)  # Heading #4, Section #2
    assert label5.order == (5, 3)  # Heading #5, Section #3

    # 4. Try switch the labels doc_id order. This will place label1, label2
    #    after label3, label4, label5
    context['label_resets']['chapter'] = {'section', 'subsection'}
    label1.doc_id = doc_id3
    label2.doc_id = doc_id3

    register_orders(labels=labels, root_context=context)

    # Check the orders
    assert label3.order == (1, 1)  # Heading #1, Chapter #1 (doc_id2)
    assert label4.order == (2, 1)  # Heading #2, Section #1 (doc_id2)
    assert label5.order == (3, 2)  # Heading #3, Section #2 (doc_id2)
    assert label1.order == (4, 2)  # Heading #4, Chapter #1 (doc_id3)
    assert label2.order == (5, 1)  # Heading #5, Section #1 (doc_id3)


def test_label_manager_doc_register_orders(doctree):
    """Tests the label_manager reordering functionality with a doc."""

    # Setup the doctree
    doc1 = doctree
    doc2, doc3 = doc1.documents_list(only_subdocuments=True, recursive=True)
    doc_id1, doc_id2, doc_id3 = doctree.doc_ids

    # Generate a couple of short labels
    doc2.src_filepath.write_text("""
    @figure[id=fig:one-one]{@caption{figure 2-1}}
    @figure[id=fig:one-two]{@caption{figure 2-2}}
    """)

    doc3.src_filepath.write_text("""
    @figure[id=fig:two-one]{@caption{figure 3-1}}
    @figure[id=fig:two-two]{@caption{figure 3-2}}
    """)

    # Load the document and get the label manager
    doc1.load()
    label_man = doc1.context['label_manager']

    # There should be 7 labels altogether: 3 DocumentLabels, 4 ContentLabels
    labels = label_man.get_labels_by_kind()
    assert len(labels) == 7

    label1, label2, label3, label4, label5, label6, label7 = labels

    # Check the numbers and kind
    assert isinstance(label1, DocumentLabel)
    assert label1.kind == ('document', 'document-level-1')
    assert label1.order == (1, 1)
    assert label1.doc_id == 'test.dm'
    assert label1.id == 'doc:test-dm'

    assert isinstance(label2, DocumentLabel)
    assert label2.kind == ('document', 'document-level-2')
    assert label2.order == (2, 1)
    assert label2.doc_id == 'test2.dm'
    assert label2.id == 'doc:test2-dm'

    assert isinstance(label3, ContentLabel)
    assert label3.kind == ('caption', 'figure',)
    assert label3.order == (1, 1)
    assert label3.doc_id == 'test2.dm'
    assert label3.id == 'fig:one-one'

    assert isinstance(label4, ContentLabel)
    assert label4.kind == ('caption', 'figure',)
    assert label4.order == (2, 2)
    assert label4.doc_id == 'test2.dm'
    assert label4.id == 'fig:one-two'

    assert isinstance(label5, DocumentLabel)
    assert label5.kind == ('document', 'document-level-2')
    assert label5.order == (3, 2)
    assert label5.doc_id == 'test3.dm'
    assert label5.id == 'doc:test3-dm'

    assert isinstance(label6, ContentLabel)
    assert label6.kind == ('caption', 'figure',)
    assert label6.order == (3, 3)
    assert label6.doc_id == 'test3.dm'
    assert label6.id == 'fig:two-one'

    assert isinstance(label7, ContentLabel)
    assert label7.kind == ('caption', 'figure',)
    assert label7.order == (4, 4)
    assert label7.doc_id == 'test3.dm'
    assert label7.id == 'fig:two-two'

    # Now reset the labels for the second document. The
    # corresponding labels should also disappear, 4 labels for doc2 and doc3.
    label_man.reset(doc_ids=doc_id2)

    labels = label_man.get_labels_by_kind()
    assert len(labels) == 4
    label1, label5, label6, label7 = labels

    # Check the labels
    # Check the numbers and kind
    assert isinstance(label1, DocumentLabel)
    assert label1.kind == ('document', 'document-level-1')
    assert label1.order == (1, 1)

    assert isinstance(label5, DocumentLabel)
    assert label5.kind == ('document', 'document-level-2')
    assert label5.order == (2, 1)

    assert isinstance(label6, ContentLabel)
    assert label6.kind == ('caption', 'figure',)
    assert label6.order == (1, 1)

    assert isinstance(label7, ContentLabel)
    assert label7.kind == ('caption', 'figure',)
    assert label7.order == (2, 2)

    # delete the subdocuments, and the labels should be removed
    # Clear the sub-documents first
    doc1.src_filepath.write_text("""
    """)
    doc1.load()

    # There are no subdocuments
    assert (len(doc1.documents_list(only_subdocuments=True, recursive=True)) ==
            0)

    # There should only be 1 DocumentLabel for the root document (doc_id1)
    assert len(label_man.get_labels_by_kind(doc_id=doc_id1)) == 1
    assert len(label_man.get_labels_by_kind(doc_id=doc_id2)) == 0
    assert len(label_man.get_labels_by_kind(doc_id=doc_id3)) == 0


def test_label_manager_register_content_labels_part():
    """Test the register_content_labels function with 'part' labels."""

    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'part'),
                          title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'chapter'),
                          title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a', kind=('heading', 'section'),
                          title='a.a.a')
    label4 = ContentLabel(doc_id='a', id='a.a.a.a',
                          kind=('heading', 'subsection'),
                          title='a.a.a.a')

    # Give the labels mock orders (usually set by the register_label_orders)
    label1.order = (1, 1)
    label2.order = (2, 1)
    label3.order = (3, 1)
    label4.order = (4, 1)

    # Register the content labels labels
    labels = OrderedDict()
    for label in [label1, label2, label3, label4]:
        labels[(label.doc_id, label.id)] = label
    register_content_labels(labels=labels)

    # Check the values of the labels
    assert label1.part_label == label1
    assert label1.chapter_label is None
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.subsubsection_label is None
    assert label1.part_number == 1
    assert label1.part_title == 'a'
    assert label1.chapter_number == ''
    assert label1.chapter_title == ''
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''
    assert label1.tree_number == '1'

    assert label2.part_label == label1
    assert label2.chapter_label == label2
    assert label2.section_label is None
    assert label2.subsection_label is None
    assert label2.subsubsection_label is None
    assert label2.part_number == 1
    assert label2.part_title == 'a'
    assert label2.chapter_number == 1
    assert label2.chapter_title == 'a.a'
    assert label2.section_number == ''
    assert label2.section_title == ''
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''
    assert label2.tree_number == '1.1'

    assert label3.part_label == label1
    assert label3.chapter_label == label2
    assert label3.section_label == label3
    assert label3.subsection_label is None
    assert label3.subsubsection_label is None
    assert label3.part_number == 1
    assert label3.part_title == 'a'
    assert label3.chapter_number == 1
    assert label3.chapter_title == 'a.a'
    assert label3.section_number == 1
    assert label3.section_title == 'a.a.a'
    assert label3.subsection_number == ''
    assert label3.subsection_title == ''
    assert label3.tree_number == '1.1.1'

    assert label4.part_label == label1
    assert label4.chapter_label == label2
    assert label4.section_label == label3
    assert label4.subsection_label == label4
    assert label4.subsubsection_label is None
    assert label4.part_number == 1
    assert label4.part_title == 'a'
    assert label4.chapter_number == 1
    assert label4.chapter_title == 'a.a'
    assert label4.section_number == 1
    assert label4.section_title == 'a.a.a'
    assert label4.subsection_number == 1
    assert label4.subsection_title == 'a.a.a.a'
    assert label4.tree_number == '1.1.1.1'


def test_label_manager_register_content_labels_chapter():
    """Test the register_content_labels function with 'chapter' labels."""

    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'chapter'),
                          title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'section'),
                          title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a',
                          kind=('heading', 'subsection'), title='a.a.a')
    label4 = ContentLabel(doc_id='a', id='a.a.a.a',
                          kind=('heading', 'subsubsection'), title='a.a.a.a')

    # Give the labels mock orders (usually set by the register_label_orders)
    label1.order = (1, 1)
    label2.order = (2, 1)
    label3.order = (3, 1)
    label4.order = (4, 1)

    # Process the labels
    labels = OrderedDict()
    for label in [label1, label2, label3, label4]:
        labels[(label.doc_id, label.id)] = label
    register_content_labels(labels=labels)

    # Check the values of the labels
    assert label1.part_label is None
    assert label1.chapter_label == label1
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.subsubsection_label is None
    assert label1.part_number == ''
    assert label1.part_title == ''
    assert label1.chapter_number == 1
    assert label1.chapter_title == 'a'
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''
    assert label1.tree_number == '1'

    assert label2.part_label is None
    assert label2.chapter_label == label1
    assert label2.section_label == label2
    assert label2.subsection_label is None
    assert label2.subsubsection_label is None
    assert label2.part_number == ''
    assert label2.part_title == ''
    assert label2.chapter_number == 1
    assert label2.chapter_title == 'a'
    assert label2.section_number == 1
    assert label2.section_title == 'a.a'
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''
    assert label2.tree_number == '1.1'

    assert label3.part_label is None
    assert label3.chapter_label == label1
    assert label3.section_label == label2
    assert label3.subsection_label == label3
    assert label3.subsubsection_label is None
    assert label3.part_number == ''
    assert label3.part_title == ''
    assert label3.chapter_number == 1
    assert label3.chapter_title == 'a'
    assert label3.section_number == 1
    assert label3.section_title == 'a.a'
    assert label3.subsection_number == 1
    assert label3.subsection_title == 'a.a.a'
    assert label3.tree_number == '1.1.1'

    assert label4.part_label is None
    assert label4.chapter_label == label1
    assert label4.section_label == label2
    assert label4.subsection_label == label3
    assert label4.subsubsection_label == label4
    assert label4.part_number == ''
    assert label4.part_title == ''
    assert label4.chapter_number == 1
    assert label4.chapter_title == 'a'
    assert label4.section_number == 1
    assert label4.section_title == 'a.a'
    assert label4.subsection_number == 1
    assert label4.subsection_title == 'a.a.a'
    assert label4.tree_number == '1.1.1.1'
