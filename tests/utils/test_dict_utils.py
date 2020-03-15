"""
Test dict utility functions.
"""
from disseminate.utils.dict import find_entry


def test_find_entry():
    """Test the find_entry function on dicts."""
    d = {'starter_middle1_term': 1,
         'starter_middle1': 2,
         'starter_middle2_term': 3,
         'starter_middle2': 4,
         'starter_term': 5,
         'starter': 6}

    assert find_entry(d, 'starter', 'middle1', suffix='term') == 1
    assert find_entry(d, 'starter', 'middle1') == 2
    assert find_entry(d, 'starter', 'middle2', suffix='term') == 3
    assert find_entry(d, 'starter', 'middle2', ) == 4
    assert find_entry(d, 'starter', suffix='term') == 5
    assert find_entry(d, 'starter') == 6
