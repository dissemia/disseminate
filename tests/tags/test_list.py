"""
Test the @list tag.
"""
from disseminate.tags.list import (parse_list, parse_string_list,
                                   clean_string_list, ListItem, List,
                                   OrderedList)


def test_parse_string_list():
    """Test the parse_string_list and clean_string_list functions."""

    # 1. A non-nested list
    t1 = """
    - One
    - Two
    - Three
    """
    l1 = parse_string_list(t1)
    c1 = clean_string_list(l1)

    assert l1 == [(4, 'One'), (4, 'Two'), (4, 'Three')]
    assert c1 == [(4, 'One'), (4, 'Two'), (4, 'Three')]

    # 2. A nested list
    t2 = """
    - One
      - Two with
        multiple lines
    - Three
    """
    l2 = parse_string_list(t2)
    c2 = clean_string_list(l2)
    assert (l2 ==
            [(4, 'One'), (6, 'Two with\n        multiple lines'),
             (4, 'Three')])
    assert (c2 ==
            [(4, 'One'), (6, 'Two with multiple lines'),
             (4, 'Three')])

    # 3. An empty string
    t3 = "This is a simple string"
    l3 = parse_string_list(t3)
    c3 = clean_string_list(l3)
    assert l3 == []
    assert c3 == []


def test_parse_list_strings(doc):
    """Test the parse_list_strings function"""

    # 1. Test a simple list string
    t1 = """
    - One
    - Two
    - Three
    """
    returned_list = parse_list(content=t1, context=doc.context)

    assert len(returned_list) == 3

    assert isinstance(returned_list[0], ListItem)
    assert returned_list[0].name == "listitem"
    assert returned_list[0].content == "One"
    assert returned_list[0].attributes['level'] == 4

    assert isinstance(returned_list[1], ListItem)
    assert returned_list[1].name == "listitem"
    assert returned_list[1].content == "Two"
    assert returned_list[1].attributes['level'] == 4

    assert isinstance(returned_list[2], ListItem)
    assert returned_list[2].name == "listitem"
    assert returned_list[2].content == "Three"
    assert returned_list[2].attributes['level'] == 4

    # 2. Test a nested list
    t2 = """
    - One
      - Two with
        multiple lines
    - Three
    """
    returned_list = parse_list(content=t2, context=doc.context)

    assert len(returned_list) == 3

    assert isinstance(returned_list[0], ListItem)
    assert returned_list[0].name == "listitem"
    assert returned_list[0].content == "One"
    assert returned_list[0].attributes['level'] == 4

    assert isinstance(returned_list[1], ListItem)
    assert returned_list[1].name == "listitem"
    assert returned_list[1].content == "Two with multiple lines"
    assert returned_list[1].attributes['level'] == 6

    assert isinstance(returned_list[2], ListItem)
    assert returned_list[2].name == "listitem"
    assert returned_list[2].content == "Three"
    assert returned_list[2].attributes['level'] == 4

    # 3. Test a list with tags
    t3 = """
    - One
      - Two with
        @b{multiple} lines
    - Three
    """
    returned_list = parse_list(content=t3, context=doc.context)

    assert len(returned_list) == 3

    assert isinstance(returned_list[0], ListItem)
    assert returned_list[0].name == "listitem"
    assert returned_list[0].content == "One"
    assert returned_list[0].attributes['level'] == 4

    assert isinstance(returned_list[1], ListItem)
    assert returned_list[1].name == "listitem"
    assert returned_list[1].content[0] == "Two with "
    assert returned_list[1].content[1].name == "b"
    assert returned_list[1].content[1].content == "multiple"
    assert returned_list[1].content[2] == " lines"
    assert returned_list[1].attributes['level'] == 6

    assert isinstance(returned_list[2], ListItem)
    assert returned_list[2].name == "listitem"
    assert returned_list[2].content == "Three"
    assert returned_list[2].attributes['level'] == 4


# tex targets

