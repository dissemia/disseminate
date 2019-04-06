"""
Processors for working up the headers of strings in a context.
"""
from ..context.context import re_header_block


def process_context_headers(context):
    """Process header strings for entries in a context by loading them into
    the context.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.
    """
    # See which context entries have a header
    for k, v in context.items():
        if isinstance(v, str) and re_header_block.match(v):
            # The context entry has a header. Process the header entry and
            # strip the header from the string.
            context[k] = context.load(v, strip_header=True)
