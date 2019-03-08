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
        return self.get_content()

    @content.setter
    def content(self, value):
        pass

    def get_content(self, content=None, seen=None):
        """Retrieve the tag's content from the context.

        This method replaces the inner substitution tags with strings to avoid
        recursion loops.
        """
        # Setup the set for Substitution tag names that have already been
        # retrieved so that they will only be retrieved once. This set avoids
        # recursive substitutions
        seen = set() if seen is None else seen

        # Next retrieve the contents of this tag from the context, if needed
        if content is None:
            if self.name in self.context and self.name not in seen:
                seen.add(self.name)
                content = self.context[self.name]
            else:
                content = ''

        # Further process the content elements, which may include Substitution
        # sub tags
        if isinstance(content, list):
            # If the content is a list, further process each item of the content
            for i, item in enumerate(content):
                if isinstance(item, Substitution):
                    content[i] = (item.get_content(seen=seen) if item.name
                                  not in seen else '')
                else:
                    # The item itself may have nested tags, so process these
                    # as above
                    content[i] = self.get_content(content=item, seen=seen)
        elif isinstance(content, Substitution):
            # If the content is a Substitution tag itself, retrieve its
            # entry from the context if it hasn't been retrieved already.
            if content.name in seen:
                content = ''
            else:
                seen.add(content.name)
                content = self.context[content.name]
        elif hasattr(content, 'content'):
            content.content = self.get_content(content=content.content,
                                               seen=seen)

        return content

    def default_fmt(self, content=None):
        content = self.get_content() if content is None else None
        # If the content has a default format method, use that directly.
        # Otherwise wrap the content in a substitution tag
        if hasattr(content, 'default_fmt'):
            return content.default_fmt()
        else:
            return super().default_fmt(content=content)

    def html_fmt(self, level=1, content=None):
        content = self.get_content() if content is None else None
        # If the content has a html format method, use that directly.
        # Otherwise wrap the content in a substitution tag
        if hasattr(content, 'html_fmt'):
            return content.html_fmt(level=level)
        else:
            return super().html_fmt(level=level, content=content)

    def tex_fmt(self, level=1, mathmode=False, content=None):
        content = self.get_content() if content is None else None
        # If the content has a default format method, use that directly.
        # Otherwise wrap the content in a substitution tag
        if hasattr(content, 'tex_fmt'):
            return content.tex_fmt(level=level, mathmode=mathmode)
        else:
            return super().tex_fmt(level=level, mathmode=mathmode,
                                   content=content)
