"""
Tags for figure environments.
"""
from .tag import Tag
from .caption import Caption
from .utils import format_attribute_width
from ..utils.string import strip_multi_newlines
from ..utils.types import StringPositionalValue


class BaseFigure(Tag):
    """A base class for a figure tag.

    The BaseFigure initializes figures by adding 'id' attributes to labels in
    the label manager and reorganizing captions to the bottom of the figure.
    """

    # Render the figures as '<span>' elements in xhtml, instead of <figure>
    # elements becase <figure> elements are block level items--i.e. they
    # cannot be placed inside a paragraph.
    # html_name = 'figure'
    html_name = 'span'
    active = False

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
            # caption.html_name = 'figcaption'
            caption.html_class = 'figcaption'

            # Create the label in the label_manager
            caption.create_label()

    def html_fmt(self, attributes=None, **kwargs):
        attrs = attributes if attributes is not None else self.attributes

        # Set the html class
        if self.html_class is not None:
            attrs = self.attributes.filter(target='.html')
            if 'class' in attrs:
                attrs['class'] = ' ' + self.html_class
            else:
                attrs['class'] = self.html_class

        return super().html_fmt(attributes=attrs, **kwargs)


class Marginfigure(BaseFigure):
    """The @marginfig tag"""

    aliases = ('marginfig',)
    html_class = 'marginfig'
    tex_env = 'marginfigure'
    active = True


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
        attrs = format_attribute_width(attrs, target='.tex')

        # Convert the width attribute to a StringPositional, which is needed
        # by the panel environment
        # ex: \begin{panel}{0.5\textwidth} \end{panel}
        width = attrs.get('width', target='.tex')
        if width is not None:
            attrs[width] = StringPositionalValue

        # Raises an error if a width is not present. Strip multiple newlines
        # as these break up side-by-side figures
        env = super().tex_fmt(attributes=attrs, **kwargs)
        return strip_multi_newlines(env).strip()

    def html_fmt(self, attributes=None, method='html', **kwargs):
        attrs = self.attributes.copy() if attributes is None else attributes
        target = '.' + method if not method.startswith('.') else method

        # Format the width
        attrs = format_attribute_width(attrs, target=method)
        attrs['class'] = 'panel'

        return super().html_fmt(attributes=attrs, method=method, **kwargs)
