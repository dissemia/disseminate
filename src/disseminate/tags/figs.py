"""
Tags for figure environments.
"""
from .tag import Tag
from .caption import Caption
from .utils import xhtml_percentwidth, tex_percentwidth
from ..utils.string import strip_multi_newlines
from .. import settings


class BaseFigure(Tag):
    """A base class for a figure tag.

    The BaseFigure initializes figures by adding 'id' attributes to labels in
    the label manager and reorganizing captions to the bottom of the figure.
    """

    # Render the figures as '<span>' elements in xhtml, instead of <figure>
    # elements becase <figure> elements are block level items--i.e. they
    # cannot be placed inside a paragraph.
    html_name = 'figure'
    active = False

    include_paragraphs = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Transfer the label id ('id') to the caption, if available. First,
        # find the caption tag, if available
        captions = [tag for tag in self.flatten(filter_tags=True)
                    if isinstance(tag, Caption)]

        for caption in captions:
            # Transfer the 'id' to the caption (but only the first)
            caption.label_id = self.attributes.pop('id', None)

            # Set the label kind for the caption as a figure caption
            caption.kind = ('caption', 'figure')

            # Make the caption a figcaption tag for html
            caption.html_name = 'figcaption'
            caption.html_class = 'figcaption'

            # Create the label in the label_manager
            caption.create_label()

    def html_fmt(self, attributes=None, method='html', **kwargs):
        attrs = attributes or self.attributes.copy()

        # Set the html class
        if self.html_class is not None:
            if 'class' in attrs:
                attrs['class'] = ' ' + self.html_class
            else:
                attrs['class'] = self.html_class
        return super().html_fmt(attributes=attrs, method=method, **kwargs)


class MarginFigure(BaseFigure):
    """The @marginfig tag"""

    aliases = ('marginfig',)
    html_class = 'marginfig'
    tex_env = 'marginfigure'
    active = True

    def xhtml_fmt(self, attributes=None, **kwargs):
        attributes = attributes or self.attributes.copy()
        attr_name = '{{{}}}type'.format(settings.xhtml_namespace['epub'])
        attributes[attr_name] = 'footnote'
        return super().xhtml_fmt(attributes=attributes, **kwargs)


class Figure(BaseFigure):
    """The @figure/@fig tag"""

    aliases = ('fig',)
    html_class = 'figure'
    tex_env = 'figure'
    active = True


class FullFigure(BaseFigure):
    """The @fullfigure/@ffig tag"""

    aliases = ('ffig', 'fullfig')
    html_class = 'fullfigure'
    tex_env = 'figure*'
    active = True


class Panel(Tag):
    """A panel (sub-figure) for a figure."""

    active = True
    html_name = 'panel'
    tex_env = 'panel'

    def tex_fmt(self, attributes=None, **kwargs):
        attrs = self.attributes.copy() if attributes is None else attributes

        # Format the width
        attrs = tex_percentwidth(attrs, target='.tex', use_positional=True)

        # Raises an error if a width is not present. Strip multiple newlines
        # as these break up side-by-side figures
        env = super().tex_fmt(attributes=attrs, **kwargs)
        return strip_multi_newlines(env).strip()

    def html_fmt(self, attributes=None, method='html', **kwargs):
        attrs = self.attributes.copy() if attributes is None else attributes
        target = '.' + method if not method.startswith('.') else method

        # Format the html classes
        attrs['class'] = 'panel'
        attrs = xhtml_percentwidth(attributes=attrs, target=target)
        return super().html_fmt(attributes=attrs, method=method, **kwargs)
