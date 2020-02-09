"""
Tags for data sources
"""
import abc
from io import StringIO

import pandas as pd

from .tag import Tag
from ..paths.utils import find_files
from ..formats.html import html_tag


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
        """The a list of the data headers"""
        return (None if 'noheader' in self.attributes else
                list(self.dataframe.columns))

    @property
    def rows(self):
        """An iterator for the data rows"""
        return self.dataframe.itertuples()


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
        headers = self.headers

        # Prepare the header row, if a header is available
        elements = []
        if headers is not None:
            header_row = [html_tag('th', attributes=attributes,
                                   formatted_content=header, level=level)
                          for header in headers]
            tr = html_tag('tr', formatted_content=header_row, level=level)
            thead = html_tag('thead', formatted_content=tr,
                             level=level)
            elements.append(thead)

        # Prepare each row individually. Each row is a named tuple with the
        # first element as the index
        rows = []
        for row in self.rows:
            body_row = [html_tag('td', formatted_content=str(item), level=level)
                        for item in row[1:]]
            tr = html_tag('tr', formatted_content=body_row, level=level)
            rows.append(tr)

        tbody = html_tag('tbody', formatted_content=rows, level=level)
        elements.append(tbody)

        return elements

