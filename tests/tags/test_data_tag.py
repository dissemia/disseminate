"""
Test data types.
"""


def test_csv_parsing_with_header(csv_tag1):
    """Test the @csv (DelimData) tag for parsing csv data with headers"""

    # Check the data
    assert csv_tag1.headers == ['header 1', 'header 2', 'header 3']

    rows = list(csv_tag1.rows)
    assert len(rows) == 3
    assert rows[0] == (0, "1-1", "1-2", "1-3")
    assert rows[1] == (1, "2-1", "2-2", "2-3")
    assert rows[2] == (2, "3-1", "3-2", "3-3")


def test_csv_parsing_without_header(csv_tag2):
    """Test the @csv (DelimData) tag for parsing csv data without a header"""

    # Check the data
    assert csv_tag2.headers is None

    rows = list(csv_tag2.rows)
    assert len(rows) == 3
    assert rows[0] == (0, 1, 2, 3)
    assert rows[1] == (1, 4, 5, 6)
    assert rows[2] == (2, 7, 8, 9)


def test_csv_with_header_html(csv_tag1):
    """Test the @csv (DelimData) tag with header data in html format"""

    # Check the html
    html = csv_tag1.html_table()
    assert len(html) == 2  # 1 header row, 3 data rows

