"""
Tags to insert values from entries in the context (macros).
"""
from .core import Tag
from .utils import repl_tags


class Substitution(Tag):
    """A macro tag draws its content from the value of a header entry matching
    the tag's name.

    A substitution tag doesn't have its own content; it uses the content from
    an entry in the context. For this reason, the content attribute only
    contains the empty string. The rendering methods, like default_fmt,
    html_fmt and tex_fmt, access the content of the context with the
    `get_content` method.
    """

    active = True

    @property
    def content(self):
        return ''

    @content.setter
    def content(self, value):
        pass

    def get_content(self):
        """Retrieve the tag's content from the context.

        This method replaces the inner substitution tags with strings to avoid
        recursion loops.
        """
        content = self.context[self.name] if self.name in self.context else ''

        # Turn the content into a string, if needed
        if not isinstance(content, str) and not isinstance(content, Tag):
            content = str(content)

        # Remove any substitutions within contents
        content = repl_tags(element=content, tag_class=Substitution,
                            replacement='')

        return content

    def default_fmt(self, content=None):
        content = self.get_content() if content is None else None
        return super().default_fmt(content=content)

    def html_fmt(self, level=1, content=None):
        content = self.get_content() if content is None else None
        return super().html_fmt(level=level, content=content)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = self.get_content() if content is None else None
        return super().tex_fmt(level=level, mathmode=mathmode, content=content)
