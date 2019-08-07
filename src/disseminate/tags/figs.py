"""
Tags for figure environments.
"""
from .tag import Tag
from .caption import Caption


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

    html_name = 'marginfig'
    tex_env = 'marginfigure'
    active = True
