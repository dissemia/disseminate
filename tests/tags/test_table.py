"""
Test for table tags
"""
from disseminate.tags.table import Table, MarginTable, FullTable


# html targets

def test_table_csv_with_header_html(csv_tag1):
    """Test the html format for a @table tag with a CSV tag for data, including
    header."""
    context = csv_tag1.context
    table = Table(name='table', content=csv_tag1, attributes='',
                  context=context)

    html = ('<table>\n'
            '<thead><tr>\n'
            '<th>header 1</th>\n'
            '<th>header 2</th>\n'
            '<th>header 3</th>\n'
            '</tr></thead>\n'
            '<tbody>\n'
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
            '</tbody>\n'
            '</table>\n')
    assert table.html == html


def test_table_csv_without_header_html(csv_tag2):
    """Test the html format for a @table tag with a CSV tag for data, including
    header."""
    context = csv_tag2.context
    table = Table(name='table', content=csv_tag2, attributes='',
                  context=context)

    html = ('<table><tbody>\n'
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
            '</tbody></table>\n')
    assert table.html == html


def test_table_csv_with_formatted_text_html(csv_tag3):
    """Test the html format for a @table tag with a CSV tag for data, including
    formatted text cells."""
    context = csv_tag3.context
    table = Table(name='table', content=csv_tag3, attributes='',
                  context=context)

    html = ('<table>\n'
            '<thead><tr>\n'
            '<th>header <i>1</i>\n'
            '</th>\n'
            '<th>header <i>2</i>\n'
            '</th>\n'
            '<th>header <i>3</i>\n'
            '</th>\n'
            '</tr></thead>\n'
            '<tbody>\n'
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
            '</tbody>\n'
            '</table>\n')
    assert table.html == html


def test_margintable_csv_with_header_html(csv_tag1):
    """Test the html format for a @margintable tag with a CSV tag for tag,
    including header."""
    context = csv_tag1.context
    table = MarginTable(name='margintable', content=csv_tag1, attributes='',
                        context=context)

    html = ('<table class="margintbl">\n'
            '<thead><tr>\n'
            '<th>header 1</th>\n'
            '<th>header 2</th>\n'
            '<th>header 3</th>\n'
            '</tr></thead>\n'
            '<tbody>\n'
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
            '</tbody>\n'
            '</table>\n')
    assert table.html == html


def test_margintable_csv_without_header_html(csv_tag2):
    """Test the html format for a @margintable tag with a CSV tag for tag,
    including header."""
    context = csv_tag2.context
    table = MarginTable(name='margintable', content=csv_tag2, attributes='',
                        context=context)

    html = ('<table class="margintbl"><tbody>\n'
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
            '</tbody></table>\n')
    assert table.html == html


def test_fulltable_csv_with_header_html(csv_tag1):
    """Test the html format for a @fulltable tag with a CSV tag for tag,
    including header."""
    context = csv_tag1.context
    table = FullTable(name='fulltable', content=csv_tag1, attributes='',
                      context=context)

    html = ('<table class="fulltable">\n'
            '<thead><tr>\n'
            '<th>header 1</th>\n'
            '<th>header 2</th>\n'
            '<th>header 3</th>\n'
            '</tr></thead>\n'
            '<tbody>\n'
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
            '</tbody>\n'
            '</table>\n')
    assert table.html == html


def test_fulltable_csv_without_header_html(csv_tag2):
    """Test the html format for a @mfulltable tag with a CSV tag for tag,
    including header."""
    context = csv_tag2.context
    table = FullTable(name='fulltable', content=csv_tag2, attributes='',
                      context=context)

    html = ('<table class="fulltable"><tbody>\n'
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
            '</tbody></table>\n')
    assert table.html == html


# tex targets

def test_margintable_csv_with_header_tex(csv_tag1):
    """Test the tex format for a @margintable tag with a CSV tag for data,
    including header."""
    context = csv_tag1.context
    table = MarginTable(name='table', content=csv_tag1, attributes='',
                        context=context)

    tex = ('\n\\begin{margintable}\n'
           '\\begin{tabular}{lll}\n'
           '\\toprule\n'
           'header 1 && header 2 && header 3\n'
           '\\midrule\n'
           '1-1 && 1-2 && 1-3 \\\\\n'
           '2-1 && 2-2 && 2-3 \\\\\n'
           '3-1 && 3-2 && 3-3\n'
           '\\bottomrule\n'
           '\\end{tabular}\n'
           '\\end{margintable}\n')
    assert table.tex == tex


def test_fulltable_csv_with_header_tex(csv_tag1):
    """Test the tex format for a @fulltable tag with a CSV tag for data,
    including header."""
    context = csv_tag1.context
    table = FullTable(name='table', content=csv_tag1, attributes='',
                      context=context)

    tex = ('\n\\begin{table*}\n'
           '\\begin{tabular}{lll}\n'
           '\\toprule\n'
           'header 1 && header 2 && header 3\n'
           '\\midrule\n'
           '1-1 && 1-2 && 1-3 \\\\\n'
           '2-1 && 2-2 && 2-3 \\\\\n'
           '3-1 && 3-2 && 3-3\n'
           '\\bottomrule\n'
           '\\end{tabular}\n'
           '\\end{table*}\n')
    assert table.tex == tex


def test_table_csv_with_header_tex(csv_tag1):
    """Test the tex format for a @table tag with a CSV tag for data, including
    header."""
    context = csv_tag1.context
    table = Table(name='table', content=csv_tag1, attributes='',
                  context=context)

    tex = ('\n\\begin{table}\n'
           '\\begin{tabular}{lll}\n'
           '\\toprule\n'
           'header 1 && header 2 && header 3\n'
           '\\midrule\n'
           '1-1 && 1-2 && 1-3 \\\\\n'
           '2-1 && 2-2 && 2-3 \\\\\n'
           '3-1 && 3-2 && 3-3\n'
           '\\bottomrule\n'
           '\\end{tabular}\n'
           '\\end{table}\n')
    assert table.tex == tex


def test_table_csv_without_header_tex(csv_tag2):
    """Test the tex format for a @table tag with a CSV tag for data, without
    header."""
    context = csv_tag2.context
    table = Table(name='table', content=csv_tag2, attributes='',
                  context=context)

    tex = ('\n\\begin{table}\n'
           '\\begin{tabular}{lll}\n'
           '\\toprule\n1 && 2 && 3 \\\\\n'
           '4 && 5 && 6 \\\\\n'
           '7 && 8 && 9\n'
           '\\bottomrule\n'
           '\\end{tabular}\n'
           '\\end{table}\n')
    assert table.tex == tex


def test_table_csv_with_formatted_text_tex(csv_tag3):
    """Test the html format for a @table tag with a CSV tag for data, including
    formatted text cells."""
    context = csv_tag3.context
    table = Table(name='table', content=csv_tag3, attributes='',
                  context=context)

    tex = ('\n\\begin{table}\n'
           '\\begin{tabular}{lll}\n'
           '\\toprule\n'
           'header \\textit{1} && header \\textit{2} && header \\textit{3}\n'
           '\\midrule\n'
           'My \\textbf{1-1} column && My \\textbf{1-2} column && My \\'
           'textbf{1-3} column \\\\\n'
           'My \\textbf{2-1} column && My \\textbf{2-2} column && My \\'
           'textbf{2-3} column \\\\\n'
           'My \\textbf{3-1} column && My \\textbf{3-2} column && My \\'
           'textbf{3-3} column\n'
           '\\bottomrule\n'
           '\\end{tabular}\n'
           '\\end{table}\n')
    assert table.tex == tex
