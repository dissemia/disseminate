"""
Core classes and functions for tags.
"""
import lxml


class TagFactory(object):
    pass

class Tag(object):

    tag_type = None
    tag_content = None
    tag_attributes = None

    def __init__(self, tag_type, tag_content, tag_attributes):
        self.tag_type = tag_type
        self.tag_attributes = tag_attributes
        if isinstance(tag_content, list) and len(tag_content) == 1:
            self.tag_content = tag_content[0]
        else:
            self.tag_content = tag_content

    def __repr__(self):
        return "{type}{{{content}}}".format(type=self.tag_type,
                                            content=self.tag_content)

    def html(self):
        """The html string for the tag, if the output target is html."""
        if isinstance(self.tag_content, list):

            return ("<{tag}>"
                    "{content}</{tag}>".format(tag=esc(self.tag_type),
                                               content=esc(self.tag_content)))
        else:
            return "<{tag} />".format(tag=esc(self.tag_type))

    def default(self):
        """The default string for the tag, if no other format matches."""
        return self.tag_content