"""
Processor for tags in contexts.
"""
from .process_context import ProcessContext
from ...tags import Tag, TagFactory


class ProcessContextTags(ProcessContext):
    """Process the tags in the context.

    This function converts tags for context entries identified by keys listed
    in the 'process_context_tags' context entry

    .. note:: This function is designed to work with string macro entries. These
              are identified by context entries with keys that start with the
              settings.tag_prefix (e.g. '@test'). These *should not* be
              converted into asts, as they are required for simple string
              replacement.
    """

    order = 1000
    short_desc = ("Convert context entries into tags for entries listed the "
                  "'process_context_tags' context entry")

    def __call__(self, context):
        assert context.is_valid('process_context_tags')

        # Find the tags to process, based on the context entries in the
        # 'process_context_tags' entry of the context and the available context
        # entries
        process_tags = context['process_context_tags']
        keys = set(context.keys())
        keys = keys.intersection(process_tags)

        # Create a tag factory to create new tags
        factory = TagFactory(tag_base_cls=Tag)

        for k in keys:
            value = context[k]

            # Only process strings
            if not isinstance(value, str):
                continue

            context[k] = factory.tag(tag_name=k,
                                     tag_content=value,
                                     tag_attributes='',
                                     context=context)

        return context
