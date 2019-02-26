"""
Functions to clean ASTs.
"""
from itertools import groupby


def clean_strings(ast):
    """Clean an AST by group strings and removing empty strings.

    .. note:: This function intentionally does not replace lists; it only
              replaces items in lists.

    Parameters
    ----------
    ast : list, str or :obj:`Tag <disseminate.tags.core.Tag>`
        An AST comprising a strings, tags or lists of both.

    Returns
    -------
    processed_ast
        The AST with the strings grouped and cleaned up

    Examples
    --------
    >>> clean_strings(ast=['a', 'b', '', 3, '', 4, 5, 'f'])
    ['ab', 3, 4, 5, 'f']
    >>> clean_strings(ast=['a', 'b', 'c', 3, 'd', 'e', 4, 5, 'f'])
    ['abc', 3, 'de', 4, 5, 'f']
    """
    if hasattr(ast, 'content'):
        ast.content = clean_strings(ast.content)
    elif isinstance(ast, list):
        # Remove empty strings
        l = list(filter(bool, ast))
        ast.clear()
        ast += l

        # Join consecutive string elements
        l = []
        for cond, group in groupby(ast, key=lambda x: isinstance(x, str)):
            if cond:
                l.append(''.join(group))
            else:
                l += list(group)
        ast.clear()
        ast += l

        # Iterate over the items
        for i, item in enumerate(ast):
            if not isinstance(item, str):
                ast[i] = clean_strings(item)

    return ast
