"""
Tags for figure captions and references.
"""
from .tag import Tag
from .label import LabelMixin
from .utils import content_to_str
from ..formats import tex_cmd
from ..utils.string import hashtxt


class CaptionError(Exception):
    """An error was encountered in processing a caption."""
    pass


class Caption(Tag, LabelMixin):
    """A tag for captions.

    .. note:: The use of a naked caption tag is allowed (i.e. a caption not
              nested within a figure or table), but this won't register a label
              with the label manager. In order to create a label, the
              create_label method in the LabelMixin must be invoked.

              :example:

                 ::

                    @fig{@img{image.svg}
                         @caption{My first figure}
                        }
    """

    # Render captions as <span> because the <caption> tag is a block element,
    # and captions can be rendered inline
    html_name = 'span'
    html_class = 'caption'
    tex_cmd = 'caption'

    kind = None
    active = True

    def __init__(self, *args, **kwargs):
        # Call the tag constructor, but not the LabelMixin construction.
        # The create_label method of LabelMixin must be invoked separately.
        Tag.__init__(self, *args, **kwargs)

        # Set the attributes to the class
        if 'class' not in self.attributes:
            self.attributes['class'] = 'caption'

    def generate_label_id(self):
        """Generate the label id and set the id in the attributes."""
        if self.label_id is not None:
            label_id = self.label_id
        elif 'id' in self.attributes:
            label_id = self.attributes['id']
        else:
            text = self.default_fmt()
            label_id = 'caption-' + hashtxt(text)

        # Set the 'id' attributes
        self.attributes['id'] = label_id
        return label_id

    def generate_label_kind(self):
        return self.kind if self.kind is not None else ('caption',)

    def default_fmt(self, attributes=None, content=None):
        # Prepare the content with the label. References for the default format
        # are not supported
        content = ''
        if self.label_tag is not None:
            content += self.label_tag.default_fmt()
        content += content_to_str(self.content)

        return super().default_fmt(content=content, attributes=attributes)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        cls_name = self.__class__.__name__.lower()
        content = ''

        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        if self.label_tag is not None:
            content += self.label_tag.tex_fmt(mathmode=mathmode,
                                              level=level)

        # Format the tag's contents into a string
        content += content_to_str(self.content, target='.tex',
                                  mathmode=mathmode, level=level)

        # Format the heading tag. ex: \chapter{Chapter 1. My First Chapter}
        content = tex_cmd(cls_name, attributes=self.attributes,
                          formatted_content=content)

        if self.label_anchor is not None:
            content += ' ' + self.label_anchor.tex_fmt(mathmode=mathmode,
                                                       level=level)

        return content

    def html_fmt(self, content=None, **kwargs):
        # Prepare the tag contents to include the label tag.
        # ex: 'My Title' becomes 'Chap 1. My Title'
        content = []
        if self.label_tag is not None:
            content.append(self.label_tag)

        if isinstance(self.content, list):
            content += self.content
        else:
            content.append(self.content)

        return super().html_fmt(content=content, **kwargs)
