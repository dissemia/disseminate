"""
Test the caption and reg tags.
"""
import pathlib

from disseminate import TargetPath
from disseminate.tags import Tag
from disseminate.labels import LabelManager


def test_naked_caption(tmpdir, context_cls):
    """Tests the parsing of naked captions (i.e. those not nested in a figure
    or table)."""
    tmpdir = pathlib.Path(tmpdir)

    # Create the context and a label manager
    target_root = TargetPath(target_root=tmpdir)
    context = context_cls(target_root=target_root)
    label_man = LabelManager(root_context=context)
    context['label_manager'] = label_man

    # Generate the markup without an id
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.name == 'caption'
    assert caption.attributes == {}
    assert caption.content == 'This is my caption'

    # Naked captions do not register labels
    assert len(label_man.labels) == 0

