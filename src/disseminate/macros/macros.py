"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from ..utils.string import Metastring
from .. import settings


re_macro = regex.compile(r"(?P<macro>" +
                         settings.tag_prefix +  # tag prefix. e.g. '@'
                         r"\w+)"
                         r"({\s*})?"  # match empty curly brackets
                         )

#: The following are macros defined by this submodule
_submodule_macros = None


def replace_macros(s, context):
    """Replace the macros and return a processed string.

    Macros are simple string replacements from context entries whose keys
    start with the tag_prefix character (e.g. '@test'). The process_context_asts
    will ignore macro context entries that have keys which start with this
    prefix. This is to preserve macros as strings.

    Parameters
    ----------
    context : dict
        A dict containing variables defined for a specific document.

    Returns
    -------
    processed_string : str
        A string with the macros replaced.

    Raises
    ------
    MacroNotFound
        Raises a MacroNotFound exception if a macro was included, but it could
        not be found.
    """
    # Initialize the metastring dict
    meta = s.__dict__ if hasattr(s, '__dict__') else dict()

    # Replace the macros
    def _substitute(m):
        d = m.groupdict()
        macro = d['macro']

        # Replace a macro if if it's the context
        if macro in context:
            return str(context[macro])
        else:
            return m.group()

    # Return a metastring with the macros substituted. Keep substituting until
    # all macros are replaced or the string is no longer changing
    s, num_subs = re_macro.subn(_substitute, s)
    last_num_subs = 0
    while num_subs > 0 and num_subs > last_num_subs:
        last_num_subs = num_subs
        s, num_subs = re_macro.subn(_substitute, s)

    return Metastring(s, **meta)


def process_context_macros(context):
    """""Process the macros of strings in a context.

    This function replaces macros in strings in the context--and not tags.
    Consequently, it should be executed before tags are created in the context.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.
    """

    # Go through the entries in the context and determine which are tags
    for k, v in context.items():
        # Skip non-string entries
        if not isinstance(v, str):
            continue

        # Process the entry in the context
        context[k] = replace_macros(s=v, context=context)

    return None
