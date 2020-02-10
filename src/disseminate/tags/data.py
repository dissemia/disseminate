"""
Tags for data sources
"""
import abc
from io import StringIO

import pandas as pd

from .tag import Tag
from .utils import format_content
from ..paths.utils import find_files
from ..formats.html import html_tag
from ..formats.tex import tex_cmd


class Cell(Tag):
    """A cell in a table"""

    active = True
    html_name = 'td'


class HeaderCell(Tag):
    """A header cell in a table"""

    active = True
    html_name = 'th'



class Data(Tag):
    """A container for data."""

    dataframe = None
    active = False

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)
        # See if the content containts filenames or the actual data
        filepaths = find_files(string=content, context=context)

        if filepaths:
            # If it's a filepath, send that to the load function
            self.dataframe = self.load(filepaths[0])
        else:
            # Otherwise consider that its data. Load that.
            self.dataframe = self.load(StringIO(content))

    @abc.abstractmethod
    def load(self, filepath_or_buffer):
        """Load the data from a filepath or a string buffer.

        Parameters
        ----------
        filepath_or_buffer : Union[:obj:`pathlib.Path`, str, :obj:`io.StringIO`]
            The filename and path (filepath) or string buffer.

        Returns
        -------
        dataframe : :obj:`pandas.DataFrame`
            The processed dataframe
        """
        pass

    @property
    def headers(self):
        """The list of the data headers"""
        return (None if 'noheader' in self.attributes else
                list(self.dataframe.columns))

    @property
    def parsed_headers(self):
        """The list of the data headers in which the columns are formatted into
        Cell tags."""
        headers = self.headers
        if headers is None:
            return None
        return [HeaderCell(name='cell', content=str(header), attributes='',
                           context=self.context) for header in headers]

    @property
    def rows(self):
        """An iterator for the data rows"""
        return self.dataframe.itertuples()

    @property
    def parsed_rows(self):
        """An iterator for data rows in which columns are formatted into Cell
        tags."""
        for row in self.rows:
            parsed = [Cell(name='cell', content=str(i), attributes='',
                           context=self.context)
                      for i in row[1:]]
            yield (row[0],) + tuple(parsed)

    @property
    def num_cols(self):
        """The number of columns in the data"""
        columns = getattr(self.dataframe, 'columns', None)
        return len(columns) if columns is not None else None

    @property
    def num_rows(self):
        """The number of columns in the data"""
        rows = getattr(self.dataframe, 'columns', None)
        return len(rows) if rows is not None else None


class DelimData(Data):
    """A container for delimiter data (ex: comma-separated values)"""

    active = True
    aliases = ('csv', 'tsv')
    delimiter = None

    def __init__(self, name, content, attributes, context, delimiter=','):
        self.delimiter = delimiter
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

    def load(self, filepath_or_buffer, delimiter=None):
        delimiter = delimiter if delimiter is not None else self.delimiter
        if 'noheader' in self.attributes:
            return pd.read_csv(filepath_or_buffer, engine='c', header=None,
                               skipinitialspace=True, delimiter=delimiter)
        else:
            return pd.read_csv(filepath_or_buffer, engine='c',
                               skipinitialspace=True, delimiter=delimiter)

    def html_table(self, content=None, attributes=None, level=1):
        headers = self.parsed_headers

        # Prepare the header row, if a header is available
        elements = []
        if headers is not None:
            header_row = [format_content(cell, 'html_fmt', level=level)
                          for cell in headers]

            tr = html_tag('tr', formatted_content=header_row, level=level)
            thead = html_tag('thead', formatted_content=tr,
                             level=level)
            elements.append(thead)

        # Prepare each row individually. Each row is a named tuple with the
        # first element as the index
        rows = []
        for row in self.parsed_rows:
            body_row = [format_content(cell, 'html_fmt', level=level)
                        for cell in row[1:]]

            tr = html_tag('tr', formatted_content=body_row, level=level)
            rows.append(tr)

        tbody = html_tag('tbody', formatted_content=rows, level=level)
        elements.append(tbody)

        return elements

    def tex_table(self, content=None, attributes=None, mathmode=False, level=1):
        headers = self.parsed_headers

        tex = tex_cmd('toprule') + "\n"

        if headers is not None:
            tex += " && ".join([format_content(cell, 'tex_fmt',
                                               mathmode=mathmode, level=level)
                                for cell in headers]) + "\n"
            tex += tex_cmd('midrule') + "\n"

        for row in self.parsed_rows:
            tex += " && ".join([format_content(cell, 'tex_fmt',
                                               mathmode=mathmode, level=level)
                                for cell in row[1:]]) + "\n"

        tex += tex_cmd('bottomrule')
        return tex



