"""
Test the proces_paragraphs function.
"""
from disseminate.ast import process_ast, process_paragraphs
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


def test_process_paragraphs():
    """Test the process_paragraphs function"""

    # Disable the management of dependencies for tags
    manage_dependencies = Img.manage_dependencies
    Img.manage_dependencies = False

    ast = process_ast([test_paragraphs])
    ast = process_paragraphs(ast)

    for count, i in enumerate(ast):
        print("{}: {}".format(count, i))
    # Reset dependency management
    Img.manage_dependencies = manage_dependencies
