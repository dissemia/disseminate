"""
Test the interfacing of process_ast with macros
"""
from disseminate.ast import process_ast
from disseminate.macros import replace_macros


def test_process_ast_basic_macros(context_cls):
    """Test process_ast with basic macros."""

    context = context_cls()

    # 1. Try a basic side note.
    test1 = """The first pulse@sidenote{A                                                                                                             
    pulse rotates the magnetization by with a phase of `x'.}"""

    # Replace the macros and process ast
    test1 = replace_macros(test1, context)
    ast = process_ast(test1, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 2. Try including a standard macro
    test2 = """The first pulse@sidenote{A @1H
    pulse rotates the magnetization with a phase of `x'.}"""
    test2 = replace_macros(test2, context)
    ast = process_ast(test2, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 3. Try including a undefined macro
    test3 = """The first pulse@sidenote{A @undefined 
        pulse rotates the magnetization with a phase of `x'.}"""
    test3 = replace_macros(test3, context)
    ast = process_ast(test3, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'


def test_process_ast_nested_macros(context_cls):
    """Test the process_ast with a nested macros."""

    context = context_cls(**{'@p90x': '90@deg@sub{x}'})
    test1 = "My @p90x pulse."

    test1 = replace_macros(test1, context=context)
    ast = process_ast(test1, context=context)

    assert ast.content[0] == 'My 90'
    assert ast.content[1].name == 'deg'
    assert ast.content[2].name == 'sub'
    assert ast.content[3] == ' pulse.'

    assert ast.txt == 'My 90x pulse.'


def test_ast_recursive_macros(context_cls):
    """Tests the application of macros."""

    # 1. Test with a basic macro
    test1 = "This is my @test string."
    context = context_cls(**{'@test': 'substituted'})
    s = replace_macros(test1, context=context)
    ast1 = process_ast(s, context=context)
    assert ast1 == 'This is my substituted string.'

    # 2. Test with a recursive macro
    test21 = "This is my @test string."
    context = context_cls(**{'@test': 'substituted @test'})
    s = replace_macros(test21, context=context)
    ast21 = process_ast(s, context=context)
    assert ast21.txt == 'This is my substituted substituted  string.'

    # 3. Test with a cross-recursive macro

    context = context_cls(**{'@a': '@b', '@b': '@a'})
    context['a'] = replace_macros(context['@a'], context=context)
    context['b'] = replace_macros(context['@b'], context=context)
    context['a'] = process_ast(context['@a'], context=context)
    context['b'] = process_ast(context['@b'], context=context)
    assert context['@a'] == '@b'
    assert context['@b'] == '@a'


def test_ast_nested_macros_and_tags(context_cls):
    """Test the processing of AST with nested macros and tags."""

    context = context_cls(**{'@toc': '@toc{documents}'})

    # replace the macros
    context['@toc'] = replace_macros(context['@toc'], context)

    assert context['@toc'] == '@toc{documents}{documents}{documents}'

    # process the ast
    ast = process_ast(context['@toc'], context=context, root_name='toc')

    assert ast.name == 'toc'
    assert ast.toc_kind == 'documents'
