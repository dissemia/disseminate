"""
Tests the DocumentContext class.
"""
from disseminate.document import DocumentContext


# A DummyDocument class
class DummyDocument(object):
    src_filepath = ''
    project_root = ''
    target_root = ''


def test_document_context_inheritence():
    """Test the proper inheritence of the document context."""
    # Create a DocumentContext with one entry in the class's 'do_not_inherit'
    # class attribute and one not in 'do_not_inherit'
    parent_context = {'paths': [],
                      'lst': []}
    doc = DummyDocument()
    context = DocumentContext(document=doc, parent_context=parent_context)

    assert 'paths' in context.do_not_inherit
    assert 'lst' not in context.do_not_inherit

    assert 'paths' in context
    assert 'lst' in context
    assert context['paths'] == ['']  # An entry for the project_root
    assert context['lst'] == []

    # 'path' is not inherited
    assert id(parent_context['paths']) != id(context['paths'])

    # 'lst' is inherited
    assert id(parent_context['lst']) == id(context['lst'])
