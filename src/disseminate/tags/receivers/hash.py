"""
Calculate the hash for a tag's contents.
"""

from ..signals import tag_created
from ...utils.string import hashtxt


@tag_created.connect_via(order=50)
def process_hash(tag, tag_factory, **kwargs):
    """A receiver to create a hash for the contents of tags."""
    content = tag.content
    if isinstance(content, str):
        tag.hash = hashtxt(tag.content)
    return tag
