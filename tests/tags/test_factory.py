"""Test the TagFactory."""
from disseminate.tags import Tag, TagFactory


# Test tag classes
class Available(Tag):
    active = True


class Unavailable(Tag):
    active = False


def test_tag_factory_available(context_cls):
    """Tests that unavailable tags are not returned by the TagFactory."""

    context = context_cls()

    # 1. Try an instance of the available class
    available = TagFactory.tag(tag_name='available', tag_attributes='',
                               tag_content='', context=context)
    assert isinstance(available, Available)

    # 2. Try an instance of the Un class
    unavailable = TagFactory.tag(tag_name='unavailable', tag_attributes='',
                                 tag_content='', context=context)
    assert not isinstance(unavailable, Unavailable)


def test_tag_factory_inactive_tags(doc):
    """Tests the 'inactive_tags' entry of the context."""

    context = doc.context

    # 1. Try an instance of the available class
    available = TagFactory.tag(tag_name='available', tag_attributes='',
                               tag_content='', context=context)
    assert isinstance(available, Available)

    # 2. Disable the Available tag subclass from the context
    context['inactive_tags'] = {'available'}

    available = TagFactory.tag(tag_name='available', tag_attributes='',
                               tag_content='', context=context)
    assert not isinstance(available, Available)
