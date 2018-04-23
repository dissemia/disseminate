"""
Test the preamble tags.
"""
from lxml import etree

from disseminate.tags.preamble import Authors, Titlepage


def test_authors_tag_html():
    """Test the rendering of the authors tag in html."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          '<div class="authors">Justin L Lorieau</div>'),
                         ({'authors': 'Fred Kay, D Smith'},
                          '<div class="authors">Fred Kay and D Smith</div>'),
                         ({'authors': ['A', 'B', 'C']},
                          '<div class="authors">A, B and C</div>'),
                        ]:

        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)

        html = etree.tostring(tag.html()).decode('utf-8')

        assert key == html


def test_authors_tag_tex():
    """Test the rendering of the authors tag in tex."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          'Justin L Lorieau'),
                         ({'authors': 'Fred Kay, D Smith'},
                          'Fred Kay and D Smith'),
                         ({'authors': ['A', 'B', 'C']},
                          'A, B and C'),
                        ]:

        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)

        tex = tag.tex()

        assert key == tex


def test_titlepage_tag_html():
    """Test the rendering of the authors tag in html."""
    # setup the tag
    context = {'authors': 'Fred Kay, D Smith',
               'title': 'My Title'}

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)

    html = etree.tostring(tag.html()).decode('utf-8')

    key = ('<div class="title-page">'
           '<h1 class="title">My Title</h1>'
           '<div class="authors">Fred Kay and D Smith</div>'
           '</div>')
    print(html)
    assert key == html


def test_titlepage_tag_tex():
    """Test the rendering of the authors tag in tex."""
    # setup the tag
    context = {'authors': 'Fred Kay, D Smith',
               'title': 'My Title'}

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)

    tex = tag.tex()

    key = "\n\\maketitle\n\n"
    assert key == tex
