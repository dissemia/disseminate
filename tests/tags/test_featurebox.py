"""Test featurebox tags."""
from disseminate.tags import Tag
from disseminate.settings import default_context

src1 = """This is a paragraph.
    
    @featurebox{This is my featurebox.
    
    It has 2 paragraphs.}
    
    This is another paragraph.
    """


# tex target

def test_tag_featurebox_tex(context_cls):
    """Test the featurebox tag in tex"""
    context = context_cls(parent_context=default_context)

    # Generate a tag for each and compare the generated html to the answer key
    tex = ('\nThis is a paragraph.\n\n'
           '\\begin{featurebox}\n'
           'This is my featurebox.\n\n'
           'It has 2 paragraphs.\n'
           '\\end{featurebox}\n\n'
           'This is another paragraph.\n    \n')

    body = Tag(name='body', content=src1, attributes='', context=context)
    assert body.tex == tex


# html target

def test_tag_featurebox_html(context_cls):
    """Test the featurebox tags in html."""

    context = context_cls(parent_context=default_context)

    # Generate a tag for each and compare the generated html to the answer key
    html = ('<span class="body">'
            '<p>This is a paragraph.</p>\n'
            '<div class="featurebox">\n'
            '<p>This is my featurebox.</p>\n'
            '<p>It has 2 paragraphs.</p>\n'
            '</div>\n'
            '<p>This is another paragraph.\n    '
            '</p></span>\n')

    body = Tag(name='body', content=src1, attributes='', context=context)
    assert body.html == html


# xhtml target

def test_tag_featurebox_xhtml(context_cls, is_xml):
    """Test the featurebox tags in xhtml."""

    context = context_cls(parent_context=default_context)

    # Generate a tag for each and compare the generated html to the answer key
    xhtml = ('<span class="body">\n'
             '  <p>This is a paragraph.</p>\n'
             '  <div class="featurebox">\n'
             '    <p>This is my featurebox.</p>\n'
             '    <p>It has 2 paragraphs.</p>\n'
             '  </div>\n'
             '  <p>This is another paragraph.\n'
             '    </p>\n'
             '</span>\n')

    body = Tag(name='body', content=src1, attributes='', context=context)
    assert body.xhtml == xhtml
    assert is_xml(body.xhtml)
