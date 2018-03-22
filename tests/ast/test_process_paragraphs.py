"""
Test the proces_paragraphs function.
"""
from disseminate.ast import process_ast, process_paragraphs
from disseminate.macros import replace_macros
from disseminate.tags.text import P
from disseminate.tags.text import Bold


test_paragraphs = """
This is my @b{first} paragraph.

This is my @i{second}. It has a multiple
lines.

This paragraph has a note. @note{

This note has multiple lines.

and multiple paragraphs.
}

This is the fourth paragraph

@section{A heading (no paragraph}

A fifth paragraph.

Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @b{test}
    }

My final paragraph.
"""

test_paragraphs2 = """
  @section{A heading with leading spaces}
  
  This is my paragraph.
"""


def test_process_paragraphs():
    """Test the process_paragraphs function"""

    ast = process_ast(test_paragraphs)
    ast = process_paragraphs(ast)

    # Check the individual items of the ast.
    assert isinstance(ast[0], P)
    assert ast[0].content[0] == 'This is my '
    assert ast[0].content[1].name == 'b'  # bolded
    assert ast[0].content[2] == ' paragraph.'

    assert isinstance(ast[1], P)
    assert ast[1].content[0] == 'This is my '
    assert ast[1].content[1].name == 'i'  # italics
    assert ast[1].content[2] == '. It has a multiple\nlines.'

    assert isinstance(ast[2], P)
    assert ast[2].content[0] == 'This paragraph has a note. '
    assert ast[2].content[1].name == 'note'  # note

    assert isinstance(ast[3], P)
    assert ast[3].content == 'This is the fourth paragraph'

    assert ast[4].name == 'section'
    assert ast[4].content == 'A heading (no paragraph'

    assert isinstance(ast[5], P)
    assert ast[5].content == 'A fifth paragraph.'

    assert isinstance(ast[6], P)
    assert ast[6].content[0] == 'Here is a new one with '
    assert ast[6].content[1].name == 'b'  # bolded
    assert ast[6].content[2] == ' text as an example.\n    '
    assert ast[6].content[3].name == 'marginfig'  # margin tag

    assert isinstance(ast[7], P)
    assert ast[7].content == 'My final paragraph.'


def test_process_paragraphs_leading_spaces():
    """Test the process_paragraphs function when trailing spaces are present.
    """

    ast = process_ast(test_paragraphs2)
    ast = process_paragraphs(ast)

    assert ast.content[0] == '  '
    assert ast.content[1].name == 'section'
    assert ast.content[2] == '  \n  This is my paragraph.'


def test_process_paragraphs_edgecases():
    """Test the process_paragraphs function for a series of edge cases."""

    # Test a basic string with no tags. This create a root tag
    test_edge = "basic"
    ast = process_paragraphs(test_edge)

    assert ast.name == 'root'
    assert ast.content.name == 'p'
    assert ast.content.content == 'basic'
    assert ast.tex() == '\nbasic\n'


def test_process_paragraphs_macros():
    """Test the process_paragraphs function with macros."""

    # setup a test ast with a macro
    context = {'macros': {'@p90x': '90@deg@sub{x}'}}

    result = replace_macros("My @p90x pulse.", context=context)
    ast = process_paragraphs([result], context=context)
    assert ast.content.content == "My 90@sup{○}@sub{x} pulse."

    # Test paragraph processing with a macro and tag
    result = replace_macros("My @b{y = x} @1H pulse.", context=context)
    ast = process_paragraphs([result], context=context)
    assert ast.name == 'root'
    assert ast.content.name == 'p'
    assert ast.content.content == 'My @b{y = x} @sup{1}H pulse.'

    # Test paragraph processing after process_ast
    ast = process_ast(result, context={})
    ast = process_paragraphs(ast, context=context)
