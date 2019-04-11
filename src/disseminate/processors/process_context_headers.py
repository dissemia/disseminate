"""
Processors for working up the headers of strings in a context.
"""
from .process_context import ProcessContext
from ..context.context import re_header_block


class ProcessContextHeaders(ProcessContext):
    """Process header strings for entries in a context by loading them into
    the context.
    """

    order = 100

    def __call__(self, context):

        # See which context entries have a header
        for k, v in context.items():
            if isinstance(v, str) and re_header_block.match(v):
                # The context entry has a header. Process the header entry and
                # strip the header from the string.
                context[k] = context.load(v, strip_header=True)
