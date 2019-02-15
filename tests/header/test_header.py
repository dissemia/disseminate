"""
Test the header functions.
"""
from disseminate.header import load_header
from disseminate import settings


def test_load_header(context_cls):
    """Test the load header function."""

    test = """
    ---
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    ---
    body
    """
    body_attr = settings.body_attr
    context = context_cls(**{body_attr: test})
    load_header(context)

    assert context[body_attr] == '    body\n    '

    assert 'contact' in context
    assert context['contact'] == '  address: 1,2,3 lane\n  phone: 333-333-4123.'

    assert 'name' in context
    assert context['name'] == 'Justin L Lorieau'

    assert 'address' not in context
    assert 'phone' not in context
