"""
Receivers for processing a tag's macros on tag creation.
"""
from ..signals import tag_created
from ...utils.string import replace_macros


@tag_created.connect_via(order=100)
def process_macros(tag, **kwargs):
    """A receiver for replacing macros in pre-parsed tag strings."""
    # Skip non-string entries and macro entries. Macros themselves don't
    # need to be processed, and processing these can introduce problems
    # with recursion
    if not isinstance(tag.content, str):
        return None

    # Process the entry in the context
    tag.content = replace_macros(tag.content, tag.context)
    return tag
