"""
Test data types.
"""


def test_csv_parsing_with_header(csv_tag1):
    """Test the @csv (DelimData) tag for parsing csv data with headers"""

    # Check the data
    assert csv_tag1.headers == ('header 1', 'header 2', 'header 3')
    assert csv_tag1.data == {'header 1': ('1-1', '2-1', '3-1'),
                             'header 2': ('1-2', '2-2', '3-2'),
                             'header 3': ('1-3', '2-3', '3-3')}

    # Check the rows
    rows = list(csv_tag1.rows)
    assert len(rows) == 3
    assert rows[0] == ("1-1", "2-1", "3-1")
    assert rows[1] == ("1-2", "2-2", "3-2")
    assert rows[2] == ("1-3", "2-3", "3-3")

    # Check the transposed rows
    rows_T = list(csv_tag1.rows_transpose)
    assert len(rows_T) == 3
    assert rows_T[0] == ('1-1', '1-2', '1-3')
    assert rows_T[1] == ("2-1", "2-2", "2-3")
    assert rows_T[2] == ("3-1", "3-2", "3-3")


def test_csv_parsing_without_header(csv_tag2):
    """Test the @csv (DelimData) tag for parsing csv data without a header"""

    # Check the data
    assert csv_tag2.headers == (0, 1, 2)
    assert csv_tag2.data == {0: ('1', '4', '7'),
                             1: ('2', '5', '8'),
                             2: ('3', '6', '9')}

    # Check the rows
    rows = list(csv_tag2.rows)
    assert len(rows) == 3
    assert rows[0] == ('1', '4', '7')
    assert rows[1] == ('2', '5', '8')
    assert rows[2] == ('3', '6', '9')

    # Check the transposed rows
    rows_T = list(csv_tag2.rows_transpose)
    assert len(rows_T) == 3
    assert rows_T[0] == ('1', '2', '3')
    assert rows_T[1] == ('4', '5', '6')
    assert rows_T[2] == ('7', '8', '9')


def test_csv_parsing_with_formatted_text(csv_tag3):
    """Test the @csv (DelimData) tag for parsing csv data with formatted text
    in disseminate format"""

    # Check the data. The headers are just simple, unparsed strings
    assert csv_tag3.headers == ('header @i{1}', 'header @i{2}', 'header @i{3}')

    # The cells are just simple, unparsed strings
    rows_T = list(csv_tag3.rows_transpose)
    assert len(rows_T) == 3
    assert rows_T[0] == ("My @b{1-1} column", "My @b{1-2} column",
                         "My @b{1-3} column")
    assert rows_T[1] == ("My @b{2-1} column", "My @b{2-2} column",
                         "My @b{2-3} column")
    assert rows_T[2] == ("My @b{3-1} column", "My @b{3-2} column",
                         "My @b{3-3} column")


def test_csv_parsing_with_filepath(csv_tag5):
    """Test the @csv (DelimData) tag for parsing csv data from a filepath"""

    # Check the data. The headers are just simple, unparsed strings
    assert csv_tag5.headers == ('Header 1', 'Header 2', 'Header 3', 'Header 4')

    # The cells are just simple, unparsed strings
    rows_T = list(csv_tag5.rows_transpose)
    assert len(rows_T) == 3
    assert rows_T[0] == ('Onion', 'Carrots', 'Pickles', 'Toast')
    assert rows_T[1] == ('CPU', 'RAM', 'Keyboard', 'Mouse')
    assert rows_T[2] == ('Nuclei', 'Operator', 'Hamiltonian', 'Planck')


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

    # Check the number of entries
    assert len(html) == 2  # 1 header row, 1 body row

    # Check the entries
    assert html[0] == ('<thead><tr>\n'
                       '<th>header 1</th>\n'
                       '<th>header 2</th>\n'
                       '<th>header 3</th>\n'
                       '</tr></thead>\n')
    assert html[1] == ('<tbody>\n'
                       '<tr>\n'
                       '<td>1-1</td>\n'
                       '<td>1-2</td>\n'
                       '<td>1-3</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>2-1</td>\n'
                       '<td>2-2</td>\n'
                       '<td>2-3</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>3-1</td>\n'
                       '<td>3-2</td>\n'
                       '<td>3-3</td>\n'
                       '</tr>\n'
                       '</tbody>\n')


def test_csv_without_header_html(csv_tag2):
    """Test the @csv (DelimData) tag with header data in html format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    html = csv_tag2.html_table()

    # Check enties
    assert len(html) == 1  # 1 body row
    assert html[0] == ('<tbody>\n'
                       '<tr>\n'
                       '<td>1</td>\n'
                       '<td>2</td>\n'
                       '<td>3</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>4</td>\n'
                       '<td>5</td>\n'
                       '<td>6</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>7</td>\n'
                       '<td>8</td>\n'
                       '<td>9</td>\n'
                       '</tr>\n'
                       '</tbody>\n')


def test_csv_parsing_with_formatted_text_html(csv_tag3):
    """Test the @csv (DelimData) tag with formated text, converting in html
    format"""

    # Check the html. These are lxml elements that are rendered into an actual
    # table by the @table tag
    html = csv_tag3.html_table()

    # Check entries
    assert len(html) == 2  # 1 header row, 1 body row
    assert html[0] == ('<thead><tr>\n'
                       '<th>header <i>1</i>\n'
                       '</th>\n'
                       '<th>header <i>2</i>\n'
                       '</th>\n'
                       '<th>header <i>3</i>\n'
                       '</th>\n'
                       '</tr></thead>\n')
    assert html[1] == ('<tbody>\n'
                       '<tr>\n'
                       '<td>My <strong>1-1</strong> column</td>\n'
                       '<td>My <strong>1-2</strong> column</td>\n'
                       '<td>My <strong>1-3</strong> column</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>My <strong>2-1</strong> column</td>\n'
                       '<td>My <strong>2-2</strong> column</td>\n'
                       '<td>My <strong>2-3</strong> column</td>\n'
                       '</tr>\n'
                       '<tr>\n'
                       '<td>My <strong>3-1</strong> column</td>\n'
                       '<td>My <strong>3-2</strong> column</td>\n'
                       '<td>My <strong>3-3</strong> column</td>\n'
                       '</tr>\n'
                       '</tbody>\n')
