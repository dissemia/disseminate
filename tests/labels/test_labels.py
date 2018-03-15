"""
Tests the label manager and label classes.
"""
import pytest
from lxml import etree

from disseminate.labels import LabelManager, LabelNotFound
from disseminate import Document


def test_basic_labels(tmpdir):
    """Tests the basic functionality of labels."""
    # Create a test document and global_context
    global_context = dict()
    src_filepath = tmpdir.join('src').join('main.dm')
    doc = Document(src_filepath=str(src_filepath),
                   targets={'.html': str(tmpdir.join('html').join('main.html')),
                            '.tex': str(tmpdir.join('html').join('main.html'))},
                   global_context=global_context)

    # Get a label manager
    label_man = LabelManager()

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
    # Create a test document and global_context
    global_context = dict()
    src_filepath = tmpdir.join('src').join('main.dm')
    doc = Document(src_filepath=str(src_filepath),
                   targets={'.html': str(tmpdir.join('html').join('main.html')),
                            '.tex': str(tmpdir.join('html').join('main.html'))},
                   global_context=global_context)

    # Get a label manager
    label_man = LabelManager()

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label1 = label_man.add_label(document=doc, kind='figure')
    label2 = label_man.add_label(document=doc, kind='figure')

    # Get all labels
    labels = label_man.get_labels()
    assert labels == [label1, label2]

    # Get labels for this document
    labels = label_man.get_labels(document=doc)
    assert labels == [label1, label2]

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
    # Create a test document and global_context
    global_context = dict()
    src_filepath = tmpdir.join('src').join('main.dm')
    doc = Document(src_filepath=str(src_filepath),
                   targets={'.html': str(tmpdir.join('html').join('main.html')),
                            '.tex': str(tmpdir.join('html').join('main.html'))},
                   global_context=global_context)

    # Get a label manager
    label_man = LabelManager()

    # Generate a couple of short labels
    label1 = label_man.add_label(document=doc, kind='figure')
    label2 = label_man.add_label(document=doc, kind='figure')

    # Create a second document
    src_filepath2 = tmpdir.join('src').join('tmp2.dm')
    doc2 = Document(src_filepath=str(src_filepath2),
                    targets={'.html': str(tmpdir.join('html').join('tmp2.html')),
                             '.tex': str(tmpdir.join('html').join('tmp2.html'))},
                    global_context=global_context)

    # Generate a couple of short labels
    label3 = label_man.add_label(document=doc2, kind='figure')
    label4 = label_man.add_label(document=doc2, kind='figure')

    # Check the numbers
    assert label3.global_number == 3
    assert label3.local_number == 1
    assert label4.global_number == 4
    assert label4.local_number == 2

    # Check that the labels were correctly added
    assert len(label_man.labels) == 4
    assert label1 in label_man.labels
    assert label2 in label_man.labels
    assert label3 in label_man.labels
    assert label4 in label_man.labels

    # Now remove labels for the document in local_context
    label_man.reset(doc)

    assert len(label_man.labels) == 2
    assert label1 not in label_man.labels
    assert label2 not in label_man.labels
    assert label3 in label_man.labels
    assert label4 in label_man.labels

    # Check the numbers
    assert label3.global_number == 1
    assert label3.local_number == 1
    assert label4.global_number == 2
    assert label4.local_number == 2


def test_label_html(tmpdir):
    """Tests the generation of html from a label"""
    # Create a test document and global_context
    global_context = {'_target_root': str(tmpdir),
                      '_segregate_targets': True}
    src_filepath = tmpdir.join('src').join('main.dm')
    doc = Document(src_filepath=str(src_filepath),
                   targets={'.html': str(tmpdir.join('html').join('main.html')),
                            '.tex': str(tmpdir.join('html').join('main.html'))},
                   global_context=global_context)

    # Get a label manager
    label_man = LabelManager()

    # Generate a specific labels
    label1 = label_man.add_label(document=doc,  kind='figure', id='fig:image1')

    # Check the html label
    local_context = {'_src_filepath': doc.src_filepath,
                     'figure': "Fig. {number}"}
    html = etree.tostring(label1.html_label(local_context=local_context))
    html = html.decode('utf-8')
    assert html == '<span class="figure-label" id="fig:image1">Fig. 1.</span>'

    # Check the html reference (from inside the document)
    html = etree.tostring(label1.html_ref(local_context=local_context))
    html = html.decode('utf-8')
    assert html == '<a href="#fig:image1">Fig. 1</a>'

    # Check the html reference (from outside the document and with a different
    # local_context)
    local_context = {'_src_filepath': 'different',
                     'figure': "Fig. {number}"}
    html = etree.tostring(label1.html_ref(local_context=local_context))
    html = html.decode('utf-8')
    assert html == '<a href="main.html#fig:image1">Fig. 1</a>'
