"""
Tags to render asymptote (asy) figures and diagrams
"""
from .img import RenderedImg


class Asy(RenderedImg):
    """The asy tag for inserting asymptote images."""

    src_filepath = None
    active = True

    def __init__(self, name, content, attributes, context):
        super(Asy, self).__init__(name=name, content=content,
                                  attributes=attributes,
                                  context=context,
                                  render_target='.asy')
