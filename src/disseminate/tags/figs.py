"""
Tags for figure environments.
"""
from .core import Tag
from .caption import Caption, CaptionError
from ..attributes import get_attribute_value, remove_attribute


class BaseFigure(Tag):
    """A base class for a figure tag.

    The BaseFigure initializes figures by adding 'id' attributes to labels in
    the label manager and reorganizing captions to the bottom of the figure.
    """

    def __init__(self, name, content, attributes, context):
        super(BaseFigure, self).__init__(name, content, attributes, context)

        # Register the caption as a label, if there's a caption in the contents
        id = get_attribute_value(self.attributes, 'id')
        self.attributes = remove_attribute(self.attributes, 'id')

        # Get the caption tag from the content. If the caption is in a list
        # in the content, then place it last
        if isinstance(self.content, list):
            caption = [i for i in self.content if isinstance(i, Caption)]
            if len(caption) > 1:
                msg = "Only one caption can be used for a figure"
                raise CaptionError(msg)
            caption = caption[0] if len(caption) == 1 else None
            new_content = [i for i in self.content
                           if not isinstance(i, Caption)]

            # Add the caption if it's present
            if caption is not None:
                new_content.append(caption)

            self.content = new_content

        elif isinstance(self.content, Caption):
            caption = self.content

        else:
            caption = None

        if caption is not None:
            caption.add_label(context=context, kind='figure', id=id)


class Marginfig(BaseFigure):

    html_name = 'marginfig'
    tex_name = 'marginfigure'
    active = True
