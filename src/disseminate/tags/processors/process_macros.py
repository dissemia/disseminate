"""
Tag processors for replacing macros in the strings of tag contents.
"""

from .process_tag import ProcessTag
from ...utils.string import replace_macros


class ProcessMacros(ProcessTag):
    """A tag processor for replacing macros in tag strings"""

    order = 100
    short_desc = "Replace text macros in tag strings"

    def __call__(self, tag):
        # Skip non-string entries and macro entries. Macros themselves don't
        # need to be processed, and processing these can introduce problems
        # with recursion
        if not isinstance(tag.content, str):
            return None

        # Process the entry in the context
        tag.content = replace_macros(tag.content, tag.context)
