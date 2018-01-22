from pprint import pprint

import pytest

from disseminate import process_ast
from disseminate import Tag
from disseminate.ast import print_ast


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

    test_pieces = test.splitlines()

    # Check the AST piece-by-piece
    assert ast[0] == test[0:len(ast[0])] # string

    assert isinstance(ast[1], Tag) and ast[1].tag_type == 'b' # b tag

    assert isinstance(ast[2], str) # string

    assert isinstance(ast[3], Tag) and ast[3].tag_type == 'marginfig'  # margin tag
    assert isinstance(ast[3].tag_content, list)  # margin tag has subtags in a list

    assert isinstance(ast[3][0], str) # string

    assert isinstance(ast[3][1], Tag) and ast[3][1].tag_type == 'img'  # img tag
    assert ast[3][1].tag_content == "media/files"  # img contents

    assert isinstance(ast[3][2], str)  # string

    assert isinstance(ast[3][3], Tag) and ast[3][3].tag_type == 'caption'  # caption tag
    assert isinstance(ast[3][3].tag_content, list)  # contents includes strings and tags

    assert isinstance(ast[3][3][0], str) # string

    assert isinstance(ast[3][3][1], Tag) and ast[3][3][1].tag_type == 'i'  # i tag
    assert ast[3][3][1].tag_content == "first"  # i contents

    assert isinstance(ast[3][3][2], str)  # string

    assert isinstance(ast[4], str)  # string

    assert len(ast) == 5
