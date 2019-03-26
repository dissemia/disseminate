"""
Test the proces_paragraphs function.
"""
from disseminate.ast import (process_ast, process_paragraphs,
                             process_context_asts, process_context_paragraphs)
from disseminate.ast.paragraph import (group_paragraphs, clean_paragraphs,
                                       assign_paragraph_roles)
from disseminate.macros import process_context_macros
from disseminate.tags import Tag
from disseminate.tags.text import P
from disseminate.header import load_header
from disseminate.paths import SourcePath


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


def test_group_paragraphs():
    """Test the group_paragraphs function."""

    # 1. Test basic lists of items and strings with newlines
    group = group_paragraphs([1, 2, 'three', 'four\n\nfive', 6,
                              'seven\n\neight'])
    assert group == [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]

    # Running it again will not change the result
    group = group_paragraphs(group)
    assert group == [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]

    # 2. Test a basic string with newlines
    group = group_paragraphs("One, two\nthree\n\nFour, five\nSix\n\nSeven")
    assert group == [['One, two\nthree'], ['Four, five\nSix'], ['Seven']]

    group = group_paragraphs(group)
    assert group == [['One, two\nthree'], ['Four, five\nSix'], ['Seven']]

    group = group_paragraphs([1, 2, 'three', 'four\n\n\n\nfive', 6, '\n\n',
                      'seven\n\neight'])
    assert group == [[1, 2, 'three', 'four'], ['five', 6], ['seven'], ['eight']]

    # 3. Test string objects with 'include_paragraphs' attributes
    class AltInt(int):
        include_paragraphs = True

    group = group_paragraphs([AltInt(1), AltInt(2), 'three', 'four\n\nfive',
                              AltInt(6), 'seven\n\neight'])
    assert group == [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]

    group = group_paragraphs(group)
    assert group == [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]

    ast = [AltInt(1), AltInt(2), 'three', 'four\n\nfive', AltInt(6),
           'seven\n\neight']
    ast[0].include_paragraphs = False
    ast[1].include_paragraphs = False
    ast[4].include_paragraphs = False
    group = group_paragraphs(ast)
    assert group == [1, 2, ['three', 'four'], ['five'], 6, ['seven'], ['eight']]

    group = group_paragraphs(group)
    assert group == [1, 2, ['three', 'four'], ['five'], 6, ['seven'], ['eight']]


def test_clean_paragraphs():
    """Test the clean_paragraphs function."""

    # 1. Test a basic list of items and strings with newlines
    group = group_paragraphs([1, 2, 'three', 'four\n\nfive', 6,
                              'seven\n\neight'])
    group = clean_paragraphs(group)
    assert group == [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]

    # 2. Test a list of items with only newlines
    group = group_paragraphs([1, 2, 'three', 'four\n\n\n\nfive', 6, '\n\n',
                              'seven\n\neight'])
    group = clean_paragraphs(group)
    assert group == [[1, 2, 'three', 'four'], ['five', 6], ['seven'],
                     ['eight']]


def test_assign_paragraph_roles(context_cls):
    """Test the assign_paragraph_roles function."""

    context = context_cls()

    # 1. Test a basic list of items and strings with newlines
    tag1 = Tag(name='tag1', content='', attributes=tuple(), context=context)
    tag2 = Tag(name='tag2', content='', attributes=tuple(), context=context)
    tag3 = Tag(name='tag3', content='', attributes=tuple(), context=context)

    group = group_paragraphs([tag1, tag2, 'three', 'four\n\nfive', tag3,
                              'seven\n\neight'])
    assert group[0][0].paragraph_role is None
    assert group[0][1].paragraph_role is None
    assert group[1][1].paragraph_role is None

    # Now assign the paragraph_roles
    assign_paragraph_roles(group)
    assert group[0][0].paragraph_role == 'inline'
    assert group[0][1].paragraph_role == 'inline'
    assert group[1][1].paragraph_role == 'inline'

    # 2. Test an example with a block tag
    tag1 = Tag(name='tag1', content='', attributes=tuple(), context=context)
    tag2 = Tag(name='tag2', content='', attributes=tuple(), context=context)
    tag3 = Tag(name='tag3', content='', attributes=tuple(), context=context)

    group = group_paragraphs([tag1, tag2, 'three', 'four\n\n', tag3,
                              '\n\neight'])
    print('group:', group)
    assert group[0][0].paragraph_role is None
    assert group[0][1].paragraph_role is None
    assert group[1][0].paragraph_role is None

    # Now assign the paragraph_roles
    assign_paragraph_roles(group)
    assert group[0][0].paragraph_role == 'inline'
    assert group[0][1].paragraph_role == 'inline'
    assert group[1][0].paragraph_role == 'block'


