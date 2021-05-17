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


def test_csv_parsing_with_formatted_text(csv_tag3):
    """Test the @csv (DelimData) tag for parsing csv data with formatted text
    in disseminate format"""

    # Check the data. The headers are just simple, unparsed strings
    assert csv_tag3.headers == ['header @i{1}', 'header @i{2}', 'header @i{3}']

    # The cells are just simple, unparsed strings
    rows = list(csv_tag3.rows)
    assert len(rows) == 3
    assert rows[0] == (0, "My @b{1-1} column", "My @b{1-2} column",
                       "My @b{1-3} column")
    assert rows[1] == (1, "My @b{2-1} column", "My @b{2-2} column",
                       "My @b{2-3} column")
    assert rows[2] == (2, "My @b{3-1} column", "My @b{3-2} column",
                       "My @b{3-3} column")


# tex targets

def test_csv_with_header_tex(csv_tag1):
    """Test the @csv (DelimData) tag with header data in tex format"""

    # Check the tex
    tex = ('\\toprule\n'
           'header 1 & header 2 & header 3 \\\\\n'
           '\\midrule\n'
           '1-1 & 1-2 & 1-3 \\\\\n'
           '2-1 & 2-2 & 2-3 \\\\\n'
           '3-1 & 3-2 & 3-3 \\\\\n'
           '\\bottomrule')
    assert csv_tag1.tex_table() == tex


def test_csv_without_header_tex(csv_tag2):
    """Test the @csv (DelimData) tag without header data in tex format"""

    # Check the tex
    tex = ('\\toprule\n'
           '1 & 2 & 3 \\\\\n'
           '4 & 5 & 6 \\\\\n'
           '7 & 8 & 9 \\\\\n'
           '\\bottomrule')
    assert csv_tag2.tex_table() == tex


def test_csv_parsing_with_formatted_text_tex(csv_tag3):
    """Test the @csv (DelimData) tag with formated text, converting in tex
    format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    tex = ('\\toprule\n'
           'header \\textit{1} & '
           'header \\textit{2} & '
           'header \\textit{3} \\\\\n'
           '\\midrule\n'
           'My \\textbf{1-1} column & '
           'My \\textbf{1-2} column & '
           'My \\textbf{1-3} column \\\\\n'
           'My \\textbf{2-1} column & '
           'My \\textbf{2-2} column & '
           'My \\textbf{2-3} column \\\\\n'
           'My \\textbf{3-1} column & '
           'My \\textbf{3-2} column & '
           'My \\textbf{3-3} column \\\\\n'
           '\\bottomrule')
    assert tex == csv_tag3.tex_table()


def test_ampersand_text_tex(csv_tag4):
    """Test the @csv (DelimData) tag including text with ampersands, converting
    in tex format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    tex = ('\\toprule\n'
           'header 1 & header 2 & header 3 \\\\\n'
           '\\midrule\n'
           '1 & 2\\&3 & 4 \\\\\n'
           '5 & 6\\&7 & 8 \\\\\n'
           '9 & 10\\&11 & 12 \\\\\n'
           '\\bottomrule')
    assert tex == csv_tag4.tex_table()


# html targets

def test_csv_with_header_html(csv_tag1):
    """Test the @csv (DelimData) tag with header data in html format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    html = csv_tag1.html_table()
    assert len(html) == 2  # 1 header row, 1 body row


def test_csv_without_header_html(csv_tag2):
    """Test the @csv (DelimData) tag with header data in html format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    html = csv_tag2.html_table()
    assert len(html) == 1  # 1 body row


def test_csv_parsing_with_formatted_text_html(csv_tag3):
    """Test the @csv (DelimData) tag with formated text, converting in html
    format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    html = csv_tag3.html_table()
    assert len(html) == 2  # 1 header row, 1 body row
