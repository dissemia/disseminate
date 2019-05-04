"""
Test the creation and manipulation of ContentLabel objects.
"""
from disseminate.labels.content_label import ContentLabel, curate_content_labels


def test_labels_curate_content_empty_kind():
    """Test the curate_content_labels function with no kind specified."""
    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=(),
                          mtime=None, title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=(),
                          mtime=None, title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a',
                          mtime=None, kind=(),
                          title='a.a.a')

    # Try curating the heading labels
    curate_content_labels(registered_labels=[label1, label2, label3])

    # Check the values of the labels. There is not kind, so the labels have no
    # global_order or local_order
    assert label1.global_order == ()
    assert label2.global_order == ()
    assert label3.global_order == ()

    assert label1.local_order == ()
    assert label2.local_order == ()
    assert label3.local_order == ()


def test_labels_curate_content_labels_chapter():
    """Test the curate_content_labels function for chapter and lower
    headings."""
    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'chapter'),
                          mtime=None, title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'section'),
                          mtime=None, title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a',
                          mtime=None, kind=('heading', 'subsection'),
                          title='a.a.a')

    # Try curating the heading labels
    curate_content_labels(registered_labels=[label1, label2, label3])

    # Check the values of the labels
    assert label1.global_order == (1, 1)
    assert label2.global_order == (2, 1)
    assert label3.global_order == (3, 1)

    assert label1.local_order == (1, 1)
    assert label2.local_order == (2, 1)
    assert label3.local_order == (3, 1)

    assert label1.part_label is None
    assert label1.chapter_label == label1
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.chapter_number == 1
    assert label1.chapter_title == 'a'
    assert label1.section_label is None
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_label is None
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''

    assert label2.part_label is None
    assert label2.chapter_label == label1
    assert label2.section_label == label2
    assert label2.subsection_label is None
    assert label2.chapter_title == 'a'
    assert label2.section_label == label2
    assert label2.section_number == 1
    assert label2.section_title == 'a.a'
    assert label2.subsection_label is None
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''

    assert label3.part_label is None
    assert label3.chapter_label == label1
    assert label3.section_label == label2
    assert label3.subsection_label == label3
    assert label3.chapter_title == 'a'
    assert label3.section_label == label2
    assert label3.section_number == 1
    assert label3.section_title == 'a.a'
    assert label3.subsection_label == label3
    assert label3.subsection_number == 1
    assert label3.subsection_title == 'a.a.a'


def test_labels_curate_content_labels_part():
    """Test the curate_content_labels function for part and lower
    headings."""
    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'part'),
                          mtime=None, title='a')
    label2 = ContentLabel(doc_id='a', id='a.a', kind=('heading', 'chapter'),
                          mtime=None, title='a.a')
    label3 = ContentLabel(doc_id='a', id='a.a.a', kind=('heading', 'section'),
                          mtime=None, title='a.a.a')
    label4 = ContentLabel(doc_id='a', id='a.a.a.a',
                          mtime=None, kind=('heading', 'subsection'),
                          title='a.a.a.a')

    # Try curating the heading labels
    curate_content_labels(registered_labels=[label1, label2, label3, label4])

    # Check the values of the labels
    assert label1.global_order == (1, 1)
    assert label2.global_order == (2, 1)
    assert label3.global_order == (3, 1)
    assert label4.global_order == (4, 1)

    assert label1.local_order == (1, 1)
    assert label2.local_order == (2, 1)
    assert label3.local_order == (3, 1)
    assert label4.local_order == (4, 1)

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
