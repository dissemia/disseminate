"""
Tags for document preambles.
"""
from lxml.builder import E

from .core import Tag
from ..utils.string import str_to_list


class Authors(Tag):
    """A tag for listing the author or authors."""

    aliases = ('author',)

    def __init__(self, name, content, attributes, context):
        super(Authors, self).__init__(name, content, attributes, context)

        # Use the specified author list in the content, if specified, otherwise
        # try to get it from the context.
        if (isinstance(self.content, str) and self.content.strip() == "" or
           self.content is None):

            author = (context.get('author', '') if 'author' in context else
                      context.get('authors', ''))
            self.content = author

        # Convert the author string to a list
        if isinstance(self.content, str):
            self.content = str_to_list(self.content)

    def author_string(self):
        """Generate a formatted string listing the authors."""
        # Convert to a list of strings
        if isinstance(self.content, str):
            author_lst = str_to_list(self.content)
        elif isinstance(self.content, list):
            author_lst = self.content
        else:
            return ''

        # Convert to a list of authors
        if len(author_lst) == 0:
            return ''
        elif len(author_lst) == 1:
            return author_lst[0]
        else:
            last_two = author_lst[-2:]
            others = author_lst[:-2]

            if len(author_lst) == 2:
                return ', '.join(others) + ' and '.join(last_two)
            else:
                return ', '.join(others) + ', ' + ' and '.join(last_two)

    def html(self, level=1):
        return E('div', self.author_string(), **{'class': 'authors'})

    def tex(self, level=1, mathmode=False):
        return self.author_string()


class Titlepage(Tag):
    """A titlepage tag."""

    authors_tag = None

    def __init__(self, name, content, attributes, context):
        super(Titlepage, self).__init__(name, content, attributes, context)

        # Setup the author tag
        self.authors_tag = Authors(name='authors', content='',
                                   attributes=tuple(), context=context)

    @property
    def title(self):
        """The title of the document"""
        title = ''

        if 'document' in self.context:
            doc = self.context['document']
            if hasattr(doc, 'title'):
                title = doc.title
        elif 'title' in self.context:
            title = self.context['title']

        return title

    @property
    def authors(self):
        """The authors of the document"""
        if 'document' in self.context:
            doc = self.context['document']
            if hasattr(doc, 'author'):
                return doc.author
        if 'author' in self.context:
            return self.context['author']

    def html(self, level=1):
        return E('div',
                 E('h1', self.title, **{'class': 'title'}),
                 self.authors_tag.html(level+1),
                 **{'class': 'title-page'})

    def tex(self, level=1, mathmode=False):
        return "\n\\titlepage\n\n"
