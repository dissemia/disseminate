"""
Test the label manager.
"""
import pathlib

import pytest

from disseminate.label_manager import ContentLabel, DocumentLabel
from disseminate.document import Document


def test_label_manager_basic_labels(doc):
    """Tests the basic functionality of labels with the label manager."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    doc.src_filepath.write_text("""
    @figure{@caption{figure 1}}
    @figure{@caption{figure 2}}
    """)
    doc.load()
    # label_man.add_content_label(id='fig:one', kind='figure', title="figure 1",
    #                             context=doc.context)
    # label_man.add_content_label(id='fig:two', kind='figure', title="figure 2",
    #                             context=doc.context)

    # The DocumentLabel and 2 Content labels have been registered
    assert len(label_man.labels) == 3

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
    assert label2.kind == ('caption', 'figure')
    assert label3.kind == ('caption', 'figure',)

    assert label1.order == (1, 1)
    assert label2.order == (1, 1)
    assert label3.order == (2, 2)

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


def test_label_manager_updates(doc, wait):
    """Test updates to existing labels for the label_manager."""

    # Get the label manager from the document
    label_man = doc.context['label_manager']

    # Generate a generic labels
    doc.src_filepath.write_text("""
    @figure[id=fig:one]{@caption{figure 1}}
    """)
    doc.load()
    label = label_man.get_label(id="fig:one")
    assert label.title == 'figure 1'

    # Try changing the label
    wait()  # offset time for filesystem
    doc.src_filepath.write_text("""
        @figure[id=fig:one]{@caption{figure one}}
        """)
    doc.load()

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
    doc2.src_filepath.write_text("""
    @figure[id=fig:one]{@caption{figure 1}}
    @figure[id=fig:two]{@caption{figure 2}}
    """)
    for doc in (doc1, doc2, doc3):
        doc.load()

    # Retrieve the labels. There should only be 5 registered
    # labels: 3 DocumentLabels, 2 ContentLabels
    labels = label_man.get_labels()  # registers the labels
    assert len(label_man.labels) == 5
    assert len(labels) == 5

    # Get labels for each of the documents document
    doc_id1 = doc1.doc_id
    labels1 = label_man.get_labels(doc_id=doc_id1)
    assert len(labels1) == 1  # 1 DocumentLabel

    doc_id2 = doc2.doc_id
    labels2 = label_man.get_labels(doc_id=doc_id2)
    assert len(labels2) == 3  # 1 DocumentLabel, 2 ContentLabels

    doc_id3 = doc3.doc_id
    labels3 = label_man.get_labels(doc_id=doc_id3)
    assert len(labels3) == 1  # 1 DocumentLabel

    # Filter by kind
    labels = label_man.get_labels(kinds='figure')
    assert len(labels) == 2
    assert labels[0].kind == ('caption', 'figure',)
    assert labels[1].kind == ('caption', 'figure',)

    labels = label_man.get_labels(kinds=('figure', 'h1'))
    assert len(labels) == 2
    assert labels[0].kind == ('caption', 'figure',)
    assert labels[1].kind == ('caption', 'figure',)

    # There are no labels with a kind 'h1', so no labels are returned
    labels = label_man.get_labels(kinds=('h1',))
    assert len(labels) == 0


def test_label_manager_label_reordering(tmpdir):
    """Tests the reordering of labels when labels are registered."""

    # Create a document tree. A document tree is created here, rather than
    # use the doctree fixture, because this function needs to own the document
    # tree to properly call the __del__ function of all created documents.
    target_root = pathlib.Path(tmpdir)
    src_dir = pathlib.Path(tmpdir) / 'src'
    src_dir.mkdir()

    src_filepath1 = src_dir / 'test1.dm'
    src_filepath2 = src_dir / 'test2.dm'
    src_filepath3 = src_dir / 'test3.dm'

    src_filepath1.write_text("""
    ---
    include:
      test2.dm
      test3.dm
    ---
    """)
    src_filepath2.touch()
    src_filepath3.touch()

    doc1 = Document(src_filepath1, target_root=target_root)

    # Get the label manager from the document and the documents in the tree
    doc2, doc3 = doc1.documents_list(only_subdocuments=True)
    label_man = doc1.context['label_manager']

    # Generate a couple of short labels
    doc2.src_filepath.write_text("""
    @figure[id=fig:one-one]{@caption{figure 2-1}}
    @figure[id=fig:one-two]{@caption{figure 2-2}}
    """)
    doc2.load()

    doc3.src_filepath.write_text("""
        @figure[id=fig:two-one]{@caption{figure 3-1}}
        @figure[id=fig:two-two]{@caption{figure 3-2}}
        """)
    doc3.load()
    # Get the labels.
    for i in range(2):
        # There should be 7 labels altogether: 3 DocumentLabels, 4 ContentLabels
        labels = label_man.get_labels()
        assert len(labels) == 7

        label1, label2, label3, label4, label5, label6, label7 = labels

        # Check the numbers and kind
        assert isinstance(label1, DocumentLabel)
        assert label1.kind == ('document', 'document-level-1')
        assert label1.order == (1, 1)

        assert isinstance(label2, DocumentLabel)
        assert label2.kind == ('document', 'document-level-2')
        assert label2.order == (2, 1)

        assert isinstance(label3, ContentLabel)
        assert label3.kind == ('caption', 'figure',)
        assert label3.order == (1, 1)

        assert isinstance(label4, ContentLabel)
        assert label4.kind == ('caption', 'figure',)
        assert label4.order == (2, 2)

        assert isinstance(label5, DocumentLabel)
        assert label5.kind == ('document', 'document-level-2')
        assert label5.order == (3, 2)

        assert isinstance(label6, ContentLabel)
        assert label6.kind == ('caption', 'figure',)
        assert label6.order == (3, 3)

        assert isinstance(label7, ContentLabel)
        assert label7.kind == ('caption', 'figure',)
        assert label7.order == (4, 4)

    # Now reset the labels for the second document. The
    # corresponding labels should also disappear, 4 labels for doc2 and doc3.
    label_man.reset(context=doc2.context)

    labels = label_man.get_labels()
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

    # delete the documents, and the labels should be removed
    doc_id1 = doc1.doc_id
    doc_id2 = doc2.doc_id
    doc_id3 = doc3.doc_id

    # Clear the sub-documents first
    doc1.subdocuments.clear()
    del doc2, doc3

    assert len(label_man.get_labels(doc_id=doc_id2)) == 0
    assert len(label_man.get_labels(doc_id=doc_id3)) == 0

    # Clear the root document. Getting the labels at this point will raise an
    # attribute error because the label manager get_labels method checks for
    # a root_document in the context, and the context no longer exists.
    del doc1

    with pytest.raises(AttributeError):
        label_man.get_labels()
