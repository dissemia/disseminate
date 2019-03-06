"""
Test the process_typography function.
"""
from disseminate.ast.typography import (process_typography,
                                        process_context_typography)
from disseminate.ast.ast import process_ast
from disseminate.tags import Tag
from disseminate import settings


def test_process_typography_dashes(context_cls):
    """Test process_typography with endashes and emdashes."""

    context = context_cls()

    # Test simple strings
    test1 = "An endash--this is a test of that"
    assert (process_typography(test1, context=context) ==
            "An endash–this is a test of that")

    test2 = "An emdash---this is a test of that"
    assert (process_typography(test2, context=context) ==
            "An emdash\u2014this is a test of that")

    # Test lists of strings
    test3 = ["An endash--this is a test of that"]
    assert (process_typography(test3, context=context) ==
            ["An endash–this is a test of that"])

    test4 = ["An emdash---this is a test of that"]
    assert (process_typography(test4, context=context) ==
            ["An emdash\u2014this is a test of that"])

    # Test tags with string contents
    test5 = Tag(name='root', content="An endash--this is a test of that",
                attributes=tuple(), context=context)
    assert (process_typography(test5, context=context).content ==
            "An endash–this is a test of that")
    test6 = Tag(name='root', content="An emdash---this is a test of that",
                attributes=tuple(), context=context)
    assert (process_typography(test6, context=context).content ==
            "An emdash\u2014this is a test of that")

    # Test tags with tag contents
    test7 = Tag(name='root', content=test5, attributes=tuple(), context=context)
    assert (process_typography(test7, context=context).content.content ==
            "An endash–this is a test of that")
    test8 = Tag(name='root', content=test6, attributes=tuple(), context=context)
    assert (process_typography(test8, context=context).content.content ==
            "An emdash\u2014this is a test of that")

    # Test tags in list asts.
    test9 = ["one", test5, "two"]
    assert (process_typography(test9, context=context)[1].content ==
            "An endash–this is a test of that")
    test10 = ["one", test6, "two"]
    assert (process_typography(test10, context=context)[1].content ==
            "An emdash\u2014this is a test of that")


def test_process_typography_apostrophes_and_quotes(context_cls):
    """Test process_typography with apostrophes and quotes."""

    context = context_cls()

    assert (process_typography("This is Justin's string.", context=context) ==
            "This is Justin’s string.")
    assert (process_typography("This is 'Justin's' string.", context=context)
            == "This is ‘Justin’s’ string.")
    assert (process_typography("This is \"Justin's\" string.", context=context)
            == "This is “Justin’s” string.")


def test_process_typography_verbatim(context_cls):
    """Test process_typography with endashes and emdashes."""

    context = context_cls()

    # Test a verbatim tag
    test1 = "@v{An emdash---this is a test of that}"
    ast = process_ast(test1, context=context)
    ast = process_typography(ast, context=context)

    assert ast.content == "An emdash---this is a test of that"


def test_process_context_typography(context_cls):
    """Test the process_context_typography function."""

    texts = ("This is Justin's string.",
             "This is 'Justin's' string.",
             "This is \"Justin's\" string.")
    results = ("This is Justin’s string.",
               "This is ‘Justin’s’ string.",
               "This is “Justin’s” string.")

    body_attr = settings.body_attr

    for text, result in zip(texts, results):
        context = context_cls(**{body_attr: text})
        process_context_typography(context)
        assert context[body_attr] == result
