"""
Tests for the figure tags.
"""
import pytest

from disseminate.tags import Tag
from disseminate.formats.tex import TexFormatError


# Tag tests

def test_marginfig_parsing(context_cls):
    """Test the parsing of @marginfig tags."""

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


# Caption tests

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
    label_man = doc.context['label_manager']

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    for src in ("@marginfig[id=fig-1]{@caption{This is my caption}}",
                "@marginfig{@caption[id=fig-1]{This is my caption}}"):

        # Reset label manager to prevent duplicate labels
        label_man.reset()

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


# tex tests

def test_marginfig_caption_no_id_tex(doc):
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


def test_marginfig_caption_with_id_tex(doc):
    """Tests the tex generation of captions in figure tags when an id is
    specified."""
    label_man = doc.context['label_manager']

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Reset the labels to avoid creating a duplicate label
        label_man.reset()

        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content

        assert fig.tex == ('\n'
                           '\\begin{marginfigure}\n'
                           '\\caption{My Fig. 1. This is my caption} '
                           '\\label{fig-1}\n'
                           '\\end{marginfigure}\n')


def test_figure_tex(doc):
    """Test the @figure tag tex format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    key = ('\n'
           '\\begin{figure}\n'
           '\\caption{My Fig. 1. This is my caption} '
           '\\label{caption-92042fbb8b}\n'
           '\\end{figure}\n')
    assert fig.tex == key


def test_fullfigure_tex(doc):
    """Test the @fullfigure tag tex format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fullfigure{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    key = ('\n'
           '\\begin{figure*}\n'
           '\\caption{My Fig. 1. This is my caption} '
           '\\label{caption-92042fbb8b}\n'
           '\\end{figure*}\n')
    assert fig.tex == key


def test_panel_tex(doc):
    """Test the @panel tag tex format"""

    # 1. Generate a panel tag without a width. This will fail because the
    #    width is required
    src = "@panel{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    with pytest.raises(TexFormatError):
        assert panel.tex

    # 2. Generate a panel tag a width
    src = "@panel[width='30%']{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    key = ('\\begin{panel}{0.3\\textwidth}\n'
           'This is my panel\n'
           '\\end{panel}')
    assert panel.tex == key


# html tests

def test_marginfig_caption_no_id_html(doc):
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

    key = ('<figure class="marginfig">'
           '<figcaption id="caption-92042fbb8b" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>'
           '</figure>\n')
    assert marginfig.html == key


def test_marginfig_caption_with_id_html(doc):
    """Tests the html generation of captions in figure tags when an id is
    specified."""
    label_man = doc.context['label_manager']

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")

    key = ('<figure class="marginfig">'
           '<figcaption id="fig-1" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>'
           '</figure>\n')

    for count, src in enumerate(srcs):
        # Reset the label manager to avoid duplicate labels
        label_man.reset()

        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content

        assert fig.html == key


def test_figure_html(doc):
    """Test the @figure tag html format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    key = ('<figure class="figure">'
           '<figcaption id="caption-92042fbb8b" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>'
           '</figure>\n')
    assert fig.html == key


def test_fullfigure_html(doc):
    """Test the @fullfigure tag html format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fullfigure{@caption{This is my caption}}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    marginfig = root.content

    key = ('<figure class="fullfigure">'
           '<figcaption id="caption-92042fbb8b" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>'
           '</figure>\n')
    assert marginfig.html == key


def test_panel_html(doc):
    """Test the @panel tag html format"""

    # 1. Generate a panel tag without a width
    src = "@panel{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    key = '<span class="panel">This is my panel</span>\n'
    assert panel.html == key

    # 2. Generate a panel tag a width
    src = "@panel[width='30%']{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    key = '<span class="panel" style="width: 30.0%">This is my panel</span>\n'
    assert panel.html == key


# xhtml target

def test_figure_xhtml(doc, is_xml):
    """Test the @figure tag html format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content

    key = ('<figure class="figure">\n'
           '  <figcaption id="caption-92042fbb8b" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>\n'
           '</figure>\n')
    assert fig.xhtml == key
    assert is_xml(fig.xhtml)


def test_fullfigure_xhtml(doc, is_xml):
    """Test the @fullfigure tag xhtml format"""

    # Set the label format for the caption figure
    label_fmts = doc.context['label_fmts']
    label_fmts['caption_figure'] = "My Fig. @label.number. "

    # Generate the markup without an id
    src = "@fullfigure{@caption{This is my caption}}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    marginfig = root.content

    key = ('<figure class="fullfigure">\n'
           '  <figcaption id="caption-92042fbb8b" class="caption">'
           '<span class="label">My Fig. 1. </span>'
           'This is my caption</figcaption>\n'
           '</figure>\n')
    assert marginfig.xhtml == key
    assert is_xml(marginfig.xhtml)


def test_panel_xhtml(doc, is_xml):
    """Test the @panel tag xhtml format"""

    # 1. Generate a panel tag without a width
    src = "@panel{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    assert panel.xhtml == '<span class="panel">This is my panel</span>\n'
    assert is_xml(panel.xhtml)

    # 2. Generate a panel tag a width
    src = "@panel[width='30%']{This is my panel}"

    # Generate a tag and compare the generated html to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    panel = root.content

    assert (panel.xhtml ==
            '<span class="panel" style="width: 30.0%">This is my panel</span>\n')
    assert is_xml(panel.xhtml)
