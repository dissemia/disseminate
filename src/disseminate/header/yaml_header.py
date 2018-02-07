"""
Functions for loading a YAML header
"""
import regex
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


re_header = regex.compile(r'[\s\n]*[\n]?-{3,}\n'
                          r'(?P<yaml>[^-]+)'
                          r'\n-{3,}\n')


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

    m = re_header.match(s)
    if m:
        header_str = m.groupdict()['yaml']
        header = load(header_str, Loader=Loader)
        local_context.update(header)

        # Advance the string by the amount of the header
        _, end = m.span()
        s = s[end:]

    return s