"""
Tests for the ast sub-module.
"""
import pytest
import lxml.html

from disseminate.ast import process_ast, process_context_asts
from disseminate.ast.validate import ParseError
from disseminate.tags import Tag
from disseminate import settings


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfigtag[offset=-1.0em]{
      @imgtag{media/files}
      @captiontag{This is my @i{first} figure.}
    }

    This is a @13C variable.

    Here is a new paragraph."""

test_txt = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with bolded text as an example.
    
      media/files
      This is my first figure.
    

    This is a  variable.

    Here is a new paragraph."""

test_html = """<span class="root">
    This is my test document. It has multiple paragraphs.

    Here is a new one with <strong>bolded</strong> text as an example.
    <span offset="-1.0em" class="marginfigtag">
      <span class="imgtag">media/files</span>
      <span class="captiontag">This is my <i>first</i> figure.</span>
    </span>

    This is a <span class="13c"/> variable.

    Here is a new paragraph.</span>
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

    # Check the AST piece-by-piece
    assert isinstance(ast, Tag) and ast.name == 'root'  # root tag

    content = ast.content

    assert isinstance(content[1], Tag) and content[1].name == 'b'

    assert isinstance(content[2], str)  # string

    assert isinstance(content[3], Tag) and content[3].name == 'marginfigtag'
    assert isinstance(content[3].content, list)  # margin tag has subtags

    assert isinstance(content[3][0], str)  # string

    assert isinstance(content[3][1], Tag) and content[3][1].name == 'imgtag'
    assert content[3][1].content == 'media/files'

    assert isinstance(content[3][2], str)  # string

    assert isinstance(content[3][3], Tag) and content[3][3].name == 'captiontag'
    assert isinstance(content[3][3].content, list)  # contents includes
                                                    # strings and tags

    assert isinstance(content[3][3][0], str) # string

    assert isinstance(content[3][3][1], Tag) and content[3][3][1].name == 'i'
    assert content[3][3][1].content == "first"  # i contents

    assert isinstance(content[3][3][2], str)  # string

    assert isinstance(content[4], str)  # string

    assert isinstance(content[5], Tag) and content[5].name == '13C'
    assert content[5].content == ''

    assert isinstance(content[6], str)  # string

    assert len(content) == 7

    # Now test a string with no tags
    ast = process_ast("test")

    assert isinstance(ast, Tag) and ast.name == 'root'  # root tag
    assert isinstance(ast.content, str)
    assert ast.content == 'test'


def test_ast_basic_string_no_tags():
    """Test the conversion of a string without tags."""

    ast = process_ast("  empty  ")
    assert type(ast.content) == str
    assert ast.content == "  empty  "


def test_default_conversion():
    """Test the default conversion of an AST into a text string."""

    # Generate the txt string
    ast = process_ast(test)
    txt = ast.default
    assert txt == test_txt


def test_process_context_asts(context_cls):
    """Test the process_context_asts function."""
    body_attr = settings.body_attr

    context_cls.validation_types = {'src_filepath': str}
    context = context_cls(src_filepath='', **{body_attr: test})

    process_context_asts(context)
    assert context[body_attr].default == test_txt


def test_double_convert():
    """Tests the default conversion run twice of an AST to make sure the
    AST stays the same."""

    # Generate the txt string
    ast = process_ast(test)
    txt = ast.default
    assert txt == test_txt

    # Generate the txt string
    ast2 = process_ast(ast)
    txt = ast2.default
    assert txt == test_txt

    assert ast == ast2


def test_ast_open_brace():
    """Test the identification of open braces (unclosed tags) in formatting
     an AST."""

    test_invalid = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @caption{This is my @i{first} figure.}
    """
    with pytest.raises(ParseError):
        ast = process_ast(test_invalid)


def test_ast_edge_cases():
    """Tests the processing of ASTs with edge cases of source markup files."""

    test1 = "This is my @marginfig{{Margin figure}}."
    ast = process_ast(test1)
    assert ast.content[0] == 'This is my '
    assert ast.content[1].name == 'marginfig'
    assert ast.content[1].content == '{Margin figure}'
    assert ast.content[2] == '.'


def test_ast_substitutions(context_cls):
    """Tests the application and recursion of substitution tags from the
    context."""

    # 1. Test with a basic substitution
    test1 = "This is my @test string."
    context = context_cls(test='substituted')
    ast1 = process_ast(test1, context=context)
    assert ast1.txt == 'This is my substituted string.'

    # 2. Test with a recursive substitution
    test21 = "This is my @test string."
    context = context_cls(test='substituted @test')
    ast21 = process_ast(test21, context=context)
    assert ast21.txt == 'This is my substituted @test string.'

    context = context_cls(test='substituted @test')
    ast22 = process_ast(context['test'], context=context)
    assert context['test'] == 'substituted @test'
    assert ast22.txt == 'substituted substituted @test'

    context = context_cls(test='substituted @test')
    context['test'] = process_ast(context['test'], context=context)
    assert context['test'].txt == 'substituted substituted '

    context['test'] = process_ast(context['test'], context=context)
    assert context['test'].txt == 'substituted '

    # 3. Test with a cross-recursive substitution
    context = {'a': '@b', 'b': '@a'}
    context['a'] = process_ast(context['b'], context=context)
    assert context['a'].txt == ''
    context['b'] = process_ast(context['a'], context=context)
    assert context['b'].txt == ''

    context = {'a': '@b', 'b': '@a'}
    context['a'] = process_ast(context['a'], context=context)
    context['b'] = process_ast(context['b'], context=context)
    assert context['a'].txt == ''
    assert context['b'].txt == ''


# html targets

def test_basic_triple_conversion():
    """Test the generation of html strings from tags after 3 conversions."""
    # Generate the html string and process the ast twice
    ast = process_ast(test)
    for i in range(3):
        html = ast.html

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
        assert e3.attrib == {'class': 'marginfigtag',
                             'offset': '-1.0em'}

        e4 = next(root_iter)
        assert e4.tag == 'span'
        assert e4.text == 'media/files'
        assert e4.attrib == {'class': 'imgtag'}

        e5 = next(root_iter)
        assert e5.tag == 'span'
        assert e5.text == 'This is my '
        assert e5.attrib == {'class': 'captiontag'}

        e6 = next(root_iter)
        assert e6.tag == 'i'
        assert isinstance(e6.text, str) and e6.text == 'first'
        assert e6.attrib == {}

        e7 = next(root_iter)
        assert e7.tag == 'span'
        assert e7.attrib == {'class': '13c'}

        with pytest.raises(StopIteration):
            e8 = next(root_iter)

        ast = process_ast(ast)