def test_group_paragraphs_ast(context_cls):
    """Test the group_paragraphs function with an AST generated by
    process_ast."""

    # 1. Test with an ast object generated by process_ast
    context = context_cls()
    ast = process_ast(test_paragraphs, context=context)
    group = group_paragraphs(ast.content)

    assert group[0][0] == '\nThis is my '
    assert group[0][1].name, group[0][1].content == ('b', 'first')
    assert group[0][2] == ' paragraph.'

    assert group[1][0] == 'This is my '
    assert group[1][1].name, group[1][1].content == ('i', 'second')
    assert group[1][2] == ". It has a multiple\nlines."

    assert group[2][0] == "This paragraph has a note. "
    assert group[2][1].name == 'note'
    assert group[2][1].content == ("\n\nThis note has multiple lines.\n\n"
                                   "and multiple paragraphs.\n")

    assert group[3][0] == "This is the fourth paragraph"

    assert group[4].name == 'section'
    assert group[4].content == 'A heading (no paragraph'

    assert group[5][0] == 'A fifth paragraph.'

    assert group[6][0] == 'Here is a new one with '
    assert group[6][1].name, group[6][1].content == ('b', 'bolded')
    assert group[6][2] == ' text as an example.\n    '
    assert group[6][3].name == 'marginfig'

    assert group[7][0] == 'My final paragraph.\n'

    # Test to make sure group_paragraphs can be run more than once
    group2 = group_paragraphs(group)

    assert group == group2


def test_assign_paragraph_roles_ast(context_cls):
    """Test the assign_paragraph_rols function with an AST generated by
    process_ast."""

    # 1. Test with an ast object generated by process_ast
    context = context_cls()
    ast = process_ast(test_paragraphs, context=context)
    group = group_paragraphs(ast.content)
    assign_paragraph_roles(group)

    assert group[0][1].paragraph_role == 'inline'
    assert group[1][1].paragraph_role == 'inline'
    assert group[2][1].paragraph_role == 'inline'
    assert group[4].paragraph_role is None  # Heading is not in a paragraph
    assert group[6][1].paragraph_role == 'inline'
    assert group[6][3].paragraph_role == 'inline'


def test_process_paragraphs(context_cls):
    """Test the process_paragraphs function"""

    context = context_cls()
    ast = process_ast(test_paragraphs, context=context)
    ast = process_paragraphs(ast, context=context)

    # Check the individual items of the ast.
    assert ast.name == 'root'
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

    assert ast.name == 'root'
    assert ast.content[0].name == 'section'
    assert ast.content[0].content == 'A heading with leading spaces'
    assert ast.content[1].name == 'p'
    assert ast.content[1].content == '\n  \n  This is my paragraph.\n'


def test_process_paragraphs_macros(context_cls):
    """Test the process_paragraphs function with macros."""

    # setup a test ast with a macro
    context = context_cls(**{'p90x': '90@deg@sub{x}'})

    result = process_ast("My @p90x pulse.", context=context)
    ast = process_paragraphs(result, context=context)
    assert ast.name =='root'
    assert ast[0].name == 'p'
    assert ast[0].content[0] == 'My '
    assert ast[0].content[1].name == 'p90x'
    assert ast[0].content[2] == ' pulse.'

    # Test paragraph processing with a macro and tag
    result = process_ast("My @b{y = x} @1H pulse.", context=context)
    ast = process_paragraphs(result, context=context)
    assert ast.name == 'root'
    assert ast[0].name == 'p'
    assert ast[0].content[0] == 'My '
    assert ast[0].content[1].name == 'b'
    assert ast[0].content[2] == ' '
    assert ast[0].content[3].name == '1H'
    assert ast[0].content[4] == ' pulse.'


