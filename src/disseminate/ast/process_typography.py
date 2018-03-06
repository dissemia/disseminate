"""
Process AST functions for typography.
"""
import regex

from ..tags import Tag

re_endash = regex.compile(r"[\s\u00a0]*(--|\u2013)[\s\u00a0]*")
re_emdash = regex.compile(r"[\s\u00a0]*(---|\u2014)[\s\u00a0]*")
re_apostrophe = regex.compile(r"(?<=\w)'(?=\w)")
re_single_start = regex.compile(r"(?<!\w)'(?=\S)")
re_single_end = regex.compile(r"(?<=\S)'(?!\w)")
re_double_start = regex.compile(r"(?<!\w)\"(?=\S)")
re_double_end = regex.compile(r"(?<=\S)\"(?!\w)")


def process_typography(ast=None, local_context=None, global_context=None,
                       src_filepath=None, level=1):
    """Process the typography for an AST.

    .. note:: This function should be run after process_ast.

    Parameters
    ----------
    ast : list
        An optional AST to build from or a list of strings.
    local_context : dict, optional
        The context with values for the current document. (local)
    global_context : dict, optional
        The context with values for all documents in a project. (global)
    src_filepath : str, optional
        The path for the document (source markup) file being processed.
    level : int, optional
        The current level of the ast.

    Returns
    -------
    ast : :obj:`disseminate.Tag`
        The AST is a root tag with a content comprising a list of tags or
        strings.
    """
    # Process the ast if it's simply a string
    if isinstance(ast, str):
        ast = re_emdash.sub('\u2014', ast)
        ast = re_endash.sub('\u2013', ast)
        ast = re_apostrophe.sub('’', ast)
        ast = re_single_start.sub('‘', ast)
        ast = re_single_end.sub('’', ast)
        ast = re_double_start.sub('“', ast)
        ast = re_double_end.sub('”', ast)
        return ast

    elif isinstance(ast, Tag):
        ast.content = process_typography(ast.content,
                                         local_context, global_context,
                                         src_filepath, level+1)
        return ast

    # Process each ast element and find text elements
    new_ast = []
    for i in ast:
        # Determine the type of AST element and process it further if it's
        # a string or defer the processing recursively
        if isinstance(i, str) or isinstance(i, list):
            i = process_typography(i, local_context, global_context,
                                   src_filepath, level+1)
            new_ast.append(i)

        elif isinstance(i, Tag):
            i.content = process_typography(i.content,
                                           local_context, global_context,
                                           src_filepath, level + 1)
            new_ast.append(i)

    return new_ast