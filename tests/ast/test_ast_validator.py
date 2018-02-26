"""
Test the ASTValidator.
"""
import pytest

from disseminate.ast import process_ast
from disseminate.ast.validate import ParseError


def test_ast_validation():
    """Test the correct validation when parsing an AST."""

    test_invalid = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @caption{This is my @i{first} figure.}
    """

    # Process a string with an open tag
    with pytest.raises(ParseError) as e:
        ast = process_ast([test_invalid])
        print(process_ast(ast))

    # The error should pop up in line 4
    assert "line 4" in str(e.value)

    # Validate closing bracket