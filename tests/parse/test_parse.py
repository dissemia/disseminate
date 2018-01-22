import pytest

from disseminate import process_ast

def test_ast_basic_string():
    """Test the parsing of a basic string into an AST."""

    test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph.
    """
    ast = process_ast(test)
    print(ast)

    
