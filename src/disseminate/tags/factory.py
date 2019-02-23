"""
The Tag factory to select the correct tag classes and create tag objects.
"""
from .core import Tag
from ..utils.classes import all_subclasses


class TagFactory(object):
    """Generates the appropriate tag for a given tag type.

    The tag factory instantiates tags based on loaded modules and initialization
    parameters.
    """

    tag_clses = None
    substitution_cls = None

    def __init__(self):
        # Lazy initialization of the class. The tags can be cached because
        # the source code is assumed static once the program has started.
        if TagFactory.tag_clses is None:
            # Initialize the tag types dict.
            TagFactory.tag_clses = dict()

            for scls in all_subclasses(Tag):
                # Tag must be active
                if not scls.active:
                    continue

                # Collect the name and aliases (alternative names) for the tag
                aliases = (list(scls.aliases) if scls.aliases is not None else
                           list())
                names = [scls.__name__.lower(),] + aliases

                for name in names:
                    # duplicate or overwritten tag names are not allowed
                    assert name not in self.tag_clses
                    TagFactory.tag_clses[name] = scls

        if TagFactory.substitution_cls is None:
            substitution_cls = TagFactory.tag_clses.get('substitution')
            TagFactory.substitution_cls = substitution_cls

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

        # Try to find the appropriate subclass
        small_tag_type = tag_name.lower()
        if small_tag_type in self.tag_clses:
            # First, see if the tag_name matches one of the tag subclasses (or
            # tag aliases) in disseminate
            cls = self.tag_clses[small_tag_type]
        elif small_tag_type in context and self.substitution_cls:
            # If not, this might be a substitution, which uses a 'Substitution'
            # tag to insert the contents of an entry in the context.
            cls = self.substitution_cls
        else:
            # If all else fails, just make a generic Tag.
            cls = Tag

        # Create the tag
        tag = cls(name=tag_name, content=tag_content, attributes=tag_attributes,
                  context=context)
        return tag
