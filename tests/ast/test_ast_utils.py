"""
Test the utilities for processing ASTs.
"""
from disseminate.ast import process_ast
from disseminate.ast.utils import count_ast_lines, flatten_ast


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

        This is a @13C variable, but this is an email address: justin@lorieau.com

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
    assert count_ast_lines(ast[4]) == 5


def test_flatten_ast():
    """Test the flatten_ast function."""
    # Setup a test source string
    test = """
            This is my test document. It has multiple paragraphs.

            Here is a new one with @b{bolded} text as an example.
            @figuretag[offset=-1.0em]{
              @imgtag{media/files}
              @captiontag{This is my @i{first} figure.}
            }

            This is a @13C variable, but this is an email address: justin@lorieau.com

            Here is a @i{new} paragraph."""

    # Parse it
    ast = process_ast(test)

    # Convert the ast to a flattened list and check the items
    flattened_ast = flatten_ast(ast, filter_tags=True)

    assert len(flattened_ast) == 7
    assert flattened_ast[0].name == 'root'
    assert flattened_ast[1].name == 'b'
    assert flattened_ast[2].name == 'figuretag'
    assert flattened_ast[3].name == 'imgtag'
    assert flattened_ast[4].name == 'captiontag'
    assert flattened_ast[5].name == 'i'
    assert flattened_ast[6].name == 'i'
