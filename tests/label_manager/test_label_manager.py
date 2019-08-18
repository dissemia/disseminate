"""
Test the label manager.
"""
from disseminate.label_manager import ContentLabel, DocumentLabel


def test_label_manager_basic_labels(doc):
    """Tests the basic functionality of labels with the label manager."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label_man.add_content_label(id='fig:one', kind='figure', title="figure 1",
                                context=doc.context)
    label_man.add_content_label(id='fig:two', kind='figure', title="figure 2",
                                context=doc.context)

    # These are collected labels right now, and aren't registered. Labels
    # have to be retrieved with get_labels to register them.
    assert len(label_man.labels) == 0
    assert len(label_man.collected_labels[doc.doc_id]) == 3

    # Getting labels returns only the document label and resets the
    # collected labels
    doc_id = doc.doc_id
    labels = label_man.get_labels(doc_id=doc_id)  # register labels
    assert doc.src_filepath not in label_man.collected_labels
    assert len(labels) == 3

    # There should be 2 ContentLabels (fig:one, fig:two) and 1 DocumentLabel
    assert len([l for l in labels if isinstance(l, ContentLabel)]) == 2
    assert len([l for l in labels if isinstance(l, DocumentLabel)]) == 1

    # Make sure that the get_labels method has registered the labels
    assert len(label_man.collected_labels) == 0
    assert len(label_man.labels) == 3

    # Now check the labels themselves
    label1 = labels[0]  # document label
    label2 = labels[1]  # figure label
    label3 = labels[2]  # figure label

    assert label1.kind == ('document', 'document-level-1')
    assert label2.kind == ('figure',)
    assert label3.kind == ('figure',)

    assert label1.order == (1, 1)
    assert label2.order == (1,)
    assert label3.order == (2,)

    assert label1.mtime == doc.mtime
    assert label2.mtime == doc.mtime
    assert label3.mtime == doc.mtime

    # Generate a couple of specific labels
    label_man.add_content_label(id='fig:image1', kind='figure', title='image1',
                                context=doc.context)
    label_man.add_content_label(id='fig:image2', kind='figure', title='image1',
                                context=doc.context)

    # Check that these were placed in the collected labels
    assert len(label_man.collected_labels[doc.doc_id]) == 2

    # Getting the labels will register the new labels, removing the old labels,
    # and leaving the 2 new labels
    labels = label_man.get_labels(doc_id=doc_id)  # registers labels
    assert len(labels) == 2
    labels = label_man.get_labels(doc_id=doc_id)
    assert len(labels) == 2

    # Make sure the labels are properly assigned: 2 ContentLabels. The
    # DocumentLabel hasn't been registered because the document's
    # load/reset_context methods haven't been executed
    assert len([l for l in labels if isinstance(l, ContentLabel)]) == 2

    # Make sure that the get_labels method has registered the labels
    assert len(label_man.collected_labels) == 0
    assert len(label_man.labels) == 2

    label3 = label_man.get_label('fig:image1')
    label4 = label_man.get_label('fig:image2')

    assert labels == [label3, label4]

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label3.order == (1,)
    assert label4 == label_man.get_label('fig:image2')
    assert label4.order == (2,)

    assert label3.mtime == doc.mtime
    assert label4.mtime == doc.mtime


def test_label_manager_updates(doc):
    """Test updates to existing labels for the label_manager."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a generic labels
    label_man.add_content_label(id='fig:one', kind='figure', title="figure 1",
                                context=doc.context)

    label = label_man.get_label(id="fig:one")
    assert label.title == 'figure 1'

    # Try changing the label
    label_man.add_content_label(id='fig:one', kind='figure', title="figure one",
                                context=doc.context)

    new_label = label_man.get_label(id="fig:one")
    assert label == new_label  # the original label should be reused
    assert new_label.title == 'figure one'