def test_list_tex(doc):
    """Test the @list tag with the tex format"""

    # 1. Test a simple (unordered) nested list
    src = """
    - One
      - Two with
        multiple lines
    - Three
    """
    tex_list = List(name='list', content=src, attributes='',
                    context=doc.context)
    assert tex_list.tex == ('\n'
                            '\\begin{easylist}[itemize]\n'
                            '§ One\n'
                            '§§ Two with multiple lines\n'
                            '§ Three\n'
                            '\\end{easylist}\n')

    # 2. Test a simple (ordered) nested list
    src = """
       - One
         - Two with
           multiple lines
       - Three
       """
    tex_list = OrderedList(name='list', content=src, attributes='',
                           context=doc.context)

    assert tex_list.tex == ('\n'
                            '\\begin{easylist}[enumerate]\n'
                            '§ One\n'
                            '§§ Two with multiple lines\n'
                            '§ Three\n'
                            '\\end{easylist}\n')

    # 3. Test a list with tags
    src = """
        - One
          - Two with
            @b{multiple} lines
        - Three
        """
    tex_list = List(name='list', content=src, attributes='',
                    context=doc.context)

    assert tex_list.tex == ('\n'
                            '\\begin{easylist}[itemize]\n'
                            '§ One\n'
                            '§§ Two with \\textbf{multiple} lines\n'
                            '§ Three\n'
                            '\\end{easylist}\n')


# html targets

def test_list_html(doc):
    """Test the @list tag with the html format"""

    # 1. Test a simple (unordered) nested list
    src = """
    - One
      - Two with
        multiple lines
    - Three
    """
    html_list = List(name='list', content=src, attributes='',
                     context=doc.context)
    assert html_list.html == ('<ul>\n'
                              '<li>One</li>\n'
                              '<ul>'
                              '<li>Two with multiple lines</li>'
                              '</ul>\n'
                              '<li>Three</li>\n'
                              '</ul>\n')

    # 2. Test a simple (ordered) nested list
    src = """
    - One
      - Two with
        multiple lines
    - Three
    """
    html_list = OrderedList(name='list', content=src, attributes='',
                            context=doc.context)
    assert html_list.html == ('<ol>\n'
                              '<li>One</li>\n'
                              '<ol>'
                              '<li>Two with multiple lines</li>'
                              '</ol>\n'
                              '<li>Three</li>\n'
                              '</ol>\n')

    # 3. Test a list with tags
    src = """
    - One
      - Two with
        @b{multiple} lines
    - Three
    """
    html_list = List(name='list', content=src, attributes='',
                     context=doc.context)
    assert html_list.html == ('<ul>\n'
                              '<li>One</li>\n'
                              '<ul>'
                              '<li>'
                              'Two with <strong>multiple</strong> lines'
                              '</li>'
                              '</ul>\n'
                              '<li>Three</li>\n'
                              '</ul>\n')


# xhtml targets

def test_list_xhtml(doc, is_xml):
    """Test the @list tag with the xhtml format"""

    # 1. Test a simple (unordered) nested list
    src = """
        - One
          - Two with
            multiple lines
        - Three
        """
    xhtml_list = List(name='list', content=src, attributes='',
                      context=doc.context)
    assert xhtml_list.xhtml == ('<ul>\n'
                                '  <li>One</li>\n'
                                '  <ul>\n'
                                '    <li>Two with multiple lines</li>\n'
                                '  </ul>\n'
                                '  <li>Three</li>\n'
                                '</ul>\n')
    assert is_xml(xhtml_list.xhtml)

    # 2. Test a simple (ordered) nested list
    src = """
        - One
          - Two with
            multiple lines
        - Three
        """
    xhtml_list = OrderedList(name='list', content=src, attributes='',
                             context=doc.context)
    assert xhtml_list.xhtml == ('<ol>\n'
                                '  <li>One</li>\n'
                                '  <ol>\n'
                                '    <li>Two with multiple lines</li>\n'
                                '  </ol>\n'
                                '  <li>Three</li>\n'
                                '</ol>\n')
    assert is_xml(xhtml_list.xhtml)

    # 3. Test a list with tags
    src = """
        - One
          - Two with
            @b{multiple} lines
        - Three
        """
    xhtml_list = List(name='list', content=src, attributes='',
                      context=doc.context)
    assert xhtml_list.xhtml == ('<ul>\n'
                                '  <li>One</li>\n'
                                '  <ul>\n'
                                '    <li>'
                                'Two with <strong>multiple</strong> lines'
                                '</li>\n'
                                '  </ul>\n'
                                '  <li>Three</li>\n'
                                '</ul>\n')
    assert is_xml(xhtml_list.xhtml)
