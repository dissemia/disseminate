"""
Tests for the tag utilities.
"""
from disseminate.tags.text import Italics
from disseminate.tags.utils import repl_tags
from disseminate.ast import process_ast


def test_repl_tags(context_cls):
    """Test the repl_tags function."""
    context = context_cls()

    # 1. Test with an AST converted from a string

    # Setup a test source string
    test = """This is my test document. It has @b{nested @i{tags}} and
    @i{root-level} tags and @b{tags with @sub{@i{@i{sub}}}} tags."""

    # Parse it
    root = process_ast(test, context=context)

    # Try replacing the @i (Italics) tags
    repl_tags(element=root, tag_class=Italics, replacement='REPLACED')

    # Check the text rendering
    assert root.txt == """This is my test document. It has nested REPLACED and
    REPLACED tags and tags with REPLACED tags."""

    # Check the AST
    assert root.content[0] == 'This is my test document. It has '
    assert root.content[1].name == 'b'
    assert root.content[1].content[0] == 'nested '
    assert root.content[1].content[1] == 'REPLACED'
    assert root.content[2] == ' and\n    '
    assert root.content[3] == 'REPLACED'
    assert root.content[4] == ' tags and '
    assert root.content[5].name == 'b'
    assert root.content[5].content[0] == 'tags with '
    assert root.content[5].content[1].name == 'sub'
    assert root.content[5].content[1].content == ['REPLACED']
    assert root.content[6] == ' tags.'

    # 2. Test with a replacement tag directly
    i = Italics(name='i', content='my content', attributes=tuple(),
                context=context)
    new_element = repl_tags(element=i, tag_class=Italics,
                            replacement='replaced')
    assert new_element == 'replaced'

    # 3. Test a list with a tag
    l = [1, 2, i, '3']
    new_element = repl_tags(element=l, tag_class=Italics,
                            replacement='replaced')
    assert id(l) == id(new_element)  # same list
    assert new_element == [1, 2, 'replaced', '3']
