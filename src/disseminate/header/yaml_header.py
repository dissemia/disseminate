"""
Functions for loading a YAML header
"""
import regex
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ..utils.string import Metastring


re_header = regex.compile(r'^[\s\n]*(-{3,})\s*\n'
                          r'(?P<yaml>.+?)'
                          r'(\n\s*\g<1>)\n', regex.DOTALL)


def load_yaml_header(s, local_context, global_context):
    """Load a yaml header from a string to the local_context and return the
    string with the header removed.

    Parameters
    ----------
    s : str
        The string to process for the header
    local_context : dict
        A dict containing variables defined for a specific document.
    global_context : dict
        A dict containing variables defined for a project (i.e. a set of
        documents)

    Returns
    -------
    processed_string : str
        A string with the header removed.
    """
    # Initialize the metastring dict
    meta = s.__dict__ if hasattr(s, '__dict__') else dict()

    m = re_header.match(s)
    if m:
        header_str = m.groupdict()['yaml']
        header = load(header_str, Loader=Loader)
        local_context.update(header)

        # Determine the start and end position of the header
        start, end = m.span()

        # Determine the number of new lines skipped and add it to the meta
        # dict for the metastring
        header_str = s[start:end]
        meta['line_offset'] = (meta.setdefault('line_offset', 1) +
                               header_str.count('\n'))

        # Advance the string by the amount of the header. Add the line_offset
        # Metainformation
        s = Metastring(s[end:], **meta)

    return s
