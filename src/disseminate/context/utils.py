"""Utilities for contexts."""
import regex

from ..utils.string import str_to_dict


re_header_block = regex.compile(r'^[\s\n]*(-{3,})\s*\n'
                                r'(?P<header>.+?)'
                                r'(\n\s*\g<1>)\n?', regex.DOTALL)


def find_header_entries(context):
    """Find context entries that contain a header string.

    Parameters
    ----------
    context : dict
        The context dict to search.

    Returns
    -------
    keys
        The keys for entries with header entries.
    """
    keys = set()
    for k, v in context.items():
        if isinstance(v, str) and re_header_block.match(v):
            keys.add(k)
    return keys


def load_from_string(string):
    """Load a context from a string containing a header string.

    Parameters
    ----------
    string : str
        The string to load into this context.

    Returns
    -------
    string, dict : Tuple[str, dict]
       The processed string with the header removed and the dict with the
       loaded values from the header.
    """
    # Pull out the header string, if available
    m = re_header_block.match(string)
    rest = None
    if m is not None:
        # Determine the start and end position of the header
        start, end = m.span()

        # Collect the rest of the string
        rest = string[end:]

        # Get the header part of the string
        string = m.groupdict()['header']

    # Parse the string
    d = str_to_dict(string)

    return rest, d
