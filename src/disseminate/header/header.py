"""
Functions to load basic headers.
"""
import regex

from ..utils.string import Metastring, str_to_dict
from .. import settings

re_header_block = regex.compile(r'^[\s\n]*(-{3,})\s*\n'
                                r'(?P<header>.+?)'
                                r'(\n\s*\g<1>)\n?', regex.DOTALL)


def load_header(context):
    """Load a basic header from a string in the 'body' entry
    (see settings.body_attr) of the context and replace it with the header
    removed.

    Parameters
    ----------
    context : :obj:`BaseContext <disseminate.context.context.BaseContext>`
        A context dict containing variables defined for a specific document.

    Returns
    -------
    processed_string : str
        A string with the header removed.
    """
    body_attr = settings.body_attr
    assert context.is_valid(body_attr)
    s = context[body_attr]

    # Initialize the metastring dict
    meta = s.__dict__ if hasattr(s, '__dict__') else dict()

    m = re_header_block.match(s)
    if m:
        header_str = m.groupdict()['header']
        header = str_to_dict(header_str)

        # update the context
        context.recursive_update(header)

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

