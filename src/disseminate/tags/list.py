"""
Tags for lists.
"""
from math import ceil

import regex

from .tag import Tag
from ..attributes import Attributes
from .. import settings


# Find lists with entries labeled with a '-' or '*' bullet for each list item
re_list = regex.compile(r'^\s*[\*\-]', regex.MULTILINE)

# Regex to clean list items with multi-line line-items
re_multiline_items = regex.compile(r'\s*\n+\s+')


def parse_string_list(s):
    """Parse a string with lists.

    Parameters
    ----------
    s : str
        The string to parse

    Returns
    -------
    parsed_list : List[Tuple[int, str]]

    Examples
    --------
    >>> parse_string_list("- This is my first item.\\n"
    ...                   "  - This is my first subitem\\n")
    [(0, 'This is my first item.'), (2, 'This is my first subitem')]
    """
    parsed_list = []
    current_match = None
    current_pos = 0
    list_level = 1

    for match in re_list.finditer(s):
        # Skip the first entry, since this is the string contents before
        # the start of the list
        if current_match is None:
            current_match = match
            current_pos = match.end()

            # Find the level. The number of spaces determines the level
            list_level = match.group().count(' ')
            continue

        # Retrieve the string up to this point. Remove leading spaces.
        end_pos = match.start()
        sub_string = s[current_pos:end_pos].strip()

        # Create the new entry in the returned list
        parsed_list.append((list_level, sub_string))

        # Set the current position and current match for the next iteration
        current_match = match
        current_pos = match.end()
        list_level = match.group().count(' ')

    # Add the remaining match to the returned list
    if current_match is not None:
        # Retrieve the string up to this point up until the end.
        # Remove leading spaces.
        end_pos = current_match.end()
        sub_string = s[end_pos:].strip()

        # Create the new entry in the returned list
        parsed_list.append((list_level, sub_string))

    return parsed_list


def clean_string_list(parsed_list):
    """Clean the string list created by parse_string_list.

    Cleaning include removeing extra spaces and newlines in parse string line
    elements.
    
    Parameters
    ----------
    parsed_list : List[Tuple[int, str]]
        The parsed list from parse_string_list.
        
    Returned
    --------
    cleaned_list : List[Tuple[int, str]]
        The cleaned list.

    >>> l = parse_string_list("- This is my first item.\\n"
    ...                   "  - This is my first subitem\\n")
    >>> clean_string_list(l)
    [(0, 'This is my first item.'), (2, 'This is my first subitem')]
    """
    return [(level, re_multiline_items.sub(" ", s))
            if isinstance(s, str) else
            (level, s)
            for level, s in parsed_list ]


def normalize_levels(parsed_list, list_level_spaces=settings.list_level_spaces):
    """Normalize the levels from a parse_list so that the first level is 0,
    and subsequent levels are properly incremented.

    Parameters
    ----------
    parsed_list : List[Tuple[int, str]]
        The parsed list from parse_string_list.
    list_level_spaces : int
        The number of spaces used to identify sub-levels in a list.

    Returned
    --------
    normalized_list : List[Tuple[int, str]]
        The normalized list with levels fixed.

    >>> l = parse_string_list("- This is my first item.\\n"
    ...                   "  - This is my first subitem\\n")
    >>> normalize_levels(l)
    [(0, 'This is my first item.'), (2, 'This is my first subitem')]
    """
    min_level = min(level for level, item in parsed_list)
    return [(ceil((level - min_level)/list_level_spaces), item)
            for level, item in parsed_list]


def parse_list(content, context):
    """Parse lists (and sublists) from a string or list of content.

    Parameters
    ----------
    content : Union[str, List[Union[str, list, :obj:`Tag \
        <disseminate.tags.tag.Tag>`], :obj:`Tag <disseminate.tags.tag.Tag>`]
        The contents of the tag. It can either be a string, a tag or a list
        of strings, tags and lists.
    context : :obj:`.document.DocumentContext`
        The document's context dict.

    Returns
    -------
    returned_list : list
        The list of parse list items, to be used for the content of a list.
    """
    # Unify the format of the cotent
    if isinstance(content, str):
        content = [content]
    elif isinstance(content, Tag):
        content.content = parse_list(content.content)
    elif isinstance(content, list):
        pass
    else:
        return []

    # Go item-by-item to find list items
    returned_list = []
    current_list = None

    for item in content:
        # Add non-strings to a list
        if not isinstance(item, str) and current_list is not None:
            # If it's not a string, just add it to the current list
            current_list.append(item)

        # If it's a string, see if it has list items in it
        parsed_list = parse_string_list(item)
        parsed_list = clean_string_list(parsed_list)

        if parse_list:
            for level, list_item in parsed_list:
                if current_list is not None:
                    current_list.append(list_item)
                else:
                    current_list = [list_item]

                # Create the list item and add it the returned list
                content = (current_list[0] if len(current_list) == 1 else
                           current_list)
                li = ListItem(name='listitem', content=content,
                              attributes='level={}'.format(level),
                              context=context)
                returned_list.append(li)

                # Reset the current_list
                current_list = []

    return returned_list


class ListItem(Tag):
    """An item in a list"""

    active = False
    html_name = "li"


class List(Tag):
    """A tag for lists"""

    active = True
    html_name = "ul"

    def __init__(self, name, content, attributes, context):
        self.name = name
        self.attributes = Attributes(attributes)
        self.context = context

        # Parse the content string into list items
        parsed_list = parse_string_list(content)
        parsed_list = clean_string_list(parsed_list)
        parsed_list = normalize_levels(parsed_list)
        self.content = [ListItem(name='listitem', content=list_content,
                                 attributes='class="level-{}"'.format(level),
                                 context=context)
                        for level, list_content in parsed_list]


class OrderedList(List):
    """A tag for ordered lists"""

    active = True
    html_name = "ol"
    aliases = ('outline',)
