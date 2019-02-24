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
    s = replace_macros(test1, context)
    ast = process_ast(s, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 2. Try including a standard macro
    test2 = """The first pulse@sidenote{A @1H
    pulse rotates the magnetization with a phase of `x'.}"""

    s = replace_macros(test2, context)
    ast = process_ast(s, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 3. Try including a undefined macro
    test2 = """The first pulse@sidenote{A @undefined 
        pulse rotates the magnetization with a phase of `x'.}"""

    s = replace_macros(test2, context)
    ast = process_ast(s, context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'


def test_process_ast_nested_macros(context_cls):
    """Test the process_ast with a nested macros."""

    context = context_cls(**{'@p90x': '90@deg@sub{x}'})

    result = replace_macros("My @p90x pulse.", context=context)
    ast = process_ast(result, context=context)
    assert ast.content[0] == 'My 90'
    assert (ast.content[1].name, ast.content[1].content) == ('sup', '○')
    assert (ast.content[2].name, ast.content[2].content) == ('sub', 'x')
    assert ast.content[3] == ' pulse.'
