"""
Test the process_typography function.
"""

from disseminate.tags import Tag


def test_process_typography_dashes(context_cls):
    """Test process_typography with endashes and emdashes."""

    context = context_cls()

    # Test simple strings
    test1 = "An endash--this is a test of that"
    tag1 = Tag(name='root', content=test1, attributes='', context=context)
    assert tag1.txt == "An endash–this is a test of that"

    test2 = "An emdash---this is a test of that"
    tag2 = Tag(name='root', content=test2, attributes='', context=context)
    assert tag2.txt == "An emdash\u2014this is a test of that"

    # Test lists of strings
    test3 = ["An endash--this is a test of that"]
    tag3 = Tag(name='root', content=test3, attributes='', context=context)
    assert tag3.txt == "An endash–this is a test of that"

    test4 = ["An emdash---this is a test of that"]
    tag4 = Tag(name='root', content=test4, attributes='', context=context)
    assert tag4.txt == "An emdash\u2014this is a test of that"


def test_process_typography_apostrophes_and_quotes(context_cls):
    """Test process_typography with apostrophes and quotes."""

    context = context_cls()

    # Test simple strings
    test1 = "This is Justin's string."
    tag1 = Tag(name='root', content=test1, attributes='', context=context)
    assert tag1.txt == "This is Justin’s string."

    test2 = "This is 'Justin's' string."
    tag2 = Tag(name='root', content=test2, attributes='', context=context)
    assert tag2.txt == "This is ‘Justin’s’ string."

    test3 = "This is \"Justin's\" string."
    tag3 = Tag(name='root', content=test3, attributes='', context=context)
    assert tag3.txt == "This is “Justin’s” string."


def test_process_typography_verbatim(context_cls):
    """Test process_typography with endashes and emdashes in verbatim, img
    and other tags that shouldn't be converted."""

    context = context_cls()

    # Test a verbatim tag
    test1 = "@v{An emdash---this is a test of that}"
    root1 = Tag(name='root', content=test1, attributes='', context=context)
    verb = root1.content
    assert verb.txt == "An emdash---this is a test of that"
