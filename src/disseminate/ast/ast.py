"""
Functions for processing Abstract Syntax Trees (ASTs).
"""
import regex

from ..tags import TagFactory, Tag
from .validate import ValidateAndCleanAST
from . import settings


class AstException(Exception):
    """An error was encountered while processing the Abstract Syntax Tree"""
    pass


re_open_tag = regex.compile(r'@(?P<tag>[A-Za-z][\w]*)(?P<attributes>\[[^\]]+\])?{')
re_brace = regex.compile(r'[}{]')


def process_ast(ast=None, context=None, src_filepath=None, level=1):
    """Process an AST comprising a list of strings, lists or tags.

    .. note:: The AST processing should be able to reprocess the generated AST
              without making changes.

    .. warning:: The process_ast *can not* depend on the `local_context`
                 and `global_context` since these may not be fully populated
                 yet. However, it can populate these.

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
    ast : :obj:`disseminate.Tag`, list of ast elements or string
        The AST is a root tag with a content comprising a list of tags or
        strings.

    Raises
    ------
    AstException
        Raises an AstException if the max depth has been achieved
        (settings.ast_max_depth). This is an attempt to foil the Billion Laughs
        attack.
    """
    # Conduct initial tests
    if level >= settings.ast_max_depth:
        msg = ("The maximum depth of '{}' has been reached in the AST. "
               "Additional levels can be set by the 'settings.ast_max_depth'.")
        raise AstException(msg.format(settings.ast_max_depth))

    # Setup the AST and determine the kind of ast passed and how to process
    # it.
    context = context if isinstance(context, dict) else dict()

    new_ast = []
    process = lambda x: process_ast(x, context, src_filepath, level+1)

    # Look at the ast and process it depending on whether it's a string, tag
    # or list
    if isinstance(ast, str):
        text = ast
    elif isinstance(ast, list):
        return list(map(process, ast))
    elif isinstance(ast, Tag):
        if isinstance(ast.content, str) or isinstance(ast.content, Tag):
            ast.content = process(ast.content)
        elif isinstance(ast.content, list):
            ast.content = list(map(process, ast.content))
        return ast

    # The following only processes text

    # Setup the tag factor to generate tags
    factory = TagFactory()

    # The parser starts at the start of the text string
    position = 0

    # find open tags
    match_tag = re_open_tag.search(text[position:])

    # Process the tag
    while match_tag:
        # Add the text up to this tag the match start/end are relative to the
        # truncated text[position:] string, so the match start position has
        # to be offset when referencing the full 'text' string
        match_tag_start = position + match_tag.start()
        new_ast.append(text[position:match_tag_start])

        # Push up the position to the end of the tag match
        position += match_tag.end()
        start_position = position

        # Find open and close braces and advance the position
        # up until the match closing brace is found
        brace_level = 1
        match = re_brace.search(text[position:])
        while match and 0 < brace_level < 10:
            # Increment or decrement the match
            if match.group() == '}':
                brace_level -= 1
            elif match.group() == '{':
                brace_level += 1

            position += match.end()

            # Get the next match
            match = re_brace.search(text[position:])

        # Parse and add the tag
        d = match_tag.groupdict()
        tag_name = d['tag']
        tag_attributes = d['attributes']

        # Parse the ast for the tag's content only if it's not a verbatim style
        # tag.
        if tag_name in settings.verbatim_tags:
            tag_content = text[start_position:position - 1]
        else:
            tag_content = process(text[start_position:position - 1])

        tag = factory.tag(tag_name=tag_name,
                          tag_content=tag_content,
                          tag_attributes=tag_attributes,
                          context=context,)
        new_ast.append(tag)

        # If the tag didn't have a close brace, mark the open_brace attribute
        # on the tag. The AST validator will deal with this.
        if brace_level != 0:
            tag.open_brace = True

        # Find the next tag
        match_tag = re_open_tag.search(text[position:])

    # Add the remainer
    new_ast.append(text[position:])

    # If the new_ast has only one item, then return the item itself. (i.e.
    # don't wrap a single item in a list
    if len(new_ast) == 1:
        new_ast = new_ast[0]

    # Wrap in a root tag, if it's the first level
    if level == 1:  # root level
        # If this is the root tag, validate and clean the ast
        line_offset = ast.line_offset if hasattr(ast, 'line_offset') else 1
        validator = ValidateAndCleanAST(name=src_filepath,
                                        line_offset=line_offset)
        new_ast = validator.validate(new_ast)

        new_ast = factory.tag(tag_name='root',
                              tag_content=new_ast,
                              tag_attributes=None,
                              context=context)

    return new_ast


def process_context_tags(ast=None, context=None, src_filepath=None, level=1):
    """Process the ASTs of tags in the context.

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
    ast : :obj:`disseminate.Tag`, list of ast elements or string
        The unmodified AST.
    """
    # Setup the tag factor to generate tags
    factory = TagFactory()

    # See if there are entries in the context that share the same name as tags
    context_tag_keys = context.keys() & factory.tag_types.keys()

    # Convert the context tag entries to tags
    for key in context_tag_keys:
        entry_text = context[key]
        tag = factory.tag(tag_name=key,
                          tag_content=entry_text,
                          tag_attributes=None,
                          context=context)

        # Replace the entry in the context with the tag itself
        context[key] = tag

    # Return the AST unmodified
    return ast