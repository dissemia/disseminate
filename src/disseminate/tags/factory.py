"""
The Tag factory to select the correct tag classes and create tag objects.
"""
from ..utils.classes import all_subclasses


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.

    The tag factory instantiates tags based on loaded modules and initialization
    parameters.

    Parameters
    ----------
    tag_base_cls : :class:`Tag <disseminate.tags.tag.Tag>`
        The base class for Tag objects.
    """

    _tag_classes = None

    def __init__(self, tag_base_cls):
        self.tag_base_cls = tag_base_cls

    def tag(self, tag_name, tag_content, tag_attributes, context):
        """Return the approriate tag, given a tag_name and tag_content.

        A tag subclass, rather than the Tag base class, will be returned if

        - A tag subclass with the tag_name (or with an alias) is available.
        - The tag subclass has an 'active' attribute that is True
        - The tag's name isn't listed in the 'inactive_tags' set in the context.

        Parameters
        ----------
        tag_name : str
            The name of the tag. ex: 'bold', 'b'
        tag_content : Union[str, list]
            The content of the tag. ex: 'this is bold'
        tag_attributes : str
            The attributes of a tag. ex: 'width=32pt'
        context : dict
            The document's context dict.

        Returns
        -------
        tag : :obj:`Tag <disseminate.tags.Tag>`
            An instance of a Tag subclass.
        """
        cls = self.tag_class(tag_name=tag_name, context=context)

        # Create the tag
        tag = cls(name=tag_name, content=tag_content, attributes=tag_attributes,
                  context=context)
        return tag

    def tag_class(self, tag_name, context):
        """The retrieve the tag class for the given tag_name"""
        tag_classes = self.tag_classes
        tag_name_lower = tag_name.lower()
        tag_cls = tag_classes.get(tag_name_lower, None)

        if (tag_cls is not None and
                getattr(tag_cls, 'active', False) and
                tag_cls.__name__.lower() not in context.get('inactive_tags',
                                                            ())):
            # First, see if the tag_name matches one of the tag subclasses (or
            # tag aliases) in disseminate
            return tag_cls
        else:
            # If all else fails, just make a generic Tag.
            return self.tag_base_cls

    @property
    def tag_classes(self):
        """A dict of all the active Tag subclasses."""
        if TagFactory._tag_classes is None:
            tag_classes = dict()

            for scls in all_subclasses(self.tag_base_cls):
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
