"""
The Tag factory to select the correct tag classes and create tag objects.
"""
from ..utils.classes import all_subclasses


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.

    The tag factory instantiates tags based on loaded modules and initialization
    parameters.
    """

    _tag_classes = None

    def __init__(self, base_tag_class):
        self.base_tag_class = base_tag_class

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
        tag_classes = self.tag_classes
        if tag_name.lower() in tag_classes:
            # First, see if the tag_name matches one of the tag subclasses (or
            # tag aliases) in disseminate
            cls = tag_classes[tag_name.lower()]
        else:
            # If all else fails, just make a generic Tag.
            cls = self.base_tag_class

        # Create the tag
        tag = cls(name=tag_name, content=tag_content, attributes=tag_attributes,
                  context=context)
        return tag

    @property
    def tag_classes(self):
        """A dict of all the active Tag subclasses."""
        if TagFactory._tag_classes is None:
            tag_classes = dict()

            for scls in all_subclasses(self.base_tag_class):
                # Tag must be active
                if not scls.active:
                    continue

                # Collect the name and aliases (alternative names) for the tag
                aliases = (list(scls.aliases) if scls.aliases is not None else
                           list())
                names = [scls.__name__.lower(), ] + aliases

                for name in names:
                    # duplicate or overwritten tag names are not allowed
                    assert name not in tag_classes
                    tag_classes[name] = scls

            TagFactory._tag_classes = tag_classes

        return TagFactory._tag_classes
