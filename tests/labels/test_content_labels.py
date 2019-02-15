"""
Test the creation and manipulation of ContentLabel objects.
"""
from disseminate.labels.content_label import ContentLabel, curate_content_labels


def test_labels_curate_content_labels():
    """Test the curate content labels function."""
    # Create some heading labels
    label1 = ContentLabel(doc_id='a', id='a', kind=('heading', 'branch'),
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

    assert label1.branch_label == label1
    assert label1.section_label is None
    assert label1.subsection_label is None
    assert label1.branch_number == 1
    assert label1.branch_title == 'a'
    assert label1.section_label is None
    assert label1.section_number == ''
    assert label1.section_title == ''
    assert label1.subsection_label is None
    assert label1.subsection_number == ''
    assert label1.subsection_title == ''

    assert label2.branch_label == label1
    assert label2.section_label == label2
    assert label2.subsection_label is None
    assert label2.branch_title == 'a'
    assert label2.section_label == label2
    assert label2.section_number == 1
    assert label2.section_title == 'a.a'
    assert label2.subsection_label is None
    assert label2.subsection_number == ''
    assert label2.subsection_title == ''

    assert label3.branch_label == label1
    assert label3.section_label == label2
    assert label3.subsection_label == label3
    assert label3.branch_title == 'a'
    assert label3.section_label == label2
    assert label3.section_number == 1
    assert label3.section_title == 'a.a'
    assert label3.subsection_label == label3
    assert label3.subsection_number == 1
    assert label3.subsection_title == 'a.a.a'
