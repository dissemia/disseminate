"""
Test the Label class.
"""
from disseminate.label_manager.types import Label


def test_label_repr():
    """Test the representation of Label objects."""

    # Create a label
    label = Label(doc_id='mydoc', id='test1', kind=(), mtime=-1)
    assert repr(label) == "Label(doc_id: 'mydoc', id: 'test1')"

    # Set the order and kind
    label.kind = ('heading', 'section')
    label.order = (3, 1)
    assert repr(label) == ("Label(doc_id: 'mydoc', id: 'test1', "
                           "kind: heading[3], section[1])")
