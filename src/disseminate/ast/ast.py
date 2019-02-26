"""
Functions for processing Abstract Syntax Trees (ASTs).
"""
import regex

from .exceptions import ParseError, AstException
from .cleaners import clean_strings
from ..tags import TagFactory, Tag
from ..utils.string import NewlineCounter
from .. import settings


re_open_tag = regex.compile(  # The character to use in identifying a tag. By
                              # default, it's an '@' character.
                                settings.tag_prefix +
                                r'(?P<tag>[A-Za-z0-9][\w]*)'
                                r'(?P<attributes>\[[^\]]+\])?'
                                r'(?P<open>{)?')
re_brace = regex.compile(r'[}{]')


def process_ast(ast, context, src_filepath=None, line_counter=None, level=1):
    """Process a string into an Abstract Syntax Tree (AST) of tags, strings and
     lists of both.

     ASTs are created by having a tag whose contents are either tags, string or
     lists of both.

    .. note:: The AST processing should be able to reprocess the generated AST
              without making changes.

    Parameters
    ----------
    ast : str or list
        A string to parse into an AST, a list of strings or an existing AST.
    context : dict
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
    if level >= settings.tag_max_depth:
        msg = ("The maximum depth of '{}' has been reached in the AST. "
               "Additional levels can be set by the 'settings.ast_max_depth'.")
        raise AstException(msg.format(settings.ast_max_depth))

    # Setup the line counter, if needed
    if line_counter is None:
        line_offset = ast.line_offset if hasattr(ast, 'line_offset') else 1
        line_counter = NewlineCounter(initial=line_offset)

    new_ast = []
    process = lambda x: process_ast(x, context, src_filepath, line_counter,
                                    level+1)

    # Look at the ast and process it depending on whether it's a string, tag
    # or list
    if isinstance(ast, list):
        return list(map(process, ast))
    elif isinstance(ast, Tag):
        if isinstance(ast.content, str) or isinstance(ast.content, Tag):
            ast.content = process(ast.content)
        elif isinstance(ast.content, list):
            ast.content = list(map(process, ast.content))
        return ast

    # The following only processes text
    text = ast

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
        line_counter(text[position:match_tag_start])

        # Push up the position to the end of the tag match
        position += match_tag.end()
        start_position = position

        # Parse the tag contexts
        d = match_tag.groupdict()
        tag_name = d['tag']
        tag_attributes = d['attributes']

        # Find open and close braces and advance the position
        # up until the match closing brace is found
        brace_level = 1 if d['open'] is not None else 0
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

        # Before parsing the rest of the tag's contents, get its current
        # line number
        line_number = line_counter.number

        # Raise an error if the brace wasn't closed
        if brace_level > 0:
            msg = "The tag '{}' on line {} was not closed."
            raise ParseError(msg.format(tag_name, line_number))

        # Parse the ast for the tag's content
        if tag_name in settings.verbatim_tags:
            # If the tag_name is a verbatim tag, then don't process it further
            tag_content = text[start_position:position - 1]
            line_counter(text[start_position:position - 1])

        elif d['open'] is None:
            # For tags with no open/close braces, then the content is empty
            tag_content = ''

        else:
            # Otherwise process the text within the tag's braces
            tag_content = process(text[start_position:position - 1])

        tag = factory.tag(tag_name=tag_name,
                          tag_content=tag_content,
                          tag_attributes=tag_attributes,
                          context=context,)
        tag.line_number = line_number  # mark the line number
        new_ast.append(tag)

        # Find the next tag
        match_tag = re_open_tag.search(text[position:])

    # Add the remainer
    new_ast.append(text[position:])
    line_counter(text[position:])

    # If the new_ast has only one item, then return the item itself. (i.e.
    # don't wrap a single item in a list
    if len(new_ast) == 1:
        new_ast = new_ast[0]

    # Wrap in a root tag, if it's the first level and the new_ast isn't already
    # a tag
    if level == 1 and not isinstance(new_ast, Tag):  # root level
        # remove empty strings
        clean_strings(new_ast)

        # Unwrap lists with single items
        new_ast = (new_ast[0] if isinstance(new_ast, list) and
                   len(new_ast) == 1 else new_ast)

        # Create a new root tag
        new_ast = factory.tag(tag_name='root', tag_content=new_ast,
                              tag_attributes='', context=context)

    return new_ast


def process_context_asts(context):
    """Process the ASTs of tags in the context.

    This function converts strings with tag substrings (ex: '@b{bold}') into
    tags.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.
    """
    # Setup the needed variables for process_ast
    assert context.is_valid('src_filepath')
    src_filefile = context['src_filepath']

    # Go through the entries in the context and determine which can be converted
    # to an AST
    for k, v in context.items():
        # Skip macros and non-string entries
        if not isinstance(v, str):
            continue

        # Process the entry in the context
        ast = process_ast(ast=v, context=context, src_filepath=src_filefile)

        # Replace the context entry if it's a valid ast with tags. If 'v' was
        # just a string without tags, then the returned ast is a root tag whose
        # content is just a string.
        if not isinstance(ast.content, str):
            ast.name = k
            context[k] = ast

    return None
