"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from .science import *
from ..utils.string import Metastring


re_macro = regex.compile(r"(?P<macro>@\w+)")

#: The following are macros defined by this submodule
_submodule_macros = None


def replace_macros(s, context):
    """Replace the macros and return a processed string.

    .. note:: A set of macros from this submodule are loaded as well as macros
             that are defined in the local_context and global_context. In cases
             where macros are defined multiple times, the local_context takes
             precedence over the global_context, and the global_context takes
             precedence over the submodule_macros.

    Parameters
    ----------
    s : str
        The string to process for macros
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

    # See if the context already has a dict of macros. These will
    # potentially overwrite the submodule_macros.
    if 'macros' in context and isinstance(context['macros'], dict):
        macros.update(context['macros'])

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