def test_label_manager_get_labels(doctree):
    """Test the get_labels method."""

    # Get the label manager from the document and the documents in the tree
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)
    label_man = doc1.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 1",
                                context=doc1.context)
    label_man.add_content_label(id="fig:two", kind='figure',title="figure 2",
                                context=doc1.context)

    # The labels have been collected to this point--not registered. There
    # should be collected labels for the 3 documents.
    doc_id1 = doc1.doc_id
    doc_id2 = doc2.doc_id
    doc_id3 = doc3.doc_id

    # 2 ContentLabels, 1 DocumentLabel
    assert len(label_man.collected_labels[doc_id1]) == 3
    # 1 DocumentLabel
    assert len(label_man.collected_labels[doc_id2]) == 1
    # 1 DocumentLabel
    assert len(label_man.collected_labels[doc_id3]) == 1

    # Register and retrieve the labels. There should only be 5 registered
    # labels: 3 DocumentLabels, 2 ContentLabels
    labels = label_man.get_labels()  # registers the labels
    assert len(label_man.labels) == 5
    assert len(labels) == 5

    # Get labels for each of the documents document
    doc_id1 = doc1.doc_id
    labels1 = label_man.get_labels(doc_id=doc_id1)
    assert len(labels1) == 3

    doc_id2 = doc2.doc_id
    labels2 = label_man.get_labels(doc_id=doc_id2)
    assert len(labels2) == 1

    doc_id3 = doc3.doc_id
    labels3 = label_man.get_labels(doc_id=doc_id3)
    assert len(labels3) == 1

    # Filter by kind
    labels = label_man.get_labels(kinds='figure')
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    labels = label_man.get_labels(kinds=('figure', 'h1'))
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    # There are no labels with a kind 'h1', so no labels are returned
    labels = label_man.get_labels(kinds=('h1',))
    assert len(labels) == 0


def test_label_manager_label_reordering(doctree):
    """Tests the reordering of labels when labels are registered."""

    # Get the label manager from the document and the documents in the tree
    doc1 = doctree
    doc2, doc3 = doctree.documents_list(only_subdocuments=True)
    label_man = doc1.context['label_manager']

    # Generate a couple of short labels
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 1-1",
                                context=doc1.context)
    label_man.add_content_label(id="fig:two", kind='figure', title="figure 1-2",
                                context=doc1.context)

    # Generate a couple of short labels for the sub-document
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 2-1",
                                context=doc2.context)
    label_man.add_content_label(id="fig:two", kind='figure', title="figure 2-2",
                                context=doc2.context)

    # Get and register the labels. This will include 2 document labels and 4
    # figure labels
    for i in range(2):
        # There should be 7 labels altogether: 3 DocumentLabels, 4 ContentLabels
        labels = label_man.get_labels()
        assert len(labels) == 7

        label1, label2, label3, label4, label5, label6, label7 = labels

        # Check the numbers and kind
        assert isinstance(label1, DocumentLabel)
        assert label1.kind == ('document', 'document-level-1')
        assert label1.order == (1, 1)

        assert isinstance(label2, ContentLabel)
        assert label2.kind == ('figure',)
        assert label2.order == (1,)

        assert isinstance(label3, ContentLabel)
        assert label3.kind == ('figure',)
        assert label3.order == (2,)

        assert isinstance(label4, DocumentLabel)
        assert label4.kind == ('document', 'document-level-2')
        assert label4.order == (2, 1)

        assert isinstance(label5, ContentLabel)
        assert label5.kind == ('figure',)
        assert label5.order == (3,)

        assert isinstance(label6, ContentLabel)
        assert label6.kind == ('figure',)
        assert label6.order == (4,)

        assert isinstance(label7, DocumentLabel)
        assert label7.kind == ('document', 'document-level-2')
        assert label7.order == (3, 2)

    # Now reset the labels for the first document. The
    # corresponding labels should also disappear, 4 labels for doc2 and doc3.
    label_man.reset(context=doc1.context)

    labels = label_man.get_labels()
    assert len(labels) == 4
    label4, label5, label6, label7 = labels

    # Check the labels
    assert isinstance(label4, DocumentLabel)
    assert label4.kind == ('document', 'document-level-2')
    assert label4.order == (1, 1)

    assert isinstance(label5, ContentLabel)
    assert label5.kind == ('figure',)
    assert label5.order == (1,)

    assert isinstance(label6, ContentLabel)
    assert label6.kind == ('figure',)
    assert label6.order == (2,)

    assert isinstance(label7, DocumentLabel)
    assert label7.kind == ('document', 'document-level-2')
    assert label7.order == (2, 2)

    # Now delete the 2nd document and the labels should be removed too.
    doc1.subdocuments.clear()
    assert len(label_man.get_labels()) == 0
