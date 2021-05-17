"""
Test the label manager.
"""
import pytest

from disseminate.label_manager import LabelManager, ContentLabel, DocumentLabel
from disseminate.label_manager.exceptions import DuplicateLabel, LabelNotFound


def test_label_manager_add_label(context):
    """Test the add_label method."""
    label_man = LabelManager(root_context=context)

    label1 = label_man.add_content_label(id='fig:one', kind='figures',
                                         title='first fig', context=context)
    label2 = label_man.add_document_label(id='test2.dm::second-doc',
                                          kind='document', title="Second doc",
                                          context=context)

    # Try duplicates
    with pytest.raises(DuplicateLabel):
        # Matching ids
        label_man.add_content_label(id='fig:one', kind='figures',
                                    title='first fig', context=context)
    with pytest.raises(DuplicateLabel):
        # Matching doc_id and label_id
        label_man.add_document_label(id='test2.dm::second-doc',
                                     kind='document', title="Second doc",
                                     context=context)

    # Check the labels dict
    assert len(label_man.labels) == 2
    assert label_man.labels[('test.dm', 'fig:one')] == label1
    assert label_man.labels[('test2.dm', 'second-doc')] == label2


def test_label_manager_reset(context):
    """Test the reset method."""
    label_man = LabelManager(root_context=context)

    def create_labels():
        label_man.reset()
        label_man.add_content_label(id='fig:one', kind='figures', title='1',
                                    context=context)
        label_man.add_content_label(id='test.dm::fig:two', kind='figures',
                                    title='2', context=context)
        label_man.add_document_label(id='test2.dm::second-doc',
                                     kind='document', title="3",
                                     context=context)
        label_man.add_content_label(id='test2.dm::fig:three', kind='figure',
                                    title="4", context=context)

    # 1. Test resetting all labels
    create_labels()
    assert len(label_man.labels) == 4  # 4 labels
    label_man.reset()
    assert len(label_man.labels) == 0  # all labels removed

    # 2. Try removing labels for one doc_id only
    create_labels()
    label_man.reset(doc_ids='test2.dm')
    assert len(label_man.labels) == 2  # 2 label remaining
    assert all(label.doc_id == 'test.dm'
               for label in label_man.labels.values())


def test_label_manager_get_label(doctree):
    """Test the get_label method."""
    context = doctree.context  # doctree doc_ids: test.dm, test2.dm, test3.dm

    label_man = LabelManager(root_context=context)

    label1 = label_man.add_content_label(id='fig:one', kind='figures',
                                         title='first fig', context=context)
    label2 = label_man.add_document_label(id='test2.dm::second-doc',
                                          kind='document', title="Second doc",
                                          context=context)
    label3 = label_man.add_content_label(id='test3.dm::fig:one',
                                         kind='figures', title='first fig',
                                         context=context)

    # Get label with doc_id
    assert label_man.get_label('test.dm::fig:one') == label1
    assert label_man.get_label('test2.dm::second-doc') == label2
    assert label_man.get_label('test3.dm::fig:one') == label3

    # Get label without doc_id. The label3 has a duplicate label_id;
    # the first label (label1) will be returned
    assert label_man.get_label('fig:one') == label1
    assert label_man.get_label('second-doc') == label2

    # Try cases with invalid doc_id, label_id, which should return
    # LabelNotFound
    for id in ('test.dm::fig:two', 'test4.dm::fig:one', 'fig:three'):
        with pytest.raises(LabelNotFound):
            label_man.get_label(id)


def test_label_manager_get_labels_by_id(doctree):
    """Test the get_labels_by_id method."""
    context = doctree.context  # doctree doc_ids: test.dm, test2.dm, test3.dm
    label_man = LabelManager(root_context=context)

    label1 = label_man.add_content_label(id='fig:one', kind='figures',
                                         title='first fig', context=context)
    label2 = label_man.add_document_label(id='test2.dm::second-doc',
                                          kind='document', title="Second doc",
                                          context=context)
    label3 = label_man.add_content_label(id='test3.dm::fig:one',
                                         kind='figures', title='first fig',
                                         context=context)

    # Try different ids with doc_id
    assert label_man.get_labels_by_id(ids='test.dm::fig:one') == [label1]
    assert (label_man.get_labels_by_id(ids=('test.dm::fig:one',
                                            'test3.dm::fig:one')) ==
            [label1, label3])

    # Try different ids without doc_ids
    assert (label_man.get_labels_by_id(ids=('fig:one', 'second-doc')) ==
            [label1, label2])


