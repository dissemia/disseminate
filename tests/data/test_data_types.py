"""
Test data types.
"""
import pathlib

from disseminate.data import DelimData


def test_csvdata(context_cls):
    """Test the CsvData type."""
    paths = [pathlib.Path('.')]
    context = context_cls(paths=paths)

    # 1. Test the parsing of text strings
    text1 = ("header 1, header 2, header 3\n"
             "1-1, 1-2, 1-3\n"
             "2-1, 2-2, 2-3\n"
             "3-1, 3-2, 3-3\n")

    data = DelimData(text1, context)

    # Check the data
    assert data.headers == ['header 1', 'header 2', 'header 3']

    rows = list(data.rows)
    assert len(rows) == 3
    assert rows[0] == (0, "1-1", "1-2", "1-3")
    assert rows[1] == (1, "2-1", "2-2", "2-3")
    assert rows[2] == (2, "3-1", "3-2", "3-3")
