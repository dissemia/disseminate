"""
Tags for document preambles.
"""
from .tag import Tag
from .headings import Title
from ..formats import xhtml_tag
from ..utils.string import str_to_list


class Authors(Tag):
    """A tag for listing the author or authors."""

    aliases = ('author',)
    active = True

    def __init__(self, name, context, **kwargs):
        super(Authors, self).__init__(name=name, context=context, **kwargs)

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

    def tex_fmt(self, *args, **kwargs):
        return self.author_string()

    def html_fmt(self, content=None, method='html', level=1, *args, **kwargs):
        return xhtml_tag('span', attributes='class=authors',
                         formatted_content=self.author_string(),
                         method=method, level=level)


class Titlepage(Tag):
    """A titlepage tag."""

    authors_tag = None
    active = True

    def __init__(self, name, content, attributes, context):
        super(Titlepage, self).__init__(name, content, attributes, context)

        # Setup the title tag
        self.title_tag = Title(name='title', content='', attributes='',
                               context=context)

        # Setup the author tag
        self.authors_tag = Authors(name='authors', content='',
                                   attributes=tuple(), context=context)

    @property
    def title(self):
        """The title of the project"""
        return self.context.get('title', '')

    @property
    def authors(self):
        """The authors of the document"""
        if 'document' in self.context:
            doc = self.context['document']
            if hasattr(doc, 'author'):
                return doc.author
        if 'author' in self.context:
            return self.context['author']

    def html_fmt(self, content=None, attributes=None, format_func='html_fmt',
                 method='html', level=1, **kwargs):
        title_tag = self.title_tag
        title_html = getattr(title_tag, format_func)(method=method,
                                                     level=level + 1)
        authors_tag = self.authors_tag
        authors_html = getattr(authors_tag, format_func)(content=content,
                                                         method=method,
                                                         level=level + 1)
        return xhtml_tag('div', attributes='class=title-page',
                         formatted_content=[title_html, authors_html],
                         method=method, level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1,
                **kwargs):
        return "\n\\maketitle\n\n"
