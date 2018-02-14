"""
Image tags
"""
from .core import Tag, TagError
from ..attributes import set_attribute
from .. import settings


class Img(Tag):
    """The img tag for inserting images."""

    active = True

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
            # get the document_src_filepath
            lc = self.local_context
            if '_src_filepath' in lc:
                document_src_filepath = lc['_src_filepath']
            else:
                document_src_filepath = None

            # Add the file dependency
            assert '_dependencies' in self.global_context
            deps = self.global_context['_dependencies']
            deps.add_file(targets=['.tex'], path=self.src_filepath,
                          document_src_filepath=document_src_filepath)
            dep = deps.get_dependency(target='.tex',
                                      src_filepath=self.src_filepath)
            path = dep.dep_filepath
        else:
            path = self.src_filepath

        return "\\includegraphics{{{}}}".format(path)

    def html(self, level=1):
        if self.manage_dependencies:
            # get the document_src_filepath
            lc = self.local_context
            if '_src_filepath' in lc:
                document_src_filepath = lc['_src_filepath']
            else:
                document_src_filepath = None

            # Add the file dependency
            assert '_dependencies' in self.global_context
            deps = self.global_context['_dependencies']
            deps.add_file(targets=['.html'], path=self.src_filepath,
                          document_src_filepath=document_src_filepath)
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


def RenderedImg(Img):
    """An img base class for saving and caching an image that needs to be
    rendered by an external program.

    .. note:: This class is not intended to be directly used as a tag. Rather,
              it is intended to be subclassed for other image types that need
              to be rendered first.
    """

    active = False

    # def __init__(self, name, content, attributes,
    #              local_context, global_context, input, render_target):
