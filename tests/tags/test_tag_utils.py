"""
Tests for the tag utilities.
"""
import pytest

from disseminate.tags import Tag
from disseminate.tags.text import Italics
from disseminate.tags.utils import (repl_tags, content_to_str, replace_context,
                                    copy_tag)


def test_content_to_str(context_cls):
    """Test the content_to_str function."""

    # 1. Test basic string conversion
    assert content_to_str('my string') == 'my string'

    # 2. Test tag conversion
    context = context_cls()
    text = 'This is @i{my} string'
    root = Tag(name='root', content=text, attributes='', context=context)
    assert content_to_str(root) == 'This is my string'

    # 3. Test a list of strings and tags
    assert (content_to_str([root, ' and ', 'my string']) ==
            'This is my string and my string')

    # 4. Invalid types raise an error
    with pytest.raises(Exception):
        content_to_str(4)


def test_repl_tags(context_cls):
    """Test the repl_tags function."""
    context = context_cls()

    # 1. Test with an AST converted from a string

    # Setup a test source string
    test = """This is my test document. It has @b{nested @i{tags}} and
    @i{root-level} tags and @b{tags with @sub{@i{@i{sub}}}} tags."""

    # Parse it
    root = Tag(name='root', content=test, attributes='', context=context)

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
    assert root.content[5].content[1].content == 'REPLACED'
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


def test_replace_context(context_cls):
    """Test the replace context function."""

    context = context_cls()

    # 1. Replace the context for a root tag with nested tags
    test = """This is my test document. It has @b{nested @i{tags}} and
        @i{root-level} tags and @b{tags with @sub{@i{@i{sub}}}} tags."""

    root = Tag(name='root', content=test, attributes='', context=context)

    # Collect a list of all tags
    flattened_tags = root.flatten(filter_tags=True)

    assert len(flattened_tags) == 8
    assert all(id(tag.context) == id(context) for tag in flattened_tags)

    # Replace the context
    new_context = context_cls()
    replace_context(root, new_context)

    # Check the replacements
    assert all(id(tag.context) != id(context) for tag in flattened_tags)
    assert all(id(tag.context) == id(new_context) for tag in flattened_tags)


def test_tag_copy(context_cls):
    """Test the tag_copy function."""

    context = context_cls()

    # 1. Copy a root tag with nested tags
    test = """This is my test document. It has @b{nested @i{tags}} and
            @i{root-level} tags and @b{tags with @sub{@i{@i{sub}}}} tags."""

    root = Tag(name='root', content=test, attributes='', context=context)

    root_cp = copy_tag(root)

    # Check that the root_cp is an actual cp
    def test_tag_equiv(tag, other):
        return (id(tag) != id(other) and  # different objs
                tag == other and  # but equivalent
                id(root.attributes) != id(root_cp.attributes) and
                root.attributes == root_cp.attributes and
                id(root.content) != id(root_cp.content) and
                root.content == root_cp.content and
                id(root.context) == id(root_cp.context) and # same object
                id(root.__weakrefattrs__) != id(root_cp.__weakrefattrs__))

    # the root tag and all its subtags
    assert test_tag_equiv(root, root_cp)

    root_flattened = root.flatten(filter_tags=True)
    root_cp_flattened = root_cp.flatten(filter_tags=True)

    assert len(root_cp_flattened) == 8
    assert len(root_flattened) == len(root_cp_flattened)
    assert all(test_tag_equiv(i, j) for i, j in
               zip(root_flattened, root_cp_flattened))

    # 2. Try changing the contexts separately. This is possible because we
    #    created a copy of the __weakrefattrs__ dict.
    other = context_cls()
    for tag in root_cp_flattened:
        tag.context = other

    for tag1, tag2 in zip(root_flattened, root_cp_flattened):
        print(tag1.__dict__); print(tag2.__dict__)
        assert id(tag1) != id(tag2)
        assert id(tag1.context) == id(context)
        assert id(tag2.context) == id(other)
