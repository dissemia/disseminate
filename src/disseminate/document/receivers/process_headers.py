"""
A receiver to process headers in a context
"""
from ..signals import document_onload
from ...renderers.utils import load_renderers
from ...context import BaseContext
from ...context.utils import find_header_entries, load_from_string


@document_onload.connect_via(order=1000)
def process_headers(context, **kwargs):
    """Process header strings for entries in a context by loading them into
    the context.

    Context information comes from the following sources:

    1. The document itself and its header file
    2. Additional headers from the template

    The information in (1) takes precedence over (2). For this reason, (1)
    should be loaded after (2), but (2) is specified by some entries, like
    renderers, template, targets, in (1), so (1) is pre-loaded before (2).
    """
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
    template_context = BaseContext()
    preload_entries = getattr(context, 'preload', set())
    context.match_update({k: v for k, v in header_context.items()
                          if k in preload_entries})

    renderers = load_renderers(context)
    template = context.get('template', None)
    template_loaded = (context.get('template_loaded', False) == template)

    # See if there are additional header files from the template
    context_filepaths = [p for r in renderers.values()
                         for p in r.context_filepaths()]

    if not template_loaded and len(context_filepaths) > 0:
        # Load the additional headers, if there are any present. The only
        # needs to be done once per template.
        # It should be done in *reverse* order because the first
        # context_filepath corresponds to the template actually used whereas
        # later context_filepaths are from inherited templates.
        for context_filepath in context_filepaths[::-1]:  # reverse order
            template_context.load(context_filepath.read_text())

        # The template contexts have now been loaded. Mark an entry for
        # this in the context.
        context['template_loaded'] = template

    # Load the rest of the subcontexts (header_context, template_context)
    # into this context.
    # 1. The header_context should always overwrite values in the context,
    #    but it should be loaded after the template context
    # 2. The template_context has optional values that should be written
    #    if they don't already exist
    # Exclude entries that have already been preloaded.
    for subcontext in (template_context, header_context):
        # Remove entries that have already been preloaded
        keys_to_update = subcontext.keys()
        keys_to_update -= getattr(subcontext, 'preload', set())

        # Load the entries from the subcontext into the context
        context.match_update({k: v for k, v in subcontext.items()
                              if k in keys_to_update})

