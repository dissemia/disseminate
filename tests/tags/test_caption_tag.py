"""
Test the caption and reg tags.
"""
from disseminate.tags import Tag


def test_naked_caption(context_cls):
    """Tests the parsing of naked captions (i.e. those not nested in a figure
    or table).

    Naked captions will not create a label.
    """

    context = context_cls()

    # Generate the markup without an id
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.name == 'caption'
    assert caption.attributes['class'] == 'caption'
    assert caption.content == 'This is my caption'


# Test tex targets

def test_caption_tex(context_cls):
    """Test the formatting of naked captions for tex targets.

    Naked captions will not create a label.
    """

    context = context_cls()

    # 1. Test a basic caption.
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.tex == '\\caption{This is my caption}'

    # 2. Test a caption with nested tags
    src = "@caption{This is @b{my} caption}"

    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.tex == '\\caption{This is \\textbf{my} caption}'


# Test html target

def test_caption_html(context_cls):
    """Test the formatting of nakedcaptions for html targets.

    Naked captions will not create a label.
    """

    context = context_cls()

    # 1. Test a basic caption.
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.html == ('<span class="caption">This is my caption'
                            '</span>\n')

    # 2. Test a caption with nested tags
    src = "@caption{This is @b{my} caption}"

    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.html == ('<span class="caption">'
                            'This is <strong>my</strong> caption</span>\n')


# Test xhtml target

def test_caption_xhtml(context, is_xml):
    """Test the formatting of nakedcaptions for html targets.

    Naked captions will not create a label.
    """
    # 1. Test a basic caption
    src = "@caption{This is @b{my} caption}"

    root = Tag(name='root', content=src, attributes='', context=context)
    caption = root.content

    assert caption.xhtml == ('<span class="caption">'
                             'This is <strong>my</strong> caption</span>\n')
    assert is_xml(caption.xhtml)

    # 2. Test an empty caption
    root = Tag(name='root', content='@caption', attributes='', context=context)
    caption = root.content

    assert caption.xhtml == ('<span class="caption"/>\n')
    assert is_xml(caption.xhtml)
