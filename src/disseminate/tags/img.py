"""
Image tags
"""
from .core import Tag
from disseminate.attributes import set_attribute


class Img(Tag):
    """The img tag for inserting images."""

    def __init__(self, name, content, attributes):
        super(Img, self).__init__(name, content, attributes)

        # Place the image location in the src attribute
        if self.attributes is None:
            self.attributes = []

        contents = self.content.strip()
        self.content = None

        if contents:
            self.attributes = set_attribute(self.attributes,
                                            ('src', contents),
                                            method='r')

