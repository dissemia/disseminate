"""
A receiver to process tag entries in a context
"""
from ..signals import document_onload
from ...tags import TagFactory


@document_onload.connect_via(order=10000)
def process_tags(context, **kwargs):
    """Convert context entries into tags for entries listed the
    process_context_tags' context entry.

    This function converts tags for context entries identified by keys listed
    in the 'process_context_tags' context entry

    .. note:: This function is designed to work with string macro entries.
              These are identified by context entries with keys that start
              with the settings.tag_prefix (e.g. '@test'). These *should not*
              be converted into asts, as they are required for simple string
              replacement.
    """
    assert context.is_valid('process_context_tags')

    # Find the tags to process, based on the context entries in the
    # 'process_context_tags' entry of the context and the available context
    # entries
    process_tags = context['process_context_tags']
    keys = set(context.keys())
    keys = keys.intersection(process_tags)

    for k in keys:
        value = context[k]

        # Only process strings
        if not isinstance(value, str):
            continue

        context[k] = TagFactory.tag(tag_name=k, tag_content=value,
                                    tag_attributes='', context=context)

    return context
