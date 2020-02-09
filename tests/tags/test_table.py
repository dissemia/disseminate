"""
Test for table tags
"""
from disseminate.tags.table import Table


# html targets

def test_table_csv_with_header_html(csv_tag1):
    """Test the html format for a @table tag with a CSV tag for tag, including
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
    """Test the html format for a @table tag with a CSV tag for tag, including
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