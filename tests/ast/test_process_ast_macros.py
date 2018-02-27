"""
Test the interfacing of process_ast with macros
"""
from disseminate.ast import process_ast
from disseminate.macros import replace_macros


def test_process_ast_basic_macros():
    """Test process_ast with basic macros."""

    # 1. Try a basic side note.
    test1 = """The first pulse@sidenote{A                                                                                                             
    pulse rotates the magnetization by with a phase of `x'.}"""

    # Replace the macros and process ast
    local_context = dict()
    global_context = dict()
    s = replace_macros(test1, local_context, global_context)
    ast = process_ast([s], local_context, global_context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 2. Try including a standard macro
    test2 = """The first pulse@sidenote{A @1H
    pulse rotates the magnetization with a phase of `x'.}"""

    s = replace_macros(test2, local_context, global_context)
    ast = process_ast([s], local_context, global_context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'

    # 3. Try including a undefined macro
    test2 = """The first pulse@sidenote{A @undefined 
        pulse rotates the magnetization with a phase of `x'.}"""

    s = replace_macros(test2, local_context, global_context)
    ast = process_ast([s], local_context, global_context)

    # Make sure the sidenote tag is in the ast
    assert ast.content[1].name == 'sidenote'


def test_process_ast_nested_macros():
    """Test the process_ast with a nested macros."""

    local_context = {'macros': {'@p90x': '90@deg@sub{x}'}}
    global_context = {}

    result = replace_macros("My @p90x pulse.", local_context=local_context,
                            global_context=global_context)
    ast = process_ast([result], local_context=local_context,
                             global_context=global_context)
    assert ast.content[0] == 'My 90'
    assert (ast.content[1].name, ast.content[1].content) == ('symbol', 'deg')
    assert (ast.content[2].name, ast.content[2].content) == ('sub', 'x')
    assert ast.content[3] == ' pulse.'
