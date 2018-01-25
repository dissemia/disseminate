"""
Tests for the ast sub-module.
"""
import pytest
from lxml import etree

from disseminate.ast import process_ast, convert_html, print_ast, ParseError
from disseminate.tags import Tag


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph."""

test_invalid = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
"""


def test_ast_basic_string():
    """Test the parsing of a basic string into an AST."""

    ast = process_ast(test)

    test_pieces = test.splitlines()

    # Check the AST piece-by-piece
    assert ast[0] == test[0:len(ast[0])] # string

    assert isinstance(ast[1], Tag) and ast[1].name == 'b' # b tag

    assert isinstance(ast[2], str) # string

    assert isinstance(ast[3], Tag) and ast[3].name == 'marginfig'
    assert isinstance(ast[3].content, list)  # margin tag has subtags

    assert isinstance(ast[3][0], str) # string

    assert isinstance(ast[3][1], Tag) and ast[3][1].name == 'img'
    assert not ast[3][1].content  # img contents should be parsed and empty

    assert isinstance(ast[3][2], str)  # string

    assert isinstance(ast[3][3], Tag) and ast[3][3].name == 'caption'
    assert isinstance(ast[3][3].content, list)  # contents includes
                                                    # strings and tags

    assert isinstance(ast[3][3][0], str) # string

    assert isinstance(ast[3][3][1], Tag) and ast[3][3][1].name == 'i'
    assert ast[3][3][1].content == "first"  # i contents

    assert isinstance(ast[3][3][2], str)  # string

    assert isinstance(ast[4], str)  # string

    assert len(ast) == 5


def test_basic_html_conversion():
    """Test the generation of html strings from tags."""

    # Generate the html string
    ast = process_ast(test)
    html = convert_html(ast)

    # Validate the html
    root = etree.fromstring(html)
    root_iter = root.iter()

    # verify each element
    e1 = next(root_iter)
    assert e1.tag == 'body'
    assert isinstance(e1.text, str) and len(e1.text) > 0
    assert e1.attrib == {}

    e2 = next(root_iter)
    assert e2.tag == 'b'
    assert isinstance(e2.text, str) and e2.text == 'bolded'
    assert e2.attrib == {}

    e3 = next(root_iter)
    assert e3.tag == 'marginfig'
    assert isinstance(e3.text, str) and e3.text.strip() == ''
    assert e3.attrib == {}

    e4 = next(root_iter)
    assert e4.tag == 'img'
    assert e4.text is None
    assert e4.attrib == {'src': 'media/files'}

    e5 = next(root_iter)
    assert e5.tag == 'caption'
    assert isinstance(e5.text, str) and e5.text == 'This is my '
    assert e5.attrib == {}

    e6 = next(root_iter)
    assert e6.tag == 'i'
    assert isinstance(e6.text, str) and e6.text == 'first'
    assert e6.attrib == {}

    with pytest.raises(StopIteration):
        e7 = next(root_iter)


def test_ast_validation():
    """Test the correct validation when parsing an AST."""

    # Process a string with an open tag
    with pytest.raises(ParseError) as e:
        ast = process_ast(test_invalid)

    # The error should pop up in line 4
    assert "line 4" in str(e.value)

    # Validate closing bracket