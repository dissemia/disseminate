"""
Utility functions for ASTs.
"""
from ..tags import Tag


def print_ast(ast, level=1):
    """Pretty print an AST with one entry per line and indentation for nested
    levels.

    Parameters
    ----------
    ast : list of str or tags
        The AST is a list of strings or tags, which may themselves
        contain strings or nested lists.
    level : int, optional
        The current level of the ast.
    """
    assert isinstance(ast, list)

    print()
    for count, item in enumerate(ast, 1):
        if isinstance(item, str):
            print("{}.{}:".format(level, count),
                  "  " * level, repr(item))
            continue

        if (hasattr(item, 'content')
            and not isinstance(item.content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item)

        if (hasattr(item, 'content')
            and isinstance(item.content, list)):

            print("{}.{}:".format(level, count),
                  "  " * level, item.name, "{")
            print_ast(item.content, level + 1)
            print("    " + "  " * level + "}")


def count_ast_lines(ast, line_number=1):
    """Count the number of lines in an AST or AST element.

    Parameters
    ----------
    ast : list of str or tags
        The AST is a list of strings or tags, which may themselves
        contain strings or nested lists.
    line_number : int, optional
        The initial line number to use.

    Returns
    count : int
        The line number count.
    """
    if isinstance(ast, str):
        line_number += ast.count('\n')
        return line_number
    if isinstance(ast, Tag):
        if isinstance(ast.content, str):
            line_number += ast.content.count('\n')
            return line_number
        elif isinstance(ast.content, list):
            ast = ast.content
        elif isinstance(ast.content, Tag):
            line_number = count_ast_lines(ast.content, line_number)

    for i in ast:
        line_number = count_ast_lines(i, line_number)

    return line_number
