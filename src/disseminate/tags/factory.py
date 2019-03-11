"""
The Tag factory to select the correct tag classes and create tag objects.
"""
from .core import Tag
from .. import settings


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.

    The tag factory instantiates tags based on loaded modules and initialization
    parameters.
    """

    def tag(self, tag_name, tag_content, tag_attributes, context):
        """Return the approriate tag, given a tag_name and tag_content.

        Parameters
        ----------
        tag_name : str
            The name of the tag. ex: 'bold', 'b'
        tag_content : str or list
            The content of the tag. ex: 'this is bold'
        tag_attributes : str
            The attributes of a tag. ex: 'width=32pt'
        context : dict
            The document's context dict.

        Returns
        -------
        :obj:`Tag subclass <disseminate.tags.core.Tag>`
            An tag.
        """
        if tag_name.lower() in settings.tag_classes:
            # First, see if the tag_name matches one of the tag subclasses (or
            # tag aliases) in disseminate
            cls = settings.tag_classes[tag_name.lower()]
        else:
            # If all else fails, just make a generic Tag.
            cls = Tag

        # Create the tag
        tag = cls(name=tag_name, content=tag_content, attributes=tag_attributes,
                  context=context)
        return tag
