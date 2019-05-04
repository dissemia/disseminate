"""
Tests for the figure tags.
"""
from disseminate import Document
from disseminate.tags import Tag
from disseminate.utils.tests import strip_leading_space


def test_marginfig_parsing(context_cls):
    """Test the parsing of marginfig tags."""

    context = context_cls()

    test1 = "@marginfig{fig1}"
    root = Tag(name='root', content=test1, attributes='', context=context)
    marginfig = root.content
    assert marginfig.name == 'marginfig'
    assert marginfig.content == 'fig1'

    test2 = "@marginfig{{fig1}}"
    root = Tag(name='root', content=test2, attributes='', context=context)
    marginfig = root.content
    assert marginfig.name == 'marginfig'
    assert marginfig.content == '{fig1}'


def test_figure_caption_no_id(doc, attributes_cls):
    """Tests the parsing of captions in figure tags when no id is specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption.\nIt has multiple lines}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    assert fig.name == 'marginfig'
    assert fig.attributes == dict()

    # 1. Get the caption, first with a basic figure label
    caption = fig.content

    assert caption.label_id == 'caption-409240e72c'  # auto-generated
    assert caption.name == 'caption'
    assert caption.attributes == attributes_cls(**{'id': 'caption-409240e72c',
                                                   'class': 'caption'})
    assert caption.default == ('My Fig. 1. This is my caption.\n'
                               'It has multiple lines')


def test_figure_caption_with_id(doc):
    """Tests the parsing of captions in figure tags when an id is specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    for src in ("@marginfig[id=fig-1]{@caption{This is my caption}}",
                "@marginfig{@caption[id=fig-1]{This is my caption}}"):

        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content
        caption = fig.content

        assert fig.name == 'marginfig'
        assert caption.name == 'caption'
        assert caption.label_id == 'fig-1'

        # Check the formatted caption. In order to use the 'caption_figure'
        # label format, a label must have been created in the label_manager
        assert caption.default == 'My Fig. 1. This is my caption'


# html tests

def test_figure_caption_no_id_html(doc):
    """Tests the html generation of captions in figure tags when no id is
    specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    marginfig = root.content

    key = ('<span class="marginfig">\n'
           '  <span class="caption" id="caption-92042fbb8b">'
           '<span class="label">My Fig. 1. </span>This is my caption</span>\n'
           '</span>\n')
    assert marginfig.html == key


def test_figure_caption_with_id_html(doc):
    """Tests the html generation of captions in figure tags when an id is
    specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")

    key = ('<span class="marginfig">\n'
           '  <span class="caption" id="fig-1">'
           '<span class="label">My Fig. 1. </span>This is my caption</span>\n'
           '</span>\n')

    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content

        assert fig.html == key


# tex tests

def test_figure_caption_no_id_tex(doc):
    """Tests the tex generation of captions in figure tags when no id is
    specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    key = ('\n'
           '\\begin{marginfigure}\n'
           '\\caption{My Fig. 1. This is my caption} '
           '\\label{caption-92042fbb8b}\n'
           '\\end{marginfigure}\n')
    assert fig.tex == key


def test_figure_caption_with_id_tex(doc):
    """Tests the tex generation of captions in figure tags when an id is
    specified."""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content

        assert fig.tex == ('\n'
                           '\\begin{marginfigure}\n'
                           '\\caption{My Fig. 1. This is my caption} '
                           '\\label{fig-1}\n'
                           '\\end{marginfigure}\n')
