"""
A tag for a feature box used in some textbooks (like examples)
"""
from .tag import Tag


class FeatureBox(Tag):
    """A box with a feature for some texts, like an Example or Note box.

    Attributes
    ----------
    active : bool
        This tag is active.
    include_paragraphs : bool
        The contents of this tag cannot be included in paragraphs.
    html_classes : str
        Classes to append in the html tag.
    """

    active = True
    include_paragraphs = False

    html_name = "div"
    html_classes = "featurebox"
    tex_env = "featurebox"

    def __init__(self, name, *args, **kwargs):
        super().__init__(name='featurebox', *args, **kwargs)

    def html_fmt(self, attributes=None, **kwargs):
        attributes = (self.attributes.copy() if attributes is None else
                      attributes)

        # Add the html attribute
        attributes['class'] = (attributes['class'] + " " + self.html_classes
                               if 'class' in attributes else self.html_classes)
        return super().html_fmt(attributes=attributes, **kwargs)


class ExampleBox(FeatureBox):
    """A box for examples"""

    html_classes = "featurebox examplebox"
    tex_env = "examplebox"


class ProblemBox(FeatureBox):
    """A box for problems"""

    html_classes = "featurebox problembox"
    tex_env = "problembox"
