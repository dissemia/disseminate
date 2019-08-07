"""
Test utilities for BaseContexts.
"""
from disseminate.context.utils import find_header_entries, load_from_string


def test_find_header_entries():
    """Test the find_header_entries function."""

    # 1. Create a dict with a string containing a header under 'body
    test = """
    ---
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    ---
    body
    """

    context = dict(body=test, decoy='not header')
    keys = find_header_entries(context=context)

    assert set(keys) == {'body'}


def test_load_from_string():
    """Test the load_from_string function."""

    # 1. Create a header string
    test = """
    ---
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    ---
    body
    """

    rest, context = load_from_string(test)

    assert rest == '    body\n    '
    assert context == {'name': 'Justin L Lorieau',
                       'contact': ('  address: 1,2,3 lane\n'
                                   '  phone: 333-333-4123.')}
