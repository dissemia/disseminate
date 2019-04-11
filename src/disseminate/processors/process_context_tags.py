"""
Processor for tags in contexts.
"""
from .process_context import ProcessContext
from ..tags import Tag


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

    order = 500
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

        for k in keys:
            context[k] = Tag(name=k, content=context[k], attributes='',
                             context=context)
        return context
