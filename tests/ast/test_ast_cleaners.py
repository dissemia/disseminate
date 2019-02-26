"""
Test the AST cleaner functions.
"""
from disseminate.tags import Tag
from disseminate.ast.cleaners import clean_strings


def test_clean_string(context_cls):
    """Test the clean_string function."""

    context = context_cls()

    # Try simple flat lists
    assert clean_strings(['a', 'b', 5, 'c', 'd']) == ['ab', 5, 'cd']
    assert clean_strings([1, 2, 3, 4]) == [1, 2, 3, 4]

    # Try nested lists
    assert (clean_strings(['a', 'b', [1, 2, 3], 'c', 'd']) ==
            ['ab', [1, 2, 3], 'cd'])
    assert (clean_strings(['a', 'b', [1, 'c', 'd'], 'e', 'f']) ==
            ['ab', [1, 'cd'], 'ef'])

    # Try with tags non-nested tag
    tag = Tag(name='tag', content='test', attributes=(), context=context)
    assert (clean_strings(['a', 'b', tag, 'c', 'd']) ==
            ['ab', tag, 'cd'])

    # Try with nested tags
    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (clean_strings(tag) == tag)
    assert tag.content == [1, 'cd']

    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (clean_strings([tag]) == [tag])
    assert tag.content == [1, 'cd']

    tag = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
              context=context)
    assert (clean_strings(['a', 'b', tag, 'c', 'd']) ==
            ['ab', tag, 'cd'])
    assert tag.content == [1, 'cd']

    tag1 = Tag(name='tag', content=[1, 'c', 'd'], attributes=(),
               context=context)
    tag2 = Tag(name='tag', content=[tag1, 'c', 'd'], attributes=(),
               context=context)
    assert (clean_strings(['a', 'b', tag2, 'c', 'd']) ==
            ['ab', tag2, 'cd'])
    assert tag1.content == [1, 'cd']
    assert tag2.content == [tag1, 'cd']
