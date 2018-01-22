from pprint import pprint

import pytest

from disseminate import process_ast
from disseminate import Tag
from disseminate.tags import convert_html
from disseminate.ast import print_ast


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph."""


def test_ast_basic_string():
    """Test the parsing of a basic string into an AST."""

    ast = process_ast(test)

    test_pieces = test.splitlines()

    # Check the AST piece-by-piece
    assert ast[0] == test[0:len(ast[0])] # string

    assert isinstance(ast[1], Tag) and ast[1].tag_type == 'b' # b tag

    assert isinstance(ast[2], str) # string

    assert isinstance(ast[3], Tag) and ast[3].tag_type == 'marginfig'
    assert isinstance(ast[3].tag_content, list)  # margin tag has subtags

    assert isinstance(ast[3][0], str) # string

    assert isinstance(ast[3][1], Tag) and ast[3][1].tag_type == 'img'
    assert not ast[3][1].tag_content  # img contents should be parsed and emptu

    assert isinstance(ast[3][2], str)  # string

    assert isinstance(ast[3][3], Tag) and ast[3][3].tag_type == 'caption'
    assert isinstance(ast[3][3].tag_content, list)  # contents includes
                                                    # strings and tags

    assert isinstance(ast[3][3][0], str) # string

    assert isinstance(ast[3][3][1], Tag) and ast[3][3][1].tag_type == 'i'
    assert ast[3][3][1].tag_content == "first"  # i contents

    assert isinstance(ast[3][3][2], str)  # string

    assert isinstance(ast[4], str)  # string

    assert len(ast) == 5


def test_html_conversion():
    """Test the generation of html strings from tags."""

    ast = process_ast(test)

    html = convert_html(ast)

    with open('tmp.html', 'w') as f:
        f.write(html)
