"""
Test the Label class.
"""
from disseminate.label_manager.types import Label, ContentLabel


def test_label_repr():
    """Test the representation of Label objects."""

    # Create a label
    label = Label(doc_id='mydoc', id='test1', kind=())
    assert repr(label) == "Label(doc_id: 'mydoc', id: 'test1')"

    # Set the order and kind
    label.kind = ('heading', 'section')
    label.order = (3, 1)
    assert repr(label) == ("Label(doc_id: 'mydoc', id: 'test1', "
                           "kind: heading[3], section[1])")


def test_label_cmp():
    """Test comparison and sorting methods for labels."""

    # Create labels
    label1 = Label(doc_id='mydoc', id='test1', kind=())
    label2 = Label(doc_id='mydoc', id='test2', kind=())
    label2a = Label(doc_id='mydoc', id='test2', kind=('heading', 'chapter'))
    label3 = Label(doc_id='mydoc', id='test3', kind=())

    assert label1 < label2
    assert label1 <= label2
    assert label1 <= label1
    assert label2 > label1
    assert label2 >= label1
    assert label1 >= label1
    assert label1 == label1
    assert label1 != label2

    assert label2 == label2a  # same doc_id and label_id
    assert list(sorted([label3, label2, label1])) == [label1, label2, label3]


def test_contentlabel_repr():
    """Test the representation of ContentLabel objects."""

    # Create a label
    label = ContentLabel(doc_id='mydoc', id='test1', kind=(), title='My Title')
    assert repr(label) == ("ContentLabel(doc_id: 'mydoc', id: 'test1' "
                           "title: 'My Title')")
