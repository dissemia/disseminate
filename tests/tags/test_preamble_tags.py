"""
Test the preamble tags.
"""
from disseminate.tags.preamble import Authors, Titlepage


def test_authors_tag_html(context_cls):
    """Test the rendering of the authors tag in html."""
    # setup the tag
    for context, key in [({'author': 'Justin L Lorieau'},
                          '<div class="authors">Justin L Lorieau</div>'),
                         ({'authors': 'Fred Kay, D Smith'},
                          '<div class="authors">Fred Kay and D Smith</div>'),
                         ({'authors': ['A', 'B', 'C']},
                          '<div class="authors">A, B and C</div>'),
                         ]:
        context = context_cls(**context)
        tag = Authors(name='authors', content='', attributes=tuple(),
                      context=context)
        tag.html == key


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


def test_titlepage_tag_html(doc):
    """Test the rendering of the authors tag in html."""
    # setup the tag
    context = doc.context
    context['authors'] = 'Fred Kay, D Smith'
    context['title'] = 'My Title'

    tag = Titlepage(name='titlepage', content='', attributes=tuple(),
                    context=context)
    key = ('<div class="title-page">\n'
           '  <h1 id="title:test-dm-my-title"><span class="label"/>My Title</h1>\n'
           '  <div class="authors">Fred Kay and D Smith</div>\n'
           '</div>\n')
    assert tag.html == key


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