def test_label_manager_get_labels_by_kind(context):
    """Test the get_labels_by_kind method."""
    label_man = LabelManager(root_context=context)

    label_man.add_content_label(id='fig:one', kind=('caption', 'figure'),
                                title='first fig', context=context)
    label_man.add_content_label(id='fig:two', kind=('caption', 'figure'),
                                title='first fig', context=context)

    # Retrieve the labels.
    labels = label_man.get_labels_by_kind()
    assert len(label_man.labels) == 2
    assert len(labels) == 2

    # Get labels by doc_id
    labels = label_man.get_labels_by_kind(doc_id=context['doc_id'])
    assert len(labels) == 2

    # Filter by kind
    labels = label_man.get_labels_by_kind(kinds='figure')
    assert len(labels) == 2
    assert labels[0].kind == ('caption', 'figure',)
    assert labels[1].kind == ('caption', 'figure',)

    labels = label_man.get_labels_by_kind(kinds=('figure', 'h1'))
    assert len(labels) == 2
    assert labels[0].kind == ('caption', 'figure',)
    assert labels[1].kind == ('caption', 'figure',)

    # There are no labels with a kind 'h1', so no labels are returned
    labels = label_man.get_labels_by_kind(kinds=('h1',))
    assert len(labels) == 0


def test_label_manager_doc_basic_labels(doc):
    """Tests the basic label_manager functionality with docs."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    doc.src_filepath.write_text("""
    @figure{@caption{figure 1}}
    @figure{@caption{figure 2}}
    """)
    doc.load()

    # The DocumentLabel and 2 Content labels have been registered
    assert len(label_man.labels) == 3

    # Getting labels returns only the document label and resets the
    # collected labels
    doc_id = doc.doc_id
    labels = label_man.get_labels_by_kind(doc_id=doc_id)  # register labels
    assert len(labels) == 3

    # There should be 2 ContentLabels (fig:one, fig:two) and 1 DocumentLabel
    assert len([label for label in labels
                if isinstance(label, ContentLabel)]) == 2
    assert len([label for label in labels
                if isinstance(label, DocumentLabel)]) == 1

    # Now check the labels themselves
    label1 = labels[0]  # document label
    label2 = labels[1]  # figure label
    label3 = labels[2]  # figure label

    assert all(label.doc_id == 'test.dm' for label in labels)
    assert label1.id == 'doc:test-dm'
    assert label2.id == 'caption-2491d216e2'
    assert label3.id == 'caption-c5939d5d3a'

    assert label1.kind == ('document', 'document-level-1')
    assert label2.kind == ('caption', 'figure')
    assert label3.kind == ('caption', 'figure',)

    assert label1.order == (1, 1)
    assert label2.order == (1, 1)
    assert label3.order == (2, 2)

    # Generate a couple of specific labels
    label_man.add_content_label(id='fig:image1', kind='figure', title='image1',
                                context=doc.context)
    label_man.add_content_label(id='fig:image2', kind='figure', title='image1',
                                context=doc.context)

    # Getting the labels will register the new labels
    labels = label_man.get_labels_by_kind(doc_id=doc_id)  # registers labels
    assert len(labels) == 5

    # Make sure the labels are properly assigned: 2 ContentLabels. The
    # DocumentLabel hasn't been registered because the document's
    # load/reset_context methods haven't been executed
    assert len([label for label in labels
                if isinstance(label, ContentLabel)]) == 4

    # Check the new labels
    label3 = label_man.get_label('fig:image1')
    label4 = label_man.get_label('fig:image2')

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label3.order == (3,)
    assert label4 == label_man.get_label('fig:image2')
    assert label4.order == (4,)


def test_label_manager_doc_updates(doc, wait):
    """Test updates to existing labels for the label_manager."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a generic labels
    doc.src_filepath.write_text("""
    @figure[id=fig:one]{@caption{figure 1}}
    """)
    doc.load()

    assert len(label_man.labels) == 2  # DocumentLabel and ContentLabel
    label = label_man.get_label(id="fig:one")
    assert label.doc_id == 'test.dm'
    assert label.id == 'fig:one'
    assert label.title == 'figure 1'

    # Try changing the label
    wait()  # offset time for filesystem
    doc.src_filepath.write_text("""
        @figure[id=fig:one]{@caption{figure one}}
        """)
    doc.load()

    assert len(label_man.labels) == 2  # DocumentLabel and ContentLabel
    new_label = label_man.get_label(id="fig:one")
    assert new_label.doc_id == 'test.dm'
    assert new_label.id == 'fig:one'
    assert new_label.title == 'figure one'
