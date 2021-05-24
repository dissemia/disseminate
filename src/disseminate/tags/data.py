"""
Tags for data sources
"""
import abc
import csv
from collections import OrderedDict

from .tag import Tag
from .utils import format_content
from ..utils.list import transpose
from ..paths.utils import load_io_stream
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
    data : Dict[Union[str, int], Tuple(str)]
        A data dict with the column names (str) or column index (int) as keys
        and the rows (tuple) as values.
    processed_headers : Union[List[:obj:`tags.Tag`], None]
        The headers processed into tags
    processed_rows : List[List[:obj:`tags.tag`]]
        The rows processed into tags
    """

    active = False
    process_content = False

    data = None
    processed_headers = None
    processed_rows = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Load the content
        self.load(content)

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
        """Process the tags for the items in the tag's data."""
        assert self.data is not None, "Data not loaded."

        # Process the headers, if needed
        headers = self.headers
        if (self.processed_headers is None and
           'noheader' not in self.attributes):
            hdrs = [HeaderCell(name='cell', content=str(header), attributes='',
                               context=self.context) for header in headers]
            self.processed_headers = hdrs

        # Process the rows, if needed
        if self.processed_rows is None:
            rows = []
            for row in self.rows_transpose:
                parsed = [Cell(name='cell', content=str(i), attributes='',
                               context=self.context)
                          for i in row]
                rows.append(tuple(parsed))
            self.processed_rows = rows

    @property
    def headers(self):
        """The tuple of the data headers"""
        return tuple(self.data.keys())

    @property
    def rows(self):
        """An iterator for the data rows"""
        return (row for row in self.data.values())

    @property
    def rows_transpose(self):
        """An iterator for the data rows (transposed)"""
        rows = [row for row in self.data.values()]
        return (tuple(row) for row in transpose(rows))

    @property
    def num_cols(self):
        """The number of columns in the data"""
        return len(self.data) if self.data is not None else None

    @property
    def num_rows(self):
        """The number of columns in the data"""
        if self.data is None:
            return None
        first_key = self.data.keys()[0]
        first_row = self.data[first_key]
        return len(first_row)


class DelimData(Data):
    """A container for delimiter data (ex: comma-separated values)"""

    active = True
    aliases = ('csv', 'tsv')
    delimiter = None
    skipinitialspace = True

    def __init__(self, delimiter=',', *args, **kwargs):
        self.delimiter = delimiter
        super().__init__(*args, **kwargs)

    def load(self, filepath_or_buffer, delimiter=None):
        if self.data is None:
            delimiter = delimiter if delimiter is not None else self.delimiter

            # Load a file or string stream from the filepath_or_buffer
            stream = load_io_stream(filepath_or_buffer, context=self.context)

            # Parse the csv data.
            # first_row is an len(cols) list
            # rows is a len(rows) list of len(cols) lists
            csv_reader = csv.reader(stream, delimiter=delimiter,
                                    skipinitialspace=self.skipinitialspace)
            first_row = next(csv_reader)
            rows = [row for row in csv_reader]

            # Transpose the rows so that rows is a len(cols) list of len(rows)
            # lists
            rows = transpose(rows)

            # Convert the rows into a data dict with the keys as column names
            # (header) or column numbers (no header)
            data = OrderedDict()

            if 'noheader' in self.attributes:
                # Prepend the first row to each row
                for col_num, (first, row) in enumerate(zip(first_row, rows)):
                    row.insert(0, first)
                    data[col_num] = tuple(row)
            else:
                # Use the first_row as the column names
                for first, row in zip(first_row, rows):
                    data[first] = tuple(row)

            # Set the data attributes
            self.data = data

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
                              for cell in row]) + " \\\\\n"
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
                        for cell in row]

            tr = xhtml_tag('tr', formatted_content=body_row, method=method,
                           level=level)
            rows.append(tr)

        tbody = xhtml_tag('tbody', formatted_content=rows, method=method,
                          level=level)
        elements.append(tbody)

        return elements
