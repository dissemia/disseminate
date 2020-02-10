"""
Tags for tables
"""
from .tag import Tag
from .data import Data
from .caption import Caption
from ..formats.tex import tex_env


class BaseTable(Tag):
    """A base tag for all tables"""

    active = False
    tex_env = 'table'
    html_name = 'table'
    html_class = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Transfer the label id ('id') to the caption, if available. First,
        # find the caption tag, if available
        captions = [tag for tag in self.flatten(filter_tags=True)
                    if isinstance(tag, Caption)]

        for caption in captions:
            # Transfer the 'id' to the caption (but only the first)
            caption.label_id = self.attributes.pop('id', None)

            # Set the label kind for the caption as a figure caption
            caption.kind = ('caption', 'figure')

            # Create the label in the label_manager
            caption.create_label()

    def html_fmt(self, content=None, attributes=None, level=1):
        # Setup the html class, if specified
        attributes = (attributes if attributes is not None else
                      self.attributes.filter(target='.html'))
        if self.html_class is not None:
            if 'class' in attributes:
                attributes['class'] += " " + self.html_class
            else:
                attributes['class'] = self.html_class

        # Collect the contents of this table and prepare in a list
        content = content if content is not None else self.content
        content = [content] if not isinstance(content, list) else content

        # Render the html for the content
        content_html = []
        for item in content:
            if item == self:
                # The flatten method will also return the self tag. To avoid
                # recursion, do not process this tag.
                continue
            elif isinstance(item, Data):
                # Process the data in the table
                content_html += item.html_table(level=level+1)
            elif isinstance(item, Tag):
                # Process other tags like captions
                content_html.append(item.html_fmt(level=level + 1))
            else:
                content_html.append(item)

        # Return the formatted table
        return super().html_fmt(content=content_html, attributes=attributes,
                                level=level)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Collect the contents of this table and prepare in a list
        content = content if content is not None else self.content
        content = [content] if not isinstance(content, list) else content

        # Render the html for the content
        content_tex = []
        for item in content:
            if item == self:
                # The flatten method will also return the self tag. To avoid
                # recursion, do not process this tag.
                continue
            elif isinstance(item, Data):
                # Process the data in the table into a tabular environment
                table_tex = item.tex_table(level=level + 1)
                col_types = 'c' * item.num_cols
                content_tex += tex_env('tabular', attributes=col_types,
                                       formatted_content=table_tex)
            elif isinstance(item, Tag):
                # Process other tags like captions
                content_tex.append(item.tex_fmt(level=level + 1))
            else:
                content_tex.append(item)

        # Return the formatted table
        return super().tex_fmt(content=content_tex, attributes=attributes,
                               level=level)



class MarginTable(BaseTable):
    """The @margintable tag"""

    aliases = ('margintbl',)
    html_class = 'margintbl'
    tex_env = 'margintable'
    active = True


class Table(BaseTable):
    """The @table tag"""

    aliases = ('tbl',)
    tex_env = 'table'
    active = True


class FullTable(BaseTable):
    """The @fulltable tag"""

    aliases = ('ftbl', 'fulltbl')
    html_class = 'fulltable'
    tex_env = 'table*'
    active = True
