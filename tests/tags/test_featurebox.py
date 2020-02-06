"""Test featurebox tags."""
from disseminate.tags import Tag
from disseminate.settings import default_context


# html targets

def test_tag_featurebox(context_cls):
    """Test the featurebox tags into html."""

    context = context_cls(parent_context=default_context)

    # Generate a tag for each and compare the generated html to the answer key
    src = """This is a paragraph.
    
    @featurebox{This is my featurebox.
    
    It has 2 paragraphs.}
    
    This is another paragraph.
    """
    html = ('<span class="body">'
            '<p>This is a paragraph.</p>\n'
            '<div class="featurebox">\n'
            '<p>This is my featurebox.</p>\n'
            '<p>It has 2 paragraphs.</p>\n'
            '</div>\n'
            '<p>This is another paragraph.\n    '
            '</p></span>\n')

    body = Tag(name='body', content=src, attributes='', context=context)
    assert body.html == html
