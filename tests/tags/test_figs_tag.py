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


def test_figure_caption_no_id(tmpdir):
    """Tests the parsing of captions in figure tags when no id is specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']
    label_fmts = doc.context['label_fmts']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption.\nIt has multiple lines}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content
    label_man.register_labels()

    assert fig.name == 'marginfig'
    assert fig.attributes == dict()

    # 1. Get the caption, first with a basic figure label
    label_fmts['caption_figure'] = "Fig. @label.number."

    caption = fig.content
    assert caption.name == 'caption'
    assert caption.attributes == dict()
    assert caption.default == ('Fig. 1. This is my caption.\n'
                               'It has multiple lines')

    # Get the caption, next with a caption title.
    label_fmts['caption_figure'] = "@b{Figure. @label.number}."

    caption = fig.content
    assert caption.name == 'caption'
    assert caption.attributes == dict()
    assert caption.default == ('Figure. 1. This is my caption.\n'
                               'It has multiple lines')

    # A label should have been registered. Altogether, there should be 1 label
    # for the figure. The document's label was wiped out by the
    # 'register_labels' function above.
    labels = label_man.get_labels(kinds='figure')
    assert len(labels) == 1
    label = labels[0]
    assert label.id is not None
    assert label.kind == ('figure',)
    assert label.local_order == (1,)
    assert label.global_order == (1,)


def test_figure_caption_with_id(tmpdir):
    """Tests the parsing of captions in figure tags when an id is specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['label_fmts']['caption_figure'] = "Fig. @number."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    for src in ("@marginfig[id=fig-1]{@caption{This is my caption}}",
                "@marginfig{@caption[id=fig-1]{This is my caption}}"):

        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content
        label_man.register_labels()

        assert fig.name == 'marginfig'

        # Get the caption
        caption = fig.content

        assert caption.name == 'caption'
        assert caption.content == 'This is my caption'

        # 1 label should be registered for the figure
        labels = label_man.get_labels(kinds='figure')
        assert len(labels) == 1
        label = labels[0]

        assert label.id == 'fig-1'
        assert label.kind == ('figure',)
        assert label.local_order == (1,)
        assert label.global_order == (1,)


# html tests

def test_figure_caption_no_id_html(tmpdir):
    """Tests the html generation of captions in figure tags when no id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['label_fmts']['caption_figure'] = "Fig. @label.number."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    marginfig = root.content
    label_man.register_labels()

    key = """<span class="marginfig">
      <span class="figure caption" id="caption-92042fbb8b">
        <span class="label">Fig. 1.</span>
        <span class="caption-text">This is my caption</span>
      </span>
    </span>
    """
    print(marginfig.html)
    assert marginfig.html == strip_leading_space(key)


def test_figure_caption_with_id_html(tmpdir):
    """Tests the html generation of captions in figure tags when an id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['label_fmts']['caption_figure'] = "@b{Fig. @label.number.}"
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")

    key = """<span class="marginfig">
      <span class="figure caption" id="fig-1">
        <span class="label">
          <strong>Fig. 1.</strong>
        </span>
        <span class="caption-text">This is my caption</span>
      </span>
    </span>
    """

    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content
        label_man.register_labels()

        assert fig.html == strip_leading_space(key)


# tex tests

def test_figure_caption_no_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when no id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['label_fmts']['caption_figure'] = "Fig. @label.number."
    doc.context['targets'] = '.tex'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)
    fig = root.content
    label_man.register_labels()

    key = """
    \\begin{marginfigure}
      \\caption{Fig. 1. This is my caption} \\label{caption-92042fbb8b}
    
    \\end{marginfigure}
    """
    assert fig.tex == strip_leading_space(key)


def test_figure_caption_with_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when an id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['label_fmts']['caption_figure'] = "Fig. @label.number."
    doc.context['targets'] = '.tex'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = Tag(name='root', content=src, attributes='', context=doc.context)
        fig = root.content
        label_man.register_labels()

        assert fig.tex == ('\n\\begin{marginfigure}\n'
                           '  \\caption{Fig. 1. This is my caption} '
                           '\\label{fig-1}\n\n'
                           '\\end{marginfigure}\n')
