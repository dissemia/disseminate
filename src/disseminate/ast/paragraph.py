"""
Functions for processing paragraphs in Abstract Syntax Trees (ASTs).
"""


import regex

from ..tags import TagFactory, Tag


re_para = regex.compile(r'(?:\n{2,}|^)')


def group_paragraphs(ast):
    """Given a list, group the items into sublists based on strings with
    newlines.

    .. note:: This function will not include items in the ast, including tags,
              in paragraphs sublists that have an attribute 'include_paragraphs'
              with a value of False.

    .. note:: The function is idempotent. It will reprocess the generated AST
              and not make changes.

    Parameters
    ----------
    ast : list
        The list of items and strings to group paragraphs.

    Returns
    -------
    parse_list : list
        The list with sublists denoting paragraph breaks.

    Examples
    --------
    >>> group_paragraphs([1, 2, 'three', 'four\\n\\nfive', 6,
    ...                   'seven\\n\\neight'])
    [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]
    """
    if isinstance(ast, str):
        ast = [ast]

    overall_list = []
    sublist = []

    for item in ast:

        # Add non-string elements to the sublist
        if not isinstance(item, str):
            if (getattr(item, 'include_paragraphs', True) and
               not isinstance(item, list)):
                # Include in the paragraph sublist
                sublist.append(item)
            else:
                # Do not include in paragraphs; create a new paragraph sublist
                if sublist:
                    overall_list.append(sublist)
                    sublist = []
                # Append this non-paragraph item to the overall list, outside
                # of a paragraph sublist
                overall_list.append(item)
            continue

        # At this point, item is a string. See if there a paragraph break in
        # the string.
        pieces = re_para.split(item)

        if len(pieces) == 1 and pieces[0]:
            # In this case, no paragraph break was found. Just add the item
            # to the sublist if it's not an empty string
            sublist.append(pieces[0])
            continue

        # In this case, multiple pieces were found. Make these into new
        # sublists
        for i, piece in enumerate(pieces):
            if piece:
                # Add the piece to the paragraph sublist, if it's not an
                # empty string
                sublist.append(piece)

            if i != len(pieces) - 1:
                if sublist:
                    overall_list.append(sublist)
                sublist = []

    if sublist:
        overall_list.append(sublist)

    ast.clear()
    ast += overall_list

    return ast


def clean_paragraphs(ast):
    """Remove invalid paragraphs from the sublists in an ast created by
    group_paragraphs.

    This function will:
    1. Remove sublists created by group_paragraphs that only contain empty
       strings and strings with space or newline characters.

    Parameters
    ----------
    ast : list
        The list of items and strings of grouped paragraphs.

    Returns
    -------
    cleaned_list : list
        The list with sublists denoting paragraph breaks.

    Examples
    --------
    >>> group = group_paragraphs([1, 2, 'three', 'four\\n\\nfive', 6,
    ...                           'seven\\n\\neight'])
    >>> clean_paragraphs(group)
    [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]
    >>> group = group_paragraphs([1, 2, 'three', '\\n\\n', 6,
    ...                           'seven\\n\\neight'])
    >>> clean_paragraphs(group)
    [[1, 2, 'three'], [6, 'seven'], ['eight']]
    """
    new_ast = []

    for item in ast:
        # Determine if item is a sublist with only empty strings or strings
        # with space and newline characters. If so, don't make a paragraph
        # with it, and skip it.
        if (isinstance(item, list) and
           all(isinstance(i, str) and not i.strip() for i in item)):
            continue

        new_ast.append(item)

    # Copy over the new_ast to the given ast
    ast.clear()
    ast += new_ast

    return ast


def process_paragraphs(ast, context):
    """Process the paragraphs for an AST. Paragraphs are blocks of text with
    zero or more tags.

    Parameters
    ----------
    ast : str or list
        A string to parse into an AST, a list of strings or an existing AST.
    context : dict
        The context with values for the document.

    Returns
    -------
    ast : :obj:`disseminate.Tag`
        The AST is a root tag with a content comprising a list of tags or
        strings.
    """
    # Setup the the tag factor
    factory = TagFactory()

    # Format ast to be used by the group_paragraphs function. The ast should
    # be a list
    if hasattr(ast, 'content'):
        if isinstance(ast.content, str):
            ast.content = [ast.content]
        processed_ast = ast.content
    elif isinstance(ast, str):
        processed_ast = [ast]
    else:
        processed_ast = ast

    assert isinstance(processed_ast, list)

    # Group the paragraphs into sublists
    group_paragraphs(processed_ast)

    # Clean the paragraph sublist groups
    clean_paragraphs(processed_ast)

    # Convert the sublists into paragraphs
    for count, item in enumerate(processed_ast):
        if isinstance(item, list):
            # Determine whether this is the first

            # sublists created by group_paragraphs are paragraphs
            p = factory.tag(tag_name='p',
                            tag_content=item,
                            tag_attributes='',
                            context=context)

            processed_ast[count] = p

    return ast


def process_context_paragraphs(context):
    """Process paragraphs in the tags of the given context.

    This function parses paragraph tags from tags in the context. Consequently,
    it should be executed after tags are created in the context.

    .. note:: This function only processes context entries listed in the
              'process_paragraphs' context entry. If the 'process_paragraphs'
              list is missing, then no paragraphs will be processed.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.

    """
    # Determine which entries in the context should be processed for paragraphs
    # based on the 'process_paragraphs' entry
    process_entries = context.get('process_paragraphs', [])
    assert isinstance(process_entries, list)

    # Go through the entries in the context and process entries specified
    # in the process_entries list
    for k, v in context.items():
        if k not in process_entries:
            continue

        # Process the entry in the context
        ast = process_paragraphs(ast=v, context=context)

        if hasattr(ast, 'name'):
            ast.name = k
        context[k] = ast

    return None
