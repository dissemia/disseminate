"""
Test the proces_paragraphs function.
"""
from disseminate.ast import (process_ast, process_paragraphs,
                             process_context_asts, process_context_paragraphs)
from disseminate.tags.text import P
from disseminate.paths import SourcePath
from disseminate import settings


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
      @b{test}
    }

My final paragraph.
"""

test_paragraphs2 = """
  @section{A heading with leading spaces}
  
  This is my paragraph.
"""


def test_process_paragraphs(context_cls):
    """Test the process_paragraphs function"""

    context = context_cls()
    ast = process_ast(test_paragraphs, context=context)
    ast = process_paragraphs(ast, context=context)

    # Check the individual items of the ast.
    assert isinstance(ast[0], P)
    assert ast[0].content[0] == '\nThis is my '
    assert ast[0].content[1].name == 'b'  # bolded
    assert ast[0].content[2] == ' paragraph.'

    assert isinstance(ast[1], P)
    assert ast[1].content[0] == 'This is my '
    assert ast[1].content[1].name == 'i'  # italics
    assert ast[1].content[2] == '. It has a multiple\nlines.'

    assert isinstance(ast[2], P)
    assert ast[2].content[0] == 'This paragraph has a note. '
    assert ast[2].content[1].name == 'note'  # note

    assert isinstance(ast[3], P)
    assert ast[3].content == 'This is the fourth paragraph'

    assert ast[4].name == 'section'
    assert ast[4].content == 'A heading (no paragraph'

    assert isinstance(ast[5], P)
    assert ast[5].content == 'A fifth paragraph.'

    assert isinstance(ast[6], P)
    assert ast[6].content[0] == 'Here is a new one with '
    assert ast[6].content[1].name == 'b'  # bolded
    assert ast[6].content[2] == ' text as an example.\n    '
    assert ast[6].content[3].name == 'marginfig'  # margin tag

    assert isinstance(ast[7], P)
    assert ast[7].content == 'My final paragraph.\n'


def test_process_paragraphs_leading_spaces(context_cls):
    """Test the process_paragraphs function when trailing spaces are present.
    """

    context = context_cls()
    ast = process_ast(test_paragraphs2, context=context)
    ast = process_paragraphs(ast, context=context)

    assert ast.content[0] == '\n  '
    assert ast.content[1].name == 'section'
    assert ast.content[2] == '\n  \n  This is my paragraph.\n'


def test_process_context_paragraphs(context_cls):
    """Test the process_context_paragraphs function."""

    body_attr = settings.body_attr

    context_cls.validation_types = {'src_filepath': str}
    context = context_cls(src_filepath='', **{body_attr: test_paragraphs2})

    process_context_asts(context)
    process_context_paragraphs(context)

    ast = context[body_attr]

    assert ast.content[0] == '\n  '
    assert ast.content[1].name == 'section'
    assert ast.content[2] == '\n  \n  This is my paragraph.\n'


def test_process_paragraphs_edgecases(context_cls):
    """Test the process_paragraphs function for a series of edge cases."""

    # Test a basic string with no tags. This create a root tag
    context = context_cls()
    test_edge = "basic"
    ast = process_paragraphs(test_edge, context=context)

    assert ast.name == 'root'
    assert ast.content.name == 'p'
    assert ast.content.content == 'basic'
    assert ast.tex == '\nbasic\n'


def test_process_paragraphs_macros(context_cls):
    """Test the process_paragraphs function with macros."""

    # setup a test ast with a macro
    context = context_cls(**{'p90x': '90@deg@sub{x}'})

    result = process_ast("My @p90x pulse.", context=context)
    ast = process_paragraphs(result, context=context)
    assert ast.content.content[0] == 'My '
    assert ast.content.content[1].name == 'p90x'
    assert ast.content.content[2] == ' pulse.'

    # Test paragraph processing with a macro and tag
    result = process_ast("My @b{y = x} @1H pulse.", context=context)
    ast = process_paragraphs(result, context=context)
    assert ast.name == 'root'
    assert ast.content.name == 'p'
    assert ast.content.content[0] == 'My '
    assert ast.content.content[1].name == 'b'
    assert ast.content.content[2] == ' '
    assert ast.content.content[3].name == '1H'
    assert ast.content.content[4] == ' pulse.'

    # Test paragraph processing after process_ast
    ast = process_ast(result, context=context)
    ast = process_paragraphs(ast, context=context)


def test_process_paragraphs_newlines(context_cls):
    """Test the preservation of newlines in a parapgraph with macros."""

    text = """The purpose of the @abrv{INEPT} sequenceMorris1979 is to 
    transfer the large magnetization from high-@gamma nuclei, like @1H or
    @19F, to low-@gamma nuclei (labeled 'X'), like @13C and @15N."""

    context = context_cls(**{'1H': '@sup{1}H',
                             '13C': '@sup{13}C', '15N': '@sup{15}N',
                             '19F': '@sup{19}F', 'gamma': '@symbol{gamma}',
                             'src_filepath': '.',
                             'body': text})

    process_context_asts(context=context)
    result = process_paragraphs(context['body'], context=context)
    assert 'or\n    <span class="19f"><sup>19</sup>F</span>' in result.html
