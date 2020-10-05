"""
Test the preamble tags.
"""
from disseminate.tags.preamble import Authors, Titlepage


# tex targets

def test_authors_tag_tex(context_cls):
    """Test the rendering of the authors tag in tex."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          'Justin L Lorieau'),
                         ({'authors': 'Fred Kay, D Smith'},
                          'Fred Kay and D Smith'),
                         ({'authors': ['A', 'B', 'C']},
                          'A, B and C'),
                         ]:
        context = context_cls(**context)

        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)

        tex = tag.tex

        assert key == tex


def test_titlepage_tag_tex(doc):
    """Test the rendering of the authors tag in tex."""
    # setup the tag
    context = doc.context
    context['authors'] = 'Fred Kay, D Smith'
    context['title'] = 'My Title'

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)

    tex = tag.tex

    key = "\n\\maketitle\n\n"
    assert key == tex


# html target

def test_authors_tag_html(context_cls):
    """Test the rendering of the authors tag in html."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          '<span class="authors">Justin L Lorieau</span>'),
                         ({'authors': 'Fred Kay, D Smith'},
                          '<span class="authors">Fred Kay and D Smith</span>'),
                         ({'authors': ['A', 'B', 'C']},
                          '<span class="authors">A, B and C</span>'),
                         ]:
        context = context_cls(**context)
        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)
        tag.html == key


def test_titlepage_tag_html(doc):
    """Test the rendering of the authors tag in html."""
    # setup the tag
    context = doc.context
    context['authors'] = 'Fred Kay, D Smith'
    context['title'] = 'My Title'

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)
    key = ('<div class="title-page">\n'
           '<h1 id="title:test-dm-my-title">'
           '<span class="label">My Title</span></h1>\n'
           '<span class="authors">Fred Kay and D Smith</span>\n'
           '</div>\n')
    assert tag.html == key


def test_authors_tag_xhtml(context_cls, is_xml):
    """Test the rendering of the authors tag in xhtml."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          '<span class="authors">Justin L Lorieau</span>\n'),
                         ({'authors': 'Fred Kay, D Smith'},
                          '<span class="authors">Fred Kay and D Smith'
                          '</span>\n'),
                         ({'authors': ['A', 'B', 'C']},
                          '<span class="authors">A, B and C</span>\n'),
                         ]:
        context = context_cls(**context)
        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)
        assert tag.xhtml == key
        assert is_xml(tag.xhtml)


def test_titlepage_tag_xhtml(doc, is_xml):
    """Test the rendering of the authors tag in xhtml."""
    # setup the tag
    context = doc.context
    context['authors'] = 'Fred Kay, D Smith'
    context['title'] = 'My Title'

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)
    key = ('<div class="title-page">\n'
           '  <h1 id="title:test-dm-my-title">\n'
           '    <span class="label">My Title</span>\n'
           '  </h1>\n'
           '  <span class="authors">Fred Kay and D Smith</span>\n'
           '</div>\n')
    assert tag.xhtml == key
    assert is_xml(tag.xhtml)
