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

        # Load the context from the document's header into a subcontext,
        # to be added to the context later
        header_context = BaseContext()
        for key in keys:
            rest, d = load_from_string(context[key])

            # Replace the entry with the context removed
            context[key] = rest

            # Update the header context
            header_context.update(d)

        # Load the template contexts. This only needs to be done once for
        # a tree of contexts with the same template. A fresh renderer should
        # be loaded for each subdocument.
        # To load a template, we need to preload some of the entries needed for
        # the renderer and for loading additional header files from the template

        # Load these values into a subcontext, to be added to the context
        # later
        template_context = BaseContext()
        for entry in getattr(context, 'preload', set()):
            if entry in header_context:
                context[entry] = header_context[entry]
        renderers = load_renderers(context)
        template = context.get('template', None)
        template_loaded = (context.get('template_loaded', False) == template)

        # See if there are additional header files from the template
        context_filepaths = [p for r in renderers.values()
                             for p in r.context_filepaths()]

        if not template_loaded and len(context_filepaths) > 0:
            # Load the additional headers, if there are any present. The only
            # needs to be done once per template
            for context_filepath in context_filepaths:
                template_context.load(context_filepath.read_text())

            # The template contexts have now been loaded. Mark an entry for
            # this accomplishement in the context.
            context['template_loaded'] = template

        # Load the rest of the subcontexts (header_context, template_context)
        # into this context.
        # 1. The header_context should always overwrite values in the context,
        #    butit should be loaded after the template context
        # 2. The template_context has optional values that should be written
        #    if they don't already exist
        # Exclude entriesthat have already been preloaded.
        for subcontext in (template_context, header_context):

            # Remove entries that have already been preloaded
            keys_to_update = subcontext.keys()
            keys_to_update -= getattr(subcontext, 'preload', set())

            # Load the entries from the subcontext into the context
            context.match_update({k: v for k, v in subcontext.items()
                                  if k in keys_to_update})
