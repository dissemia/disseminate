"""
Processors for working up the headers of strings in a context.
"""
from .process_context import ProcessContext
from ...renderers.utils import load_renderers
from ...context import BaseContext
from ...context.utils import find_header_entries, load_from_string


class ProcessContextHeaders(ProcessContext):
    """Process header strings for entries in a context by loading them into
    the context.

    Context information comes from the following sources:

    1. The document itself and its header file
    2. Additional headers from the template

    The information in (1) takes precedence over (2). For this reason, (1)
    should be loaded after (2), but (2) is specified by some entries, like
    renderers, template, targets, in (1), so (1) is pre-loaded before (2).
    """

    #: This processor should be loaded before the tags are processed
    #: (ProcessContextTags) so that the tags can use the updated values from
    #: headers in the context.
    order = 100

    def __call__(self, context):

        # See which context entries have a header
        keys = find_header_entries(context)

        # Load the context into a BaseContext
        pre_context = BaseContext()
        for key in keys:
            rest, d = load_from_string(context[key])

            # Replace the entry with the context removed
            context[key] = rest

            # Update the header context
            pre_context.update(d)

        # Preload some of the entries needed for the renderer and for loading
        # additional header files from the template
        for entry in getattr(context, 'preload', set()):
            if entry in pre_context:
                context[entry] = pre_context[entry]
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
                pre_context.load(context_filepath.read_text(), overwrite=False)

        # Load the rest of the pre-context into this context. Exclude entries
        # that have already been preloaded.
        keys_to_update = pre_context.keys()
        keys_to_update -= getattr(context, 'preload', set())
        context.match_update({k: v for k, v in pre_context.items()
                              if k in keys_to_update})
