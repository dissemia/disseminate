"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from .science import *
from ..utils.string import Metastring
from .. import settings


re_macro = regex.compile(r"(?P<macro>@\w+)")

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

    # Initialize the macros to be used
    macros = dict()

    # Load the submodule macros for this submodule
    submodule_macros = globals()['_submodule_macros']
    if submodule_macros is None:
        submodule_macros = dict()

        # Load all of the macros imported in this module.
        for macro_dict in [v for k, v in globals().items()
                           if k.startswith("macros_")
                              and isinstance(v, dict)]:
            submodule_macros.update(macro_dict)

        globals()['_submodule_macros'] = submodule_macros
    macros.update(submodule_macros)

    # Add custom macro entries like title and author.
    for entry in settings.custom_macros:
        if entry in context:
            macros['@' + entry] = context[entry]

    # Import macros from the context
    for k,v in context.items():
        if not k.startswith('@'):
            continue
        macros[k] = v

    # Replace the macros
    def _substitute(m):
        macro_name = m.group()
        return (macros[macro_name] if macro_name in macros else
                macro_name)

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
