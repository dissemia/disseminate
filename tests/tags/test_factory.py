"""Test the TagFactory."""
from disseminate.tags import Tag
from disseminate.tags.factory import TagFactory


# Test tag classes
class Available(Tag):
    active = True


class Unavailable(Tag):
    active = False


def test_tag_factory_available(context_cls):
    """Tests that unavailable tags are not returned by the TagFactory."""

    context = context_cls()
    factory = TagFactory(base_tag_class=Tag)

    # 1. Try an instance of the available class
    available = factory.tag(tag_name='available', tag_attributes='',
                            tag_content='', context=context)
    assert isinstance(available, Available)

    # 2. Try an instance of the Un class
    unavailable = factory.tag(tag_name='unavailable', tag_attributes='',
                              tag_content='', context=context)
    assert not isinstance(unavailable, Unavailable)



def test_tag_factory_inactive_tags(context_cls):
    """Tests the 'inactive_tags' entry of the context."""

    context = context_cls()
    factory = TagFactory(base_tag_class=Tag)

    # 1. Try an instance of the available class
    available = factory.tag(tag_name='available', tag_attributes='',
                            tag_content='', context=context)
    assert isinstance(available, Available)

    # 2. Disable the Available tag subclass from the context
    context['inactive_tags'] = {'available'}

    available = factory.tag(tag_name='available', tag_attributes='',
                            tag_content='', context=context)
    assert not isinstance(available, Available)
