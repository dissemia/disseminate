"""
Function(s) to replace macros.
"""

from .process_tag import ProcessTag
from ...utils.string import replace_macros


class ProcessMacros(ProcessTag):
    """A processor for macros in tags"""

    def __call__(self, tag):
        # Skip non-string entries and macro entries. Macros themselves don't
        # need to be processed, and processing these can introduce problems
        # with recursion
        if not isinstance(tag.content, str):
            return None

        # Process the entry in the context
        tag.content = replace_macros(tag.content, tag.context)


ProcessMacros(order=100)
