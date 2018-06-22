"""
Process AST functions for typography.
"""
import regex

from ..tags import Tag
from . import settings


re_endash = regex.compile(r"[\s\u00a0]*(--|\u2013)[\s\u00a0]*")
re_emdash = regex.compile(r"[\s\u00a0]*(---|\u2014)[\s\u00a0]*")
re_apostrophe = regex.compile(r"(?<=\w)'(?=\w)")
re_single_start = regex.compile(r"(?<!\w)'(?=\S)")
re_single_end = regex.compile(r"(?<=\S)'(?!\w)")
re_double_start = regex.compile(r"(?<!\w)\"(?=\S)")
re_double_end = regex.compile(r"(?<=\S)\"(?!\w)")


def process_typography(ast=None, context=None, src_filepath=None, level=1):
    """Process the typography for an AST.

    .. note:: This function should be run after process_ast.

    Parameters
    ----------
    ast : list
        An optional AST to build from or a list of strings.
    context : dict, optional
        The context with values for the document.
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
    if isinstance(ast, str):
        # Process the ast if it's simply a string
        ast = re_emdash.sub('\u2014', ast)
        ast = re_endash.sub('\u2013', ast)
        ast = re_apostrophe.sub('’', ast)
        ast = re_single_start.sub('‘', ast)
        ast = re_single_end.sub('’', ast)
        ast = re_double_start.sub('“', ast)
        ast = re_double_end.sub('”', ast)
        return ast

    elif isinstance(ast, Tag) and ast.name not in settings.verbatim_tags:
        # Process the tag (as long as it's not a verbatim tag)
        ast.content = process_typography(ast.content, context, src_filepath,
                                         level+1)
        return ast

    elif isinstance(ast, Tag):
        # For verbatim tags, simply return the ast unprocessed.
        return ast

    # The ast at this point should be a list. Process each ast element and
    # find text elements
    new_ast = []
    for i in ast:
        # Determine the type of AST element and process it further if it's
        # a string or defer the processing recursively
        if isinstance(i, str) or isinstance(i, list):
            i = process_typography(i, context, src_filepath, level+1)

        elif isinstance(i, Tag) and i.name not in settings.verbatim_tags:
            i.content = process_typography(i.content, context,
                                           src_filepath, level + 1)
        new_ast.append(i)

    return new_ast


def process_context_typography(context):
    """Process typography in the tags of the given context.

    This function parses the typography of tags in the context. Consequently,
    it should be executed after tags are created in the context.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.

    """
    # Go through the entries in the context and determine which are tags
    for k, v in context.items():
        # Skip macros and non-string entries
        if (k.startswith('@') or
           not (isinstance(v, Tag) or isinstance(v, str))):
            continue

        # Process the entry in the context
        ast = process_typography(ast=v, context=context,
                                 src_filepath='')

        # Replace the context entry
        context[k] = ast

    return None