def test_process_paragraphs_newlines(context_cls):
    """Test the preservation of newlines in a parapgraph with macros."""

    text = """The purpose of the @abrv{INEPT} sequenceMorris1979 is to 
    transfer the large magnetization from high-@gamma nuclei, like @1H or
    @19F, to low-@gamma nuclei (labeled 'X'), like @13C and @15N."""

    context = context_cls(**{'@1H': '@sup{1}H',
                             '@13C': '@sup{13}C', '@15N': '@sup{15}N',
                             '@19F': '@sup{19}F', '@gamma': '@symbol{gamma}',
                             'src_filepath': '.',
                             'body': text})

    process_context_macros(context=context)
    process_context_asts(context=context)
    result = process_paragraphs(context['body'], context=context)

    result_html = result.html
    assert 'is to \n    transfer' in result_html
    assert '<sup>1</sup>H or\n' in result_html
    assert 'or\n    <sup>19</sup>F' in result_html


def test_process_context_paragraphs(context_cls):
    """Test the process_context_paragraphs function."""

    # 1. Test a basic paragraphs example. In this first case, there is no
    #    'process_paragraphs' entry in the context, so no entry in the context
    #    will be processed

    context = context_cls(src_filepath=SourcePath(''),
                          body=test_paragraphs2)

    process_context_asts(context)
    process_context_paragraphs(context)

    ast = context['body']

    assert ast.name == 'body'
    assert ast.content[0] == '\n  '
    assert ast.content[1].name == 'section'
    assert ast.content[1].content == 'A heading with leading spaces'
    assert ast.content[2] == '\n  \n  This is my paragraph.\n'

    # 2. Test a basic paragraphs example. In this second case, there is an
    #    'process_paragraphs' entry in the context, so the 'body' entry in the
    #    context will be processed

    context = context_cls(src_filepath=SourcePath(''),
                          process_paragraphs=['body'],
                          body=test_paragraphs2)

    process_context_asts(context)
    process_context_paragraphs(context)

    ast = context['body']

    assert ast.name == 'body'
    assert ast.content[0].name == 'section'
    assert ast.content[0].content == 'A heading with leading spaces'
    assert ast.content[1].name == 'p'
    assert ast.content[1].content == '\n  \n  This is my paragraph.\n'

    # 3. Test a header processing
    header = """
    ---
    title: My @i{first} title
    author: Justin L Lorieau
    targets: html, tex
    macro: @i{example}
    ---
    This is my @macro body.
    """

    # Load the header into a context

    context = context_cls(body=header, src_filepath=SourcePath(''))
    load_header(context)

    # Now process the context entries
    process_context_asts(context)
    process_context_paragraphs(context)

    # Check the entries
    assert isinstance(context['title'], Tag)
    assert context['title'].name == 'title'
    assert context['title'].content[0] == 'My '
    assert context['title'].content[1].name == 'i'
    assert context['title'].content[1].content == 'first'
    assert context['title'].content[2] == ' title'

    assert isinstance(context['author'], str)
    assert context['author'] == 'Justin L Lorieau'

    assert isinstance(context['targets'], str)
    assert context['targets'] == 'html, tex'

    assert isinstance(context['macro'], Tag)
    assert context['macro'].name == 'i'
    assert context['macro'].content == 'example'

    assert isinstance(context['body'], Tag)
    assert context['body'].name == 'body'
    assert context['body'].content[0] == '    This is my '
    assert context['body'].content[1].name == 'macro'
    assert context['body'].content[2] == ' body.\n    '
