"""
Test the ref_labels receivers
"""
from disseminate.tags import Tag
from disseminate.tags.receivers.ref_labels import (get_ref_label_ids,
                                                   find_ref_labels)


def test_get_ref_label_ids(context):
    """Test the get_ref_label_ids function"""
    # Prepare a ref tag
    src = """
    @chapter[id=test]{caption}
    "@ref{test}"
    """

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)

    assert get_ref_label_ids(root) == {'test'}


def test_find_ref_labels(doc):
    """Test the find_ref_labels function."""
    context = doc.context

    # Prepare a ref tag
    src = """
        @chapter[id=test]{caption}
        "@ref{test}"
        """

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)

    context['root'] = root
    find_ref_labels(doc)
    assert context['ref_label_ids'] == {'test'}
