"""
Receivers for processing a tag's paragraphs on tag creation.
"""
import regex

from ..signals import tag_created


@tag_created.connect_via(order=400)
def process_paragraphs(tag, tag_factory, tag_base_cls, **kwargs):
    """A receiver to parse the paragraphs of tags."""
    if tag.name in tag.context.get('process_paragraphs', []):
        context = tag.context
        p_cls = tag_factory.tag_class(tag_name='P', context=context)
        process_paragraph_tags(tag, context=tag.context,
                               tag_base_cls=tag_base_cls,
                               p_cls=p_cls)
    return tag


re_para = regex.compile(r'(?:\s*\n\s*\n\s*\n*)')


def group_paragraphs(elements):
    r"""Given a list, group the items into sublists based on strings with
    newlines.

    .. note:: This function will not include items in the ast, including tags,
              in paragraphs sublists that have an attribute
              'include_paragraphs' with a value of False.

    .. note:: The function is idempotent. It will reprocess the generated AST
              and not make changes.

    Parameters
    ----------
    elements : Union[list, str]
        A string or a list of items and strings to group paragraphs.

    Returns
    -------
    parse_list : list
        The list with sublists denoting paragraph breaks.

    Examples
    --------
    >>> group_paragraphs([1, 2, 'three', 'four\n\nfive', 6,
    ...                   'seven\n\neight'])
    [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]
    >>> group_paragraphs('This is my\n\ntest paragraph.')
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
    r"""Remove invalid paragraphs from the sublists in an ast created by
    group_paragraphs.

    This function will:

    1. Remove sublists created by group_paragraphs that only contain empty
       strings and strings with space or newline characters.

    Parameters
    ----------
    elements : Union[list, str]
        A string or a list of items and strings to group paragraphs.

    Returns
    -------
    cleaned_list : list
        The list with sublists denoting paragraph breaks.

    Examples
    --------
    >>> group = group_paragraphs([1, 2, 'three', 'four\n\nfive', 6,
    ...                           'seven\n\neight'])
    >>> clean_paragraphs(group)
    [[1, 2, 'three', 'four'], ['five', 6, 'seven'], ['eight']]
    >>> group = group_paragraphs([1, 2, 'three', '\n\n', 6,
    ...                           'seven\n\neight'])
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


def assign_paragraph_roles(elements, tag_base_cls):
    """Assign the 'paragraph_role' attribute for tags within sublists created
    by the group_paragraphs function.

    The 'paragraph_role' attribute can either be 'block', for tags that are
    alone in a paragraph, or 'inline' for tags that are in a paragraph with
    other text elements.

    Parameters
    ----------
    elements : Union[str, list, :obj:`Tag <.Tag>`]
        The list of paragraph tags (:obj:`P <.text.P>` and
        strings.
    tag_base_cls : :class:`Tag <.Tag>`
        The base class for Tag objects.

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
        sublist_tags = list(filter(lambda x: isinstance(x, tag_base_cls),
                                   sublist))

        # Find all strings without white space
        sublist_string = [s for s in sublist
                          if isinstance(s, str) and s.strip() != ""]

        # Determine the number of tags and the number of total elements in
        # the sublist
        num_tags = len(sublist_tags)
        num_elems = len(sublist)
        num_nonempty_strings = len(sublist_string)

        if num_tags == 1 and num_nonempty_strings == 0:
            # If the number of tags and elements is 1, then tag is in its own
            # block
            sublist_tags[0].paragraph_role = 'block'
        elif num_elems > 1:
            # Otherwise the tags are inline with other elements in the
            # paragraph.
            for tag in sublist_tags:
                tag.paragraph_role = 'inline'

    return elements


def process_paragraph_tags(element, context, tag_base_cls, p_cls):
    """Process the paragraphs for the contents of a tag.

    Parameters
    ----------
    element : Union[str, list, :obj:`Tag <.Tag>`]
        A string, tag or list of both to process for paragraphs
    context : :obj:`DocumentContext <.DocumentContext>`
        The context with values for the document.
    tag_base_cls : :class:`Tag <.Tag>`
        The base class for Tag objects.
    p_cls : :class:`P <.text.P>`
        The tag class for paragraphs.

    Returns
    -------
    processed_contents : Union[str, :obj:`Tag <.Tag>`, list]
        The contents with
    """
    if isinstance(element, tag_base_cls):
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
    assign_paragraph_roles(group, tag_base_cls=tag_base_cls)

    # Convert the sublists into paragraphs
    for count, item in enumerate(group):
        if isinstance(item, list):
            # If the item is a list with only 1 item, then isolate that one
            # item. The paragraph will then only contain that one item, rather
            # than have a list with one item.
            item = item[0] if len(item) == 1 else item

            # sublists created by group_paragraphs are paragraphs
            p = p_cls(name='p', content=item, attributes='', context=context)

            group[count] = p

    # wrap the group, if it's only 1 item
    if len(group) == 1:
        group = group[0]

    # If the original element was a tag, replace its content
    if isinstance(element, tag_base_cls):
        element.content = group
        return element
    else:
        return group
