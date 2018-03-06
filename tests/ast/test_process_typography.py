"""
Test the process_typography function.
"""
from disseminate.ast.process_typography import process_typography
from disseminate.tags import Tag


def test_process_typography_dashes():
    """Test process_typography with endashes and emdashes."""

    # Test simple strings
    test1 = "An endash--this is a test of that"
    assert process_typography(test1) == "An endash–this is a test of that"

    test2 = "An emdash---this is a test of that"
    assert process_typography(test2) == "An emdash\u2014this is a test of that"

    # Test lists of strings
    test3 = ["An endash--this is a test of that"]
    assert process_typography(test3) == ["An endash–this is a test of that"]

    test4 = ["An emdash---this is a test of that"]
    assert (process_typography(test4) ==
            ["An emdash\u2014this is a test of that"])

    # Test tags with string contents
    test5 = Tag(name='root', content="An endash--this is a test of that",
                attributes=tuple(), local_context=dict(), global_context=dict())
    assert (process_typography(test5).content ==
            "An endash–this is a test of that")
    test6 = Tag(name='root', content="An emdash---this is a test of that",
                attributes=tuple(), local_context=dict(), global_context=dict())
    assert (process_typography(test6).content ==
            "An emdash\u2014this is a test of that")

    # Test tags with tag contents
    test7 = Tag(name='root', content=test5,
                attributes=tuple(), local_context=dict(), global_context=dict())
    assert (process_typography(test7).content.content ==
            "An endash–this is a test of that")
    test8 = Tag(name='root', content=test6,
                attributes=tuple(), local_context=dict(), global_context=dict())
    assert (process_typography(test8).content.content ==
            "An emdash\u2014this is a test of that")

    # Test tags in list asts.
    test9 = ["one", test5, "two"]
    assert (process_typography(test9)[1].content ==
            "An endash–this is a test of that")
    test10 = ["one", test6, "two"]
    assert (process_typography(test10)[1].content ==
            "An emdash\u2014this is a test of that")


def test_process_typography_apostrophes_and_quotes():
    """Test process_typography with apostrophes and quotes."""

    assert (process_typography("This is Justin's string.") ==
            "This is Justin’s string.")
    assert (process_typography("This is 'Justin's' string.") ==
            "This is ‘Justin’s’ string.")
    assert (process_typography("This is \"Justin's\" string.") ==
            "This is “Justin’s” string.")