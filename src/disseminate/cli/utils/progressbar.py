"""
CLI utilities
"""


def progress_builders(builders):
    """Returns the progress from a flattened list of builders.

    Parameters
    ----------
    builders : List[:obj:`.builders.Builder`]
        A flattened list of builders

    Returns
    -------
    done, total : Tuple[int, int]
        The number of done builders and the total number of builders.
    """
    return len([b for b in builders if b.status == 'done']), len(builders)


class SimpleTable(object):
    """A simple table to print to terminal.

    Parameters
    ----------
    *col_widths : Tuple[int]
        The widths of columns
    """

    col_widths = None

    def __init__(self, *col_widths):
        assert all(isinstance(width, int) for width in col_widths)
        self.col_widths = col_widths

    @property
    def width(self):
        """The number of columns for the table"""
        return sum(self.col_widths)

    def print_hdr(self, *values):
        """Print the table header."""
        assert len(self.col_widths) == len(values), ("The number of values "
                                                     "should match the number "
                                                     "of columns")
        hdr = ""
        for value, width in zip(values, self.col_widths):
            hdr += str(value).ljust(width, " ")
        print(hdr)
        bar = ""
        for value, width in zip(values, self.col_widths):
            value = str(value)
            bar += ("-" * len(value)).ljust(width, " ")
        print(bar)

    def print_row(self, *values):
        """Print a table row."""
        row = ""
        for value, width in zip(values, self.col_widths):
            row += value.ljust(width, " ")
        print(row)


class ProgressTable(SimpleTable):
    """A table for displaying the progress of a build.

    Parameters
    ----------
    environment : :obj:`.builders.Environment`
        The build environment

    Attributes
    ----------
    env_name : str
        The unique name of the build environment
    num_docs : int
        The number of documents in a build tree
    hdrs : Tuple[str]
        The names of columns
    spacing : int
        The number of spaces between columns.
    """

    env_name = None
    num_docs = None
    hdrs = ('Environment', 'Number Docs', 'Done / Total Builds (%)')
    spacing = 2

    def __init__(self, environment):
        self.env_name = environment.name
        root_doc = environment.root_document
        if root_doc is not None:
            docs_list = root_doc.documents_list(only_subdocuments=False,
                                                recursive=True)
            self.num_docs = str(len(docs_list))
        else:
            self.num_docs = ''

        # Get the column width
        col1_width = max(len(self.hdrs[0]), len(self.env_name)) + self.spacing
        col2_width = max(len(self.hdrs[1]), len(self.num_docs)) + self.spacing
        col3_width = len(self.hdrs[2]) + self.spacing

        super().__init__(col1_width, col2_width, col3_width)

    def print_hdr(self):
        super().print_hdr(*self.hdrs)

    def print_row(self, builders):
        """Print a row based on the status of the given builders."""
        done, total = progress_builders(builders)
        percent = (done / total) * 100.
        status_str = "{} / {} ({:.1f}%)".format(done, total, percent)
        rows = [self.env_name, self.num_docs, status_str]
        super().print_row(*rows)
