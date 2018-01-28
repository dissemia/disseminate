"""
Utility functions for ASTs.
"""


def print_ast(ast, level=1):
    """Pretty print an AST with one entry per line and indentation for nested
    levels.

    Parameters
    ----------
    ast : list of str or list
        The AST is a list of string or nested lists, which may themselves
        containt strings or nested lists.
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
