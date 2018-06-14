"""
Tests for the figure tags.
"""
from disseminate import Document
from disseminate.ast import process_ast
from disseminate.tags.caption import Caption
from disseminate.utils.tests import strip_leading_space


def test_marginfig_parsing():
    """Test the parsing of marginfig tags."""

    test1 = "@marginfig{fig1}"
    root = process_ast(test1)
    assert root.content.name == 'marginfig'
    assert root.content.content == 'fig1'

    test2 = "@marginfig{{fig1}}"
    root = process_ast(test2)
    assert root.content.name == 'marginfig'
    assert root.content.content == '{fig1}'


def test_figure_caption_no_id(tmpdir):
    """Tests the parsing of captions in figure tags when no id is specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption.\nIt has multiple lines}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    fig = root.content
    assert fig.name == 'marginfig'
    assert fig.attributes == tuple()

    # 1. Get the caption, first with a basic figure label
    doc.context['figure_label'] = "Fig. {label.number}."
    assert isinstance(fig.content, list)
    caption = [i for i in fig.content if isinstance(i, Caption)][0]
    assert caption.name == 'caption'
    assert caption.attributes == tuple()
    assert caption.default == ('Fig. 1. This is my caption.\n'
                               'It has multiple lines')

    # Get the caption, next with a caption title.
    doc.context['figure_label'] = "@b{{Figure. {label.number}}}."
    assert isinstance(fig.content, list)
    caption = [i for i in fig.content if isinstance(i, Caption)][0]
    assert caption.name == 'caption'
    assert caption.attributes == tuple()
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
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    for src in ("@marginfig[id=fig-1]{@caption{This is my caption}}",
                "@marginfig{@caption[id=fig-1]{This is my caption}}"):

        # Generate a tag and compare the generated tex to the answer key
        root = process_ast(src, doc.context)
        label_man.register_labels()

        fig = root.content
        assert fig.name == 'marginfig'

        # Get the caption
        assert isinstance(fig.content, list)
        caption = [i for i in fig.content if isinstance(i, Caption)][0]

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
    doc.context['figure_label'] = "Fig. {label.number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Test the caption's html
    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">\n  '
    root_end = '\n</span>\n'

    root_html = root.html

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    key = """<span class="marginfig">
        <span class="figure caption" id="caption-92042fbb8b"><span class="label">Fig. 1.</span>. <span class="caption-text">This is my caption</span></span>
      </span>"""
    assert root_html == strip_leading_space(key)


def test_figure_caption_with_id_html(tmpdir):
    """Tests the html generation of captions in figure tags when an id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {label.number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")

    key = """
      <span class="marginfig">
        <span class="figure caption" id="fig-1"><span class="label">Fig. 1.</span>. <span class="caption-text">This is my caption</span></span>
      </span>
    """

    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = process_ast(src, context=doc.context)
        label_man.register_labels()

        # Test the caption's html is a root tag
        # The following root tags have to be stripped for the html strings
        root_start = '<span class="root">'
        root_end = '</span>\n'

        root_html = root.html

        # Remove the root tag
        root_html = root_html[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == strip_leading_space(key)


# tex tests

def test_figure_caption_no_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when no id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {label.number}"
    doc.context['targets'] = '.tex'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    root_tex = root.tex
    key = """
    \\begin{marginfigure}
      \caption{Fig. 1. This is my caption} \label{caption-92042fbb8b}
    \\end{marginfigure}
    """
    assert root_tex == strip_leading_space(key)


def test_figure_caption_with_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when an id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {label.number}"
    doc.context['targets'] = '.tex'
    label_man = doc.context['label_manager']

    # Test two cases: one in which the id is in the figure tag, and one in which
    # the id is in the caption tag
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = process_ast(src, context=doc.context)
        label_man.register_labels()

        root_tex = root.tex
        assert root_tex == ('\n\\begin{marginfigure}\n'
                            '  \caption{Fig. 1. This is my caption} \label{fig-1}\n'
                            '\\end{marginfigure}\n')
