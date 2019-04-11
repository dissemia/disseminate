"""
Tag processors for identifying paragraphs in tags.
"""

import regex

from .process_tag import ProcessTag
from ..tag import Tag
from ..text import P


class ProcessParagraphs(ProcessTag):
    """A processor for identifying and tagging paragraphs in tags.

    The contents of tags will be processed if the tag's name is listed
    in the context's process_paragraphs entry.
    """

    order = 400
    short_desc = ("Identify and create paragraph tags for tag names listed in "
                  "the 'process_paragraphs' context entry")

    def __call__(self, tag):
        if tag.name in tag.context.get('process_paragraphs', []):
            process_paragraph_tags(tag, context=tag.context)


re_para = regex.compile(r'(?:\n{2,})')


def group_paragraphs(elements):
    """Given a list, group the items into sublists based on strings with
    newlines.

    .. note:: This function will not include items in the ast, including tags,
              in paragraphs sublists that have an attribute 'include_paragraphs'
              with a value of False.

    .. note:: The function is idempotent. It will reprocess the generated AST
              and not make changes.

    Parameters
    ----------
    elements : list or str
        A string or a list of items and strings to group paragraphs.

    Returns
    -------
    parse_list : list
        The list with sublists denoting paragraph breaks.

    Examples
    --------
    >>> group_paragraphs([1, 2, 'three', 'four\\n\\nfive', 6,
    ...                   'seven\\n\\neight'])
    [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]
    >>> group_paragraphs('This is my\\n\\ntest paragraph.')
    [['This is my'], ['test paragraph.']]
    """
    # Wrap strings in a list
    elements = [elements] if isinstance(elements, str) else elements

    overall_list = []
    sublist = []

    for item in elements:

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

    elements.clear()
    elements += overall_list

    return elements


def clean_paragraphs(elements):
    """Remove invalid paragraphs from the sublists in an ast created by
    group_paragraphs.

    This function will:
    1. Remove sublists created by group_paragraphs that only contain empty
       strings and strings with space or newline characters.

    Parameters
    ----------
    elements : list or str
        A string or a list of items and strings to group paragraphs.

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
    assert isinstance(elements, list)

    new_elements = []

    for item in elements:
        # Determine if item is a sublist with only empty strings or strings
        # with space and newline characters. If so, don't make a paragraph
        # with it, and skip it.
        if (isinstance(item, list) and
           all(isinstance(i, str) and not i.strip() for i in item)):
            continue

        new_elements.append(item)

    # Copy over the new_ast to the given ast
    elements.clear()
    elements += new_elements

    return elements


def assign_paragraph_roles(elements):
    """Assign the 'paragraph_role' attribute for tags within sublists created
     by the group_paragraphs function.

    The 'paragraph_role' attribute can either be 'block', for tags that are
    alone in a paragraph, or 'inline' for tags that are in a paragraph with
    other text elements.

    Parameters
    ----------
    elements : list
        The list of paragraph tags (:obj:`P <disseminate.tags.text.P>` and
        strings.

    Returns
    -------
    processed_ast : list
        The list with tags in the sublists marked with their paragraph_role.
    """
    assert isinstance(elements, list)

    # Go over the paragraph sublists and determine whether the tags within
    # are inline or block
    for sublist in filter(lambda x: isinstance(x, list), elements):
        # Find all the tags in the sublist
        sublist_tags = list(filter(lambda x: isinstance(x, Tag), sublist))

        # Determine the number of tags and the number of total elements in
        # the sublist
        num_tags = len(sublist_tags)
        num_elems = len(sublist)

        if num_tags == 1 and num_elems == 1:
            # If the number of tags and elements is 1, then tag is in its own
            # block
            sublist_tags[0].paragraph_role = 'block'
        elif num_elems > 1:
            # Otherwise the tags are inline with other elements in the
            # paragraph.
            for tag in sublist_tags:
                tag.paragraph_role = 'inline'

    return elements


def process_paragraph_tags(element, context):
    """Process the paragraphs for the contents of a tag.

    Parameters
    ----------
    element : str, list or tag (:obj:`disseminate.tags.Tag`)
        A string, tag or list of both to process for paragraphs
    context : dict
        The context with values for the document.

    Returns
    -------
    processed_contents : str, :obj:`disseminate.tags.Tag` or list of both
        The contents with
    """
    if isinstance(element, Tag):
        # If it's a tag, pull out its content
        content = element.content
    else:
        # Otherwise use the element directly as the content to process
        content = element

    # Check the format of the content. This function can only process strings
    # or lists
    if not any(isinstance(content, x) for x in (str, list)):
        return content

    # Group the paragraphs into sublists
    group = group_paragraphs(content)

    # Clean the paragraph sublist groups
    clean_paragraphs(group)

    # Assign the paragraph_role for tags within paragraph sublist groups
    assign_paragraph_roles(group)

    # Convert the sublists into paragraphs
    for count, item in enumerate(group):
        if isinstance(item, list):
            # If the item is a list with only 1 item, then isolate that one
            # item. The paragraph will then only contain that one item, rather
            # than have a list with one item.
            item = item[0] if len(item) == 1 else item

            # sublists created by group_paragraphs are paragraphs
            p = P(name='p', content=item, attributes='', context=context)

            group[count] = p

    # wrap the group, if it's only 1 item
    if len(group) == 1:
        group = group[0]

    # If the original element was a tag, replace its content
    if isinstance(element, Tag):
        element.content = group
        return element
    else:
        return group
