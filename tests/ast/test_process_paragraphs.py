"""
Test the proces_paragraphs function.
"""
from disseminate.ast import process_ast, process_paragraphs
from disseminate.tags.text import P
from disseminate.tags.img import Img


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
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

My final paragraph.
"""

test_paragraphs2 = """
  @section{A heading with leading spaces}
"""


def test_process_paragraphs():
    """Test the process_paragraphs function"""

    # Disable the management of dependencies for tags
    manage_dependencies = Img.manage_dependencies
    Img.manage_dependencies = False

    ast = process_ast([test_paragraphs])
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

    # Reset dependency management
    Img.manage_dependencies = manage_dependencies


def test_process_paragraphs_leading_spaces():
    """Test the process_paragraphs function when trailing spaces are present.
    """

    ast = process_ast([test_paragraphs2])
    ast = process_paragraphs(ast)

    assert ast.content.name == 'section'
    assert ast.content.content == 'A heading with leading spaces'
