"""
Tests the label manager and label classes.
"""
import pytest

from disseminate.labels import LabelNotFound
from disseminate import Document


def test_basic_labels(tmpdir):
    """Tests the basic functionality of labels."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label1 = label_man.add_label(document=doc, kind='figure')
    label2 = label_man.add_label(document=doc, kind='figure')

    # Try to get the labels. These are generic labels, which cannot be
    # retrieved.
    assert label1.id is None
    with pytest.raises(LabelNotFound):
        assert label1 == label_man.get_label(label1.id)

    # Generate a couple of specific labels
    label3 = label_man.add_label(document=doc, kind='figure', id='fig:image1')
    label4 = label_man.add_label(document=doc, kind='figure', id='fig:image2')

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label4 == label_man.get_label('fig:image2')


def test_get_labels(tmpdir):
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
    label1 = label_man.add_label(document=doc, kind='figure')
    label2 = label_man.add_label(document=doc, kind='figure')

    # Get all labels. There should be 3: 1 for the document, 2 for the figures
    labels = label_man.get_labels()
    assert len(labels) == 3

    # Get labels for this document
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 3

    # Get labels for another document (a string is used since the type is not
    # checked)
    labels = label_man.get_labels(document='other')
    assert labels == []

    # Filter by kind
    labels = label_man.get_labels(kinds='figure')
    assert labels == [label1, label2]

    labels = label_man.get_labels(kinds=['figure', 'h1'])
    assert labels == [label1, label2]

    labels = label_man.get_labels(kinds=['h1'])
    assert labels == []


def test_reset(tmpdir):
    """Tests the reset method for the label manager."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("")

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a couple of short labels
    label1 = label_man.add_label(document=doc, kind='figure')
    label2 = label_man.add_label(document=doc, kind='figure')

    # Create a second document, use the context of the first document
    src_filepath2 = tmpdir.join('src').join('tmp2.dm')
    src_filepath2.write("")
    doc2 = Document(str(src_filepath2), str(tmpdir),
                    context=doc.context)

    # Generate a couple of short labels
    label3 = label_man.add_label(document=doc2, kind='figure')
    label4 = label_man.add_label(document=doc2, kind='figure')

    # Check the numbers
    assert label3.global_order == (3,)
    assert label3.local_order == (1,)
    assert label4.global_order == (4,)
    assert label4.local_order == (2,)

    # Check that the labels were correctly added. There should be 6: 2 for the
    # documents themselves, and 4 for the figures.
    assert len(label_man.labels) == 6
    assert label1 in label_man.labels
    assert label2 in label_man.labels
    assert label3 in label_man.labels
    assert label4 in label_man.labels

    # Now remove labels for the document in local_context
    label_man.reset(doc)

    assert len(label_man.labels) == 3
    assert label1 not in label_man.labels
    assert label2 not in label_man.labels
    assert label3 in label_man.labels
    assert label4 in label_man.labels

    # Check the numbers
    assert label3.global_order == (1,)
    assert label3.local_order == (1,)
    assert label4.global_order == (2,)
    assert label4.local_order == (2,)
