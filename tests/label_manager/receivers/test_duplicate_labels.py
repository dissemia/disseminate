"""
Test the FindDuplicateLabels class
"""
import pytest

from disseminate.label_manager.receivers import duplicate_labels
from disseminate.label_manager.exceptions import DuplicateLabel
from disseminate.label_manager.types import Label


def test_find_duplicate_labels_processor(context_cls):
    """Test the FindDuplicateLabels label processor."""

    context = context_cls()

    # Create a new mock label type
    class TestLabel(Label):
        pass

    # Create a set of registered labels and collected labels
    label1 = Label(doc_id='a', id='1', kind='label', mtime=None)
    label2 = Label(doc_id='a', id='2', kind='label', mtime=None)
    label3 = Label(doc_id='a', id='3', kind='label', mtime=None)
    label4 = TestLabel(doc_id='b', id='1', kind='label', mtime=None)  # dupe

    # Try running find_duplicates without a duplicate label
    duplicate_labels(registered_labels=[label1, label2],
                     collected_labels={'a': [label3]})  # no duplicates

    # Try running find_duplicates with a duplicate label
    with pytest.raises(DuplicateLabel):
        duplicate_labels(registered_labels=[label1, label2],
                         collected_labels={'a': [label3], 'b': [label4]})
