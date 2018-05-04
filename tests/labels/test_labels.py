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
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # These are collected labels right now, and aren't registered. The only
    # registered label right now is the document label. There are 2 collected
    # labels for this document.
    assert len(label_man.labels) == 1
    assert len(label_man.collected_labels[doc.src_filepath]) == 2

    # Getting labels returns only the document label
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 1

    # Now register the labels. This will replace all registered labels with the
    # collected ones, thus removing the document label
    label_man.register_labels()
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 2

    label1 = labels[0]
    label2 = labels[1]

    # Try to get the labels. These are generic labels, which cannot be
    # retrieved.
    assert label1.id is None
    with pytest.raises(LabelNotFound):
        assert label1 == label_man.get_label(label1.id)

    assert label1.local_order == (1,)
    assert label1.global_order == (1,)
    assert label2.local_order == (2,)
    assert label2.global_order == (2,)

    # Generate a couple of specific labels
    label_man.add_label(document=doc, kind='figure', id='fig:image1')
    label_man.add_label(document=doc, kind='figure', id='fig:image2')

    # These aren't registered. They only get included once they're registered.
    # Since a registration was executed after adding label1 and label2, these
    # two labels replace those labels
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 2
    label_man.register_labels()
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 2

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
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # Get all labels. There should only be 1 registered label: the document's
    # label
    labels = label_man.get_labels()
    assert len(labels) == 1

    # Register the labels. Since we didn't add a new document label, there
    # should only be 2 labels: one for each figure.
    label_man.register_labels()
    labels = label_man.get_labels()
    assert len(labels) == 2

    # Get labels for this document
    labels = label_man.get_labels(document=doc)
    assert len(labels) == 2

    # Get labels for another document (a string is used since the type is not
    # checked)
    labels = label_man.get_labels(document='other')
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


def test_label_reordering(tmpdir):
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
    label_man.add_label(document=doc, kind='figure')
    label_man.add_label(document=doc, kind='figure')

    # Generate a couple of short labels for the sub-document
    label_man.add_label(document=doc2, kind='figure')
    label_man.add_label(document=doc2, kind='figure')

    # Register the labels. This will only register the newly collected labels:
    # i.e. the 4 label figures. Running it twice shouldn't impact the results
    for i in range(2):
        label_man.register_labels()
        label1, label2, label3, label4 = label_man.get_labels()

        # Check the numbers
        assert label1.local_order == (1,)
        assert label1.global_order == (1,)

        assert label2.local_order == (2,)
        assert label2.global_order == (2,)

        assert label3.local_order == (1,)
        assert label3.global_order == (3,)

        assert label4.local_order == (2,)
        assert label4.global_order == (4,)

    # Now reset the registration of labels for the first document. The
    # corresponding labels should also disappear.
    label_man.reset(document=doc)
    label_man.register_labels()

    labels = label_man.get_labels()
    assert len(labels) == 2
    label3, label4 = labels

    # Check the numbers
    assert label3.global_order == (1,)
    assert label3.local_order == (1,)
    assert label4.global_order == (2,)
    assert label4.local_order == (2,)

    # Now delete the 2nd document and the labels should be removed too.
    doc2 = None
    doc.subdocuments.clear()
    label_man.register_labels()
    assert len(label_man.get_labels()) == 0


def test_labels_chapter_numbers(tmpdir):
    """Test the labeling of chapter numbers."""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.write("""
    ---
    targets: html, txt
    ---
    @chapter{First Chapter}
    @section{Section One-One}
    @chapter{Second Chapter}
    @section{Section Two-One}
    @chapter{Third Chapter}
    """)

    doc = Document(str(src_filepath), str(tmpdir))

    # Check the labels
    label_man = doc.context['label_manager']

    # There should be 6 labels: 1 for the document, 3 for chapters,
    # 2 for sections
    assert len(label_man.labels) == 6

    # Check the formatted string of the labels
    chapter_labels = label_man.get_labels(kinds='chapter')
    assert len(chapter_labels) == 3

    # First try the short title
    doc.context['chapter_label'] = '{short}'
    assert chapter_labels[0].label(target='.txt') == 'First Chapter'
    assert chapter_labels[1].label(target='.txt') == 'Second Chapter'
    assert chapter_labels[2].label(target='.txt') == 'Third Chapter'

    # Next try the chapter number
    doc.context['chapter_label'] = 'Chapter {chapter_number}'
    assert chapter_labels[0].label(target='.txt') == 'Chapter 1'
    assert chapter_labels[1].label(target='.txt') == 'Chapter 2'
    assert chapter_labels[2].label(target='.txt') == 'Chapter 3'

    # Next try the section numbers
    section_labels = label_man.get_labels(kinds='section')
    assert len(section_labels) == 2

    # First try the short title
    doc.context['section_label'] = '{short}'
    assert section_labels[0].label(target='.txt') == 'Section One-One'
    assert section_labels[1].label(target='.txt') == 'Section Two-One'

    # Next try the chapter and section number
    doc.context['section_label'] = 'Section {chapter_number}.{section_number}'
    assert section_labels[0].label(target='.txt') == 'Section 1.1'
    assert section_labels[1].label(target='.txt') == 'Section 2.1'
