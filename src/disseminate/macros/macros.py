"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from ..utils.string import Metastring
from .. import settings


re_macro = regex.compile(settings.tag_prefix +
                         r"(?P<macro>\w+)")

#: The following are macros defined by this submodule
_submodule_macros = None


def replace_macros(s, context):
    """Replace the macros and return a processed string.

    .. note:: Macros are loaded from the following sources:

        1. submodule macros (like science macros)
        2. custom macros in the settings
        3. macro entries in the context.


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
        macro_name = d['macro']

        # Replace a macro if if it's the context
        if macro_name in context:
            return str(context[macro_name])
        else:
            return settings.tag_prefix + macro_name

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
        # Skip macros and non-string entries
        if k.startswith('@') or not isinstance(v, str):
            continue

        # Process the entry in the context
        context[k] = replace_macros(s=v, context=context)

    return None
