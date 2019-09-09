"""
Tags for figure environments.
"""
from .tag import Tag
from .caption import Caption
from .utils import format_content, format_attribute_width
from ..utils.string import strip_multi_newlines
from ..formats import tex_env, html_tag


class BaseFigure(Tag):
    """A base class for a figure tag.

    The BaseFigure initializes figures by adding 'id' attributes to labels in
    the label manager and reorganizing captions to the bottom of the figure.
    """

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Transfer the label id ('id') to the caption, if available. First,
        # find the caption tag, if available
        captions = [tag for tag in self.flatten(filter_tags=True)
                    if isinstance(tag, Caption)]

        for caption in captions:
            # Transfer the 'id' to the caption (but only the first)
            caption.label_id = self.attributes.pop('id', None)

            # Set the label kind for the caption as a figure caption
            caption.kind = ('caption', 'figure')

            # Create the label in the label_manager
            caption.create_label()


class Marginfig(BaseFigure):
    """The @marginfig tag"""

    html_name = 'marginfig'
    tex_env = 'marginfigure'
    active = True


class Figure(BaseFigure):
    """The @figure/@fig tag"""

    aliases = ('fig',)
    html_name = 'figure'
    tex_env = 'figure'
    active = True


class FullFigure(BaseFigure):
    """The @fullfigure/@ffig tag"""

    aliases = ('ffig', 'fullfig')
    html_name = 'fullfigure'
    tex_env = 'figure*'
    active = True


class Panel(Tag):
    """A panel (sub-figure) for a figure."""

    active = True
    html_name = 'panel'
    tex_env = 'minipage'

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Collect the content elements
        content = content if content is not None else self.content

        content = format_content(content=content, format_func='tex_fmt',
                                 level=level + 1, mathmode=mathmode)
        content = ''.join(content) if isinstance(content, list) else content

        # Format the width
        attrs = format_attribute_width(self.attributes, target='.tex')

        # Raises an error if a width is not present. Strip multiple newlines
        # as these break up side-by-side figures
        env = tex_env("panel", attributes=attrs, formatted_content=content)
        return strip_multi_newlines(env).strip()

    def html_fmt(self, content=None, attributes=None, level=1):
        # Collect the content elements
        content = content if content is not None else self.content
        content = format_content(content=content, format_func='html_fmt',
                                 level=level + 1)

        # Format the width
        attrs = format_attribute_width(self.attributes, target='.html')
        attrs['class'] = 'panel'

        return html_tag('span', attributes=attrs, formatted_content=content,
                        level=level)
