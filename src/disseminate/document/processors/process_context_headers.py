"""
Processors for working up the headers of strings in a context.
"""
from .process_context import ProcessContext
from ...renderers.utils import load_renderers
from ...context.utils import find_header_entries, load_from_string


class ProcessContextHeaders(ProcessContext):
    """Process header strings for entries in a context by loading them into
    the context.
    """

    #: This processor should be loaded before the tags are processed
    #: (ProcessContextTags) so that the tags can use the updated values from
    #: headers in the context.
    order = 100

    def __call__(self, context):

        # See which context entries have a header
        keys = find_header_entries(context)

        # Load the context into a dict
        header_context = dict()
        for key in keys:
            rest, d = load_from_string(context[key])

            # Replace the entry with the context removed
            context[key] = rest

            # Update the header context
            header_context.update(d)

        context.match_update(header_context)

        # Setup the Renderer
        renderers = load_renderers(context)

        # See if there are additional header files from the template
        context_filepaths = [p for r in renderers.values()
                             for p in r.context_filepaths()]

        if len(context_filepaths) > 0:
            # Load the additional headers, if there are any present. In this
            # case, do not overwrite existing values in the context. Only load
            # missing values because values loaded in the context already (by
            # this document or parent documents) take precedence.
            for context_filepath in context_filepaths:
                context.load(context_filepath.read_text(), overwrite=False)
