"""
Processor for tags in contexts.
"""
from ..tags import Tag


def process_context_tags(context):
    """Process the tags in the context.

    This function converts tags for context entries identified by keys listed
    in the 'process_context_tags' context entry

    .. note:: This function is designed to work with string macro entries. These
              are identified by context entries with keys that start with the
              settings.tag_prefix (e.g. '@test'). These *should not* be
              converted into asts, as they are required for simple string
              replacement.

    Parameters
    ----------
    context : dict, optional
        The context with values for the document.
    """
    assert context.is_valid('process_context_tags')
    process_tags = context['process_context_tags']

    for k in process_tags:
        context[k] = Tag(name=k, content=context[k], attributes='',
                         context=context)

    return context
