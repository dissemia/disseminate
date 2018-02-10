"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from .chemistry import *


re_macro = regex.compile(r"(?P<macro>@\w+)(?=\s*[^{\w])")


#: The following are macros defined by this submodule
_submodule_macros = None


def replace_macros(s, local_context, global_context):
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
    local_context : dict
        A dict containing variables defined for a specific document.
    global_context : dict
        A dict containing variables defined for a project (i.e. a set of
        documents)

    Returns
    -------
    processed_string : str
        A string with the macros replaced.
    """
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

    # See if the global_context already has a dict of macros. These will
    # potentially overwrite the submodule_macros.
    if ('macros' in global_context and
       isinstance(global_context['macros'], dict)):

        macros.update(global_context['macros'])

    # See if the local_context already has a dict of macros. These will
    # potentially overwrite the submodule_macros and global_macros
    if ('macros' in local_context and
        isinstance(local_context['macros'], dict)):

        macros.update(local_context['macros'])

    # Replace the macros
    def _substitute(m):
        macro_name = m.group()
        return (macros[macro_name] if macro_name in macros else
                macro_name)

    return re_macro.sub(_substitute, s)