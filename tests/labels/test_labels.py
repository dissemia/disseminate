"""
Tests the label manager and label classes.
"""
import pytest
from lxml import etree

from disseminate.labels import LabelManager, LabelNotFound


def test_basic_labels():
    """Tests the basic functionality of labels."""
    # Get a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Make a mock local_context
    local_context = {'_src_filepath': 'src/main1.dm',
                     '_targets': {'.html': 'html/main1.dm'}}

    # Generate a couple of generic labels. These have no id and cannot be
    # fetched
    label1 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure')
    label2 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure')

    # Try to get the labels. These are generic labels, which cannot be
    # retrieved.
    assert label1.id is None
    with pytest.raises(LabelNotFound):
        assert label1 == label_man.get_label(label1.id)

    # Generate a couple of specific labels
    label3 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure',
                                 id='fig:image1')
    label4 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure',
                                 id='fig:image2')

    # Get the labels and make sure they match
    assert label3 == label_man.get_label('fig:image1')
    assert label4 == label_man.get_label('fig:image2')


def test_reset():
    """Tests the reset method for the label manager."""
    # Get a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Make a mock local_context
    local_context = {'_src_filepath': 'src/main1.dm',
                     '_targets': {'.html': 'html/main1.html'}}

    # Generate a couple of short labels
    label1 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure')
    label2 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure')

    # Create a second mock local_context for a second document
    local_context2 = {'_src_filepath': 'src/main2.dm',
                      '_targets': {'.html': 'html/main2.html'}}

    # Generate a couple of short labels
    label3 = label_man.add_label(local_context=local_context2,
                                 global_context=None,
                                 kind='figure')
    label4 = label_man.add_label(local_context=local_context2,
                                 global_context=None,
                                 kind='figure')

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
    label_man.reset('src/main1.dm')

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


def test_label_html():
    """Tests the generation of html from a label"""
    # Get a label manager
    label_man = LabelManager(project_root='src', target_root='.',
                             segregate_targets=True)

    # Make a mock local_context
    local_context = {'_src_filepath': 'src/main1.dm',
                     '_targets': {'.html': 'html/main1.html'}}

    # Generate a specific labels
    label1 = label_man.add_label(local_context=local_context,
                                 global_context=None,
                                 kind='figure',
                                 id='fig:image1')

    # Check the html label
    html = etree.tostring(label1.html_label()).decode('utf-8')
    assert html == '<span class="figure-label" id="fig:image1">Fig. 1.</span>'

    # Check the html reference (from inside the document)
    html = etree.tostring(label1.html_ref(local_context=local_context))
    html = html.decode('utf-8')
    assert html == '<a href="#fig:image1">Fig. 1</a>'

    # Check the html reference (from outside the document and with a different
    # local_context)
    html = etree.tostring(label1.html_ref())
    html = html.decode('utf-8')
    assert html == '<a href="main1.html#fig:image1">Fig. 1</a>'
