"""
Tags for data sources
"""
import abc
from io import StringIO

import pandas as pd

from .tag import Tag
from .utils import format_content
from ..paths.utils import find_files
from ..formats.xhtml import xhtml_tag
from ..formats.tex import tex_cmd


class Cell(Tag):
    """A cell in a table"""

    active = True
    html_name = 'td'

    def tex_fmt(self, **kwargs):
        tex = super().tex_fmt(**kwargs)
        tex = tex.replace('&', '\\&')
        return tex


class HeaderCell(Tag):
    """A header cell in a table"""

    active = True
    html_name = 'th'

    def tex_fmt(self, **kwargs):
        tex = super().tex_fmt(**kwargs)
        tex = tex.replace('&', '\\&')
        return tex


class Data(Tag):
    """A container for data.

    Attributes
    ----------
    dataframe : :obj:`pandas.DataFrame`
        The raw data parsed in a dataframe
    processed_headers : Union[List[:obj:`tags.Tag`], None]
        The headers processed into tags
    processed_rows : List[List[:obj:`tags.tag`]]
        The rows processed into tags
    """

    active = False
    process_content = False

    dataframe = None
    processed_headers = None
    processed_rows = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)
        # See if the content containts filenames or the actual data
        filepaths = find_files(string=content, context=context)

        if filepaths:
            # If it's a filepath, send that to the load function
            self.load(filepaths[0])
        else:
            # Otherwise consider that its data. Load that.
            self.load(StringIO(content))

    @abc.abstractmethod
    def load(self, filepath_or_buffer):
        """Load the dataframe from a filepath or a string buffer.

        Parameters
        ----------
        filepath_or_buffer : Union[:obj:`pathlib.Path`, str, \
        :obj:`io.StringIO`]
            The filename and path (filepath) or string buffer.
        """
        pass

    def process_tags(self):
        """Process the tags for the items in the dataframe."""
        assert self.dataframe is not None, "Pandas dataframe not loaded."

        # Process the headers, if needed
        headers = self.headers
        if self.processed_headers is None and headers:
            hdrs = [HeaderCell(name='cell', content=str(header), attributes='',
                               context=self.context) for header in headers]
            self.processed_headers = hdrs

        # Process the rows, if needed
        if self.processed_rows is None:
            rows = []
            for row in self.rows:
                parsed = [Cell(name='cell', content=str(i), attributes='',
                               context=self.context)
                          for i in row[1:]]
                rows.append((row[0],) + tuple(parsed))
            self.processed_rows = rows

    @property
    def headers(self):
        """The list of the data headers"""
        return (None if 'noheader' in self.attributes else
                list(self.dataframe.columns))

    @property
    def rows(self):
        """An iterator for the data rows"""
        return self.dataframe.itertuples()

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

    def __init__(self, delimiter=',', *args, **kwargs):
        self.delimiter = delimiter
        super().__init__(*args, **kwargs)

    def load(self, filepath_or_buffer, delimiter=None):
        if self.dataframe is None:
            delimiter = delimiter if delimiter is not None else self.delimiter
            if 'noheader' in self.attributes:
                self.dataframe = pd.read_csv(filepath_or_buffer, engine='c',
                                             header=None,
                                             skipinitialspace=True,
                                             delimiter=delimiter)
            else:
                self.dataframe = pd.read_csv(filepath_or_buffer, engine='c',
                                             skipinitialspace=True,
                                             delimiter=delimiter)

    def tex_table(self, content=None, attributes=None, mathmode=False,
                  level=1):
        # Load the tags
        self.process_tags()

        headers = self.processed_headers
        tex = tex_cmd('toprule') + "\n"

        if headers is not None:
            tex += " & ".join([format_content(cell, 'tex_fmt',
                                              mathmode=mathmode, level=level)
                               for cell in headers]) + " \\\\\n"
            tex += tex_cmd('midrule') + "\n"

        rows = []
        for row in self.processed_rows:
            str = " & ".join([format_content(cell, 'tex_fmt', level=level,
                                                   mathmode=mathmode)
                              for cell in row[1:]]) + " \\\\\n"
            rows.append(str)
        tex += "".join(rows)

        tex += tex_cmd('bottomrule')
        return tex

    def html_table(self, format_func='html_fmt', method='html', level=1,
                   **kwargs):
        # Load the tags
        self.process_tags()

        headers = self.processed_headers

        # Prepare the header row, if a header is available
        elements = []
        if headers is not None:
            header_row = [format_content(cell, format_func, level=level)
                          for cell in headers]

            tr = xhtml_tag('tr', formatted_content=header_row, method=method,
                           level=level)
            thead = xhtml_tag('thead', formatted_content=tr, method=method,
                              level=level)
            elements.append(thead)

        # Prepare each row individually. Each row is a named tuple with the
        # first element as the index
        rows = []
        for row in self.processed_rows:
            body_row = [format_content(cell, format_func, level=level)
                        for cell in row[1:]]

            tr = xhtml_tag('tr', formatted_content=body_row, method=method,
                           level=level)
            rows.append(tr)

        tbody = xhtml_tag('tbody', formatted_content=rows, method=method,
                          level=level)
        elements.append(tbody)

        return elements
