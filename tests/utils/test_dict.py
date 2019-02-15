"""
Test dict utility functions.
"""
import pytest

from disseminate.utils.dict import find_entry


# def test_find_entry():
#     """Test the find_entry function on dicts."""
#
#     default = {'chapter': 'chapter (default)',
#                'chapter_tex': 'chapter_tex (default)'}
#     specific = {'chapter': 'chapter (specific)',
#                 'chapter_tex': 'chapter_tex (specific)'}
#
#     assert find_entry((specific, default), 'chapter') == 'chapter (specific)'
#     assert find_entry((specific, default), 'chapter') == 'chapter (specific)'
#     assert find_entry(default, 'chapter') == 'chapter (default)'
#
#     assert find_entry((specific, default),
#                       'chapter', 'tex') == 'chapter_tex (specific)'
#     assert find_entry((specific, default),
#                       'chapter', 'bogus') == 'chapter (specific)'
#
#     # Test missing keys
#     with pytest.raises(KeyError):
#         find_entry(default, 'missing')

def test_find_entry():
    """Test the find_entry function on dicts."""
    d = {'starter_middle1_term': 1,
         'starter_middle1': 2,
         'starter_middle2_term': 3,
         'starter_middle2': 4,
         'starter_term': 5,
         'starter': 6}

    assert find_entry(d, 'starter', ('middle1', 'middle2'), 'term') == 1
    assert find_entry(d, 'starter', ('middle1', 'middle2'),) == 2
    assert find_entry(d, 'starter', ('middle2',), 'term') == 3
    assert find_entry(d, 'starter', ('middle2',), ) == 4
    assert find_entry(d, 'starter', None, 'term') == 5
    assert find_entry(d, 'starter') == 6
