"""
Utility functions for ASTs.
"""
from ..tags import Tag


def flatten_ast(ast, filter_tags=True):
    """Convert an AST into a flat list of tags and text items.

    Parameters
    ----------
    ast : list of str or tags
        The AST is a list of strings or tags, which may themselves
        contain strings or nested lists.
    filter_tags : bool, optional
        If True, only Tag objects will be returned in the

    """
    flattened_list = [ast]

    # Process the AST's contents if present
    if hasattr(ast, 'content'):
        ast = ast.content

    # Convert the AST to a list, if it isn't already
    if not hasattr(ast, '__iter__'):
        ast = [ast]

    # Traverse the items and process each
    for item in ast:
        # Add the item to the ast
        flattened_list.append(item)

        # Process tag's sub-items, if present
        if hasattr(item, 'content') and isinstance(item.content, list):
            # Process lists recursively
            flattened_list += flatten_ast(item.content,
                                          filter_tags=filter_tags)

    if filter_tags:
        return list(filter(lambda i: isinstance(i, Tag), flattened_list))
    else:
        return flattened_list


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
