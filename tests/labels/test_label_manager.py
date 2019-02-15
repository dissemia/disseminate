"""
Test the label manager.
"""
from disseminate import Document
from disseminate.labels import ContentLabel, HeadingLabel


def test_label_manager_basic_labels(tmpdir):
    """Tests the basic functionality of labels with the label manager."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
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
    labels = label_man.get_labels(context=doc.context)  # register labels
    assert doc.src_filepath not in label_man.collected_labels
    assert len(labels) == 3

    # Make sure the labels are properly assigned as ContentLabels
    assert all(isinstance(i, ContentLabel) for i in labels)

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

    assert label1.local_order == (1, 1)
    assert label1.global_order == (1, 1)
    assert label2.local_order == (1,)
    assert label2.global_order == (1,)
    assert label3.local_order == (2,)
    assert label3.global_order == (2,)

    assert label1.mtime == doc.mtime
    assert label2.mtime == doc.mtime
    assert label3.mtime == doc.mtime

    # Generate a couple of specific labels
    label_man.add_content_label(id='fig:image1',kind='figure', title='image1',
                                context=doc.context)
    label_man.add_content_label(id='fig:image2', kind='figure', title='image1',
                                context=doc.context)

    # Check that these were placed in the collected labels
    assert len(label_man.collected_labels[doc.doc_id]) == 2

    # Getting the labels will register the new labels, removing the old labels,
    # and leaving the 2 new labels
    labels = label_man.get_labels(context=doc.context)  # registers labels
    assert len(labels) == 2
    labels = label_man.get_labels(context=doc.context)
    assert len(labels) == 2

    # Make sure the labels are properly assigned as ContentLabels
    assert all(isinstance(i, ContentLabel) for i in labels)

    # Make sure that the get_labels method has registered the labels
    assert len(label_man.collected_labels) == 0
    assert len(label_man.labels) == 2

    label3 = label_man.get_label('fig:image1')
    label4 = label_man.get_label('fig:image2')

    assert labels == [label3, label4]

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label3.local_order == (1,)
    assert label3.global_order == (1,)
    assert label4 == label_man.get_label('fig:image2')
    assert label4.local_order == (2,)
    assert label4.global_order == (2,)

    assert label3.mtime == doc.mtime
    assert label4.mtime == doc.mtime


def test_label_manager_updates(tmpdir):
    """Test updates to existing labels for the label_manager."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
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


def test_label_manager_get_labels(tmpdir, context_cls):
    """Test the get_labels method."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 1",
                                context=doc.context)
    label_man.add_content_label(id="fig:two", kind='figure',title="figure 2",
                                context=doc.context)

    # Get all labels and register them. There should only be 3 registered
    # labels: the document's label and the 3 figure labels
    assert len(label_man.collected_labels) == 1
    labels = label_man.get_labels()  # registers the labels
    assert len(label_man.labels) == 3
    assert len(labels) == 3

    # Get labels for this document
    labels = label_man.get_labels(context=doc.context)
    assert len(labels) == 3

    # Get labels for another document (a string is used since the type is not
    # checked)
    other = context_cls(doc_id='other')
    labels = label_man.get_labels(context=other)
    assert labels == []

    # Filter by kind
    labels = label_man.get_labels(kinds='figure')
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    labels = label_man.get_labels(kinds=['figure', 'h1'])
    assert len(labels) == 2
    assert labels[0].kind == ('figure',)
    assert labels[1].kind == ('figure',)

    labels = label_man.get_labels(kinds=['h1'])
    assert len(labels) == 0


def test_label_manager_label_reordering(tmpdir):
    """Tests the reordering of labels when labels are registered."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    # Create a sub-document
    src_filepath.write("""---
    include:
      tmp2.dm
      ---""")
    src_filepath2 = tmpdir.join('src').join('tmp2.dm')
    src_filepath2.write("")

    doc = Document(str(src_filepath), str(tmpdir))
    doc2 = list(doc.subdocuments.values())[0]

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of short labels
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 1-1",
                                context=doc.context)
    label_man.add_content_label(id="fig:two", kind='figure', title="figure 1-2",
                                context=doc.context)

    # Generate a couple of short labels for the sub-document
    label_man.add_content_label(id="fig:one", kind='figure', title="figure 2-1",
                                context=doc2.context)
    label_man.add_content_label(id="fig:two", kind='figure', title="figure 2-2",
                                context=doc2.context)

    # Get and register the labels. This will include 2 document labels and 4
    # figure labels
    for i in range(2):
        labels = label_man.get_labels()
        assert len(labels) == 6

        label1, label2, label3, label4, label5, label6 = labels

        # Check the numbers and kind
        assert isinstance(label1, HeadingLabel)
        assert label1.kind == ('document', 'document-level-1')
        assert label1.local_order == (1, 1)
        assert label1.global_order == (1, 1)

        assert isinstance(label2, ContentLabel)
        assert label2.kind == ('figure',)
        assert label2.local_order == (1,)
        assert label2.global_order == (1,)

        assert isinstance(label3, ContentLabel)
        assert label3.kind == ('figure',)
        assert label3.local_order == (2,)
        assert label3.global_order == (2,)

        assert isinstance(label4, HeadingLabel)
        assert label4.kind == ('document', 'document-level-2')
        assert label4.local_order == (1, 1)
        assert label4.global_order == (2, 1)

        assert isinstance(label5, ContentLabel)
        assert label5.kind == ('figure',)
        assert label5.local_order == (1,)
        assert label5.global_order == (3,)

        assert isinstance(label6, ContentLabel)
        assert label6.kind == ('figure',)
        assert label6.local_order == (2,)
        assert label6.global_order == (4,)

    # Now reset the labels for the first document. The
    # corresponding labels should also disappear, leaving 3 labels.
    label_man.reset(context=doc.context)

    labels = label_man.get_labels()
    assert len(labels) == 3
    label4, label5, label6 = labels

    # Check the labels
    assert label4.kind == ('document', 'document-level-2')
    assert label4.local_order == (1, 1)
    assert label4.global_order == (1, 1)

    assert label5.kind == ('figure',)
    assert label5.local_order == (1,)
    assert label5.global_order == (1,)

    assert label6.kind == ('figure',)
    assert label6.local_order == (2,)
    assert label6.global_order == (2,)

    # Now delete the 2nd document and the labels should be removed too.
    doc2 = None
    doc.subdocuments.clear()
    assert len(label_man.get_labels()) == 0
