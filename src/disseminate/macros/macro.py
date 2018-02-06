"""
Macros are special markup for inserting one or a series of tags in the AST.
"""
import regex

from .chemistry import *


re_macro = regex.compile(r"(?P<macro>@\w+)(?=\s*[^{\w])")


def sub_macros(s, macro_index):
    """Substitute macros in the given string."""

    def _substitute(m):
        macro_name = m.group()
        return (macro_index[macro_name] if macro_name in macro_index else
                macro_name)

    return re_macro.sub(_substitute, s)


class MacroIndex(dict):
    """A macro index"""

    def __init__(self, *args, **kwargs):
        super(MacroIndex, self).__init__(*args, **kwargs)

        # Load all of the macros imported in this module.
        for macro_dict in [v for k, v in globals().items()
                           if k.startswith("macros_")
                           and isinstance(v, dict)]:

            self.update(macro_dict)
