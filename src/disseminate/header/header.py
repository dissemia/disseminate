"""
Functions to load basic headers.
"""
import regex

from ..utils.string import Metastring
from .. import settings

re_header_block = regex.compile(r'^[\s\n]*(-{3,})\s*\n'
                                r'(?P<header>.+?)'
                                r'(\n\s*\g<1>)\n?', regex.DOTALL)

re_entry = regex.compile(r'^(?P<space_level>\s*)'
                         r'(?P<key>.+?)'
                         r'(?<!\\)\:'  # match ':' but not '\:'
                         r'\s*'
                         r'(?P<value>.*)')


def parse_header_str(s):
    """Parse a header string into a dict.

    Parameters
    ----------
    s : str
        The header in string format.

    Returns
    -------
    dict
        The parsed header in dict format.
    """
    d = dict()

    # Split the string into lines and see which lines have an entry of the
    # form "key: value"
    lines = s.splitlines()

    # Go from line to line and identify which lines are key/value pairs

    # Keep a list of all lines that pertain to a given entry
    current_entry_list = []
    # Keep track of how many spaces were used to define the entry. This is used
    # to place sub-blocks of an entry within the entry.
    current_spaces = None

    for line in lines:
        m = re_entry.match(line)

        # Workup the line. Strip leading spaces from the line.
        if current_spaces is not None:
            line = line[current_spaces:]

        # Replace escaped colons ('\:') with colons (':')
        line = line.replace("\:", ":")

        if m is not None:
            # If there's a match, then we may have a new entry.
            # However, only create a new entry if the space_level is the same
            # as the last entry.
            group_dict = m.groupdict()
            space_level = len(group_dict['space_level'])
            key = group_dict['key'].strip()
            value = group_dict['value']

            if current_spaces is not None and space_level > current_spaces:
                # Not a new entry. Just add the line to the last entry.
                current_entry_list.append(line)
            else:
                # A new entry. Create a new current_entry_list.
                current_spaces = space_level
                current_entry_list = d.setdefault(key, [])
                current_entry_list.append(value)
        else:
            # If there's not a match, just add the line to the current entry
            current_entry_list.append(line)

    # Convert the entries in the dict from a list of strings to strings
    d = {k: "\n".join(v).strip('\n') for k, v in d.items()}

    return d


def load_header(context):
    """Load a basic header from a string in the 'body' entry
    (see settings.body_attr) of the context and replace it with the header
    removed.

    Parameters
    ----------
    context : dict
        A dict containing variables defined for a specific document.

    Returns
    -------
    processed_string : str
        A string with the header removed.
    """
    body_attr = settings.body_attr
    assert body_attr in context
    s = context[body_attr]

    # Initialize the metastring dict
    meta = s.__dict__ if hasattr(s, '__dict__') else dict()

    m = re_header_block.match(s)
    if m:
        header_str = m.groupdict()['header']
        header = parse_header_str(header_str)

        # update the context
        for k, v in header.items():
            if (k in context and isinstance(v, dict) and
                    isinstance(context[k], dict)):
                # For dict entries, update the dict with the context's values
                context[k].update(v)
            else:
                # Otherwise, replace the entry
                context[k] = v

        # Determine the start and end position of the header
        start, end = m.span()

        # Determine the number of new lines skipped and add it to the meta
        # dict for the metastring
        header_str = s[start:end]
        meta['line_offset'] = (meta.setdefault('line_offset', 1) +
                               header_str.count('\n'))

        # Advance the string by the amount of the header. Add the line_offset
        # meta information
        s = Metastring(s[end:], **meta)

        # Place the new string in the context
        context[body_attr] = s

    return None

