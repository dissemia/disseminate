"""
Test the utilities for processing ASTs.
"""
from disseminate.ast import process_ast
from disseminate.ast.utils import count_ast_lines


def test_count_ast_lines():
    """Test the count_ast_lines function."""

    # Setup a test source string
    test = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @captiontag{This is my @i{first} figure.}
        }

        This is a @13C variable.

        Here is a @i{new} paragraph."""

    # Parse it
    ast = process_ast(test)

    # The total number of lines
    assert count_ast_lines(ast) == 12

    # The number of lines in elements
    assert count_ast_lines(ast[0]) == 4
    assert count_ast_lines(ast[1]) == 1
    assert count_ast_lines(ast[2]) == 2
    assert count_ast_lines(ast[3]) == 4
    assert count_ast_lines(ast[3][1]) == 1
    assert count_ast_lines(ast[3][3]) == 1
    assert count_ast_lines(ast[4]) == 3
    assert count_ast_lines(ast[5]) == 1
    assert count_ast_lines(ast[6]) == 3
    assert count_ast_lines(ast[7]) == 1
    assert count_ast_lines(ast[8]) == 1
