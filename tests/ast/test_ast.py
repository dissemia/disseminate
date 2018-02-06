"""
Tests for the ast sub-module.
"""
import pytest
import lxml.html

from disseminate.ast import process_ast
from disseminate.ast.validate import ParseError
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

test_txt = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with bolded text as an example.
    
      
      This is my first figure.
    

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph."""

test_html = """<span class="root">
    This is my test document. It has multiple paragraphs.

    Here is a new one with <strong>bolded</strong> text as an example.
    <span class=\"marginfig\">
      <img src="media/files"/>
      <caption>This is my <i>first</i> figure.</caption>
    </span>

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph.</span>
"""

test_invalid = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
"""

test_header = """
---
title: My first title
author: Justin L Lorieau
---
"""


def test_ast_basic_string():
    """Test the parsing of a basic string into an AST."""

    ast = process_ast(test)

    test_pieces = test.splitlines()

    # Check the AST piece-by-piece
    assert isinstance(ast, Tag) and ast.name == 'root' # root tag

    content = ast.content

    assert isinstance(content[1], Tag) and content[1].name == 'b'

    assert isinstance(content[2], str) # string

    assert isinstance(content[3], Tag) and content[3].name == 'marginfig'
    assert isinstance(content[3].content, list)  # margin tag has subtags

    assert isinstance(content[3][0], str) # string

    assert isinstance(content[3][1], Tag) and content[3][1].name == 'img'
    assert not content[3][1].content  # img contents should be parsed and empty

    assert isinstance(content[3][2], str)  # string

    assert isinstance(content[3][3], Tag) and content[3][3].name == 'caption'
    assert isinstance(content[3][3].content, list)  # contents includes
                                                    # strings and tags

    assert isinstance(content[3][3][0], str) # string

    assert isinstance(content[3][3][1], Tag) and content[3][3][1].name == 'i'
    assert content[3][3][1].content == "first"  # i contents

    assert isinstance(content[3][3][2], str)  # string

    assert isinstance(content[4], str)  # string

    assert len(content) == 5


def test_ast_validation():
    """Test the correct validation when parsing an AST."""

    # Process a string with an open tag
    with pytest.raises(ParseError) as e:
        ast = process_ast(test_invalid)

    # The error should pop up in line 4
    assert "line 4" in str(e.value)

    # Validate closing bracket


def test_default_conversion():
    """Test the default conversion of an AST into a text string."""

    # Generate the txt string
    ast = process_ast(test)
    txt = ast.default()

    assert txt == test_txt


def test_basic_html_conversion():
    """Test the generation of html strings from tags."""

    # Generate the html string
    ast = process_ast(test)
    html = ast.html()
    assert html == test_html

    # Validate the html
    root = lxml.html.fragment_fromstring(html)
    root_iter = root.iter()

    # verify each element
    e1 = next(root_iter)
    assert e1.tag == 'span'
    assert isinstance(e1.text, str) and len(e1.text) > 0
    assert e1.attrib == {'class': 'root'}

    e2 = next(root_iter)
    assert e2.tag == 'strong'
    assert isinstance(e2.text, str) and e2.text == 'bolded'
    assert e2.attrib == {}

    e3 = next(root_iter)
    assert e3.tag == 'span'
    assert isinstance(e3.text, str) and e3.text.strip() == ''
    assert e3.attrib == {'class': 'marginfig'}

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


def test_ast_with_header():
    """Tests the correct parsing of a header."""

    combined_test = test_header + test
    ast = process_ast(combined_test)

    # Check the contents  of the local_context
    assert 'title' in ast.local_context
    assert ast.local_context['title'] == 'My first title'

    assert 'author' in ast.local_context
    assert ast.local_context['author'] == 'Justin L Lorieau'

    # Check the correct rendering of the AST html
    html = ast.html()
    assert html == test_html


def test_local_context_update():
    """Tests that the local_context is properly updated in subsequent
    process_ast runs"""

    combined_test = test_header + test
    local_context = dict()
    global_context = dict()
    ast = process_ast(combined_test,
                      local_context=local_context,
                      global_context=global_context)

    # Check the contents  of the local_context
    assert 'title' in local_context
    assert local_context['title'] == 'My first title'

    assert 'author' in local_context
    assert local_context['author'] == 'Justin L Lorieau'

    # Now remove the header and make sure the 'author' and 'title' entries are
    # no longer in the context
    ast = process_ast(test,
                      local_context=local_context,
                      global_context=global_context)

    # Check the contents  of the local_context
    assert 'title' not in local_context
    assert 'author' not in local_context
