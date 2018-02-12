"""
Image tags
"""
from .core import Tag, TagError
from ..attributes import set_attribute
from .. import settings


class Img(Tag):
    """The img tag for inserting images."""

    src_filepath = None
    manage_dependencies = True

    def __init__(self, name, content, attributes,
                 local_context, global_context):
        super(Img, self).__init__(name, content, attributes, local_context,
                                  global_context)

        # Place the image location in the src attribute
        if self.attributes is None:
            self.attributes = []

        contents = self.content.strip()
        self.content = None

        if contents:
            self.src_filepath = contents
        else:
            msg = "An image path must be used with the img tag."
            raise TagError(msg)

    def tex(self, level=1):
        if self.manage_dependencies:
            # Add the file dependency
            assert '_dependencies' in self.global_context
            deps = self.global_context['_dependencies']
            deps.add_file(targets=['.tex'], path=self.src_filepath)
            dep = deps.get_dependency(target='.tex',
                                      src_filepath=self.src_filepath)
            path = dep.dep_filepath
        else:
            path = self.src_filepath

        return "\\includegraphics{{{}}}".format(path)

    def html(self, level=1):
        if self.manage_dependencies:
            # Add the file dependency
            assert '_dependencies' in self.global_context
            deps = self.global_context['_dependencies']
            deps.add_file(targets=['.html'], path=self.src_filepath)
            dep = deps.get_dependency(target='.html',
                                      src_filepath=self.src_filepath)
            url = dep.url
        else:
            url = self.src_filepath

        # Use the parent method to render the tag. However, the 'src' attribute
        # should be fixed first.
        self.attributes = set_attribute(self.attributes, ('src', url),
                                        method='r')
        return super(Img, self).html(level)
