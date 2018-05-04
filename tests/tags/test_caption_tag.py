"""
Test the caption and reg tags.
"""
import pytest

from disseminate import Document
from disseminate.tags.caption import Caption
from disseminate.ast import process_ast
from disseminate.labels import LabelManager, LabelNotFound


def test_naked_caption():
    """Tests the parsing of naked captions (i.e. those not nested in a figure
    or table)."""
    # Create a label manager
    label_man = LabelManager()

    # Create a mock context
    context = {'label_manager': label_man}

    # Generate the markup without an id
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=context)

    caption = root.content
    assert caption.name == 'caption'
    assert caption.attributes == tuple()
    assert caption.content == 'This is my caption'

    # Naked captions do not register labels
    assert len(label_man.labels) == 0


def test_figure_caption_no_id(tmpdir):
    """Tests the parsing of captions in figure tags when no id is specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    fig = root.content
    assert fig.name == 'marginfig'
    assert fig.attributes == tuple()

    # Get the caption
    assert isinstance(fig.content, list)
    caption = [i for i in fig.content if isinstance(i, Caption)][0]
    assert caption.name == 'caption'
    assert caption.attributes == tuple()
    assert caption.default() == 'Fig. 1. This is my caption'

    # A label should have been registered. Altogether, there should be 1 label
    # for the figure. The document's label was wiped out by the
    # 'register_labels' function above.
    assert len(label_man.labels) == 1
    labels = label_man.get_labels(kinds='figure')
    label = labels[0]
    assert label.id is not None
    assert label.kind == ('figure',)
    assert label.local_order == (1,)
    assert label.global_order == (1,)


def test_figure_caption_no_id_html(tmpdir):
    """Tests the html generation of captions in figure tags when no id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {number}."
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

    root_html = root.html()

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    key = """<span class="marginfig">
    <span class="caption">
      <span id="caption-92042fbb8b" class="figure-label">Fig. 1.</span>
      <span class="caption-text">This is my caption</span>
    </span>
  </span>"""
    assert root_html == key


def test_figure_caption_no_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when no id is
    specified."""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    root_tex = root.tex()
    key = """
\\begin{marginfigure}
Fig. 1. \\caption{This is my caption}
\\end{marginfigure}
"""
    assert root_tex == key


def test_figure_caption_with_id(tmpdir):
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    """Tests the parsing of captions in figure tags when an id is specified."""
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
        assert len(label_man.labels) == 1
        labels = label_man.get_labels(kinds='figure')
        label = labels[0]
        assert label.id == 'fig-1'
        assert label.kind == ('figure',)
        assert label.local_order == (1,)
        assert label.global_order == (1,)


def test_figure_caption_with_id_html(tmpdir):
    """Tests the html generation of captions in figure tags when an id is
    specified."""
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
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = process_ast(src, context=doc.context)
        label_man.register_labels()

        # Test the caption's html
        # The following root tags have to be stripped for the html strings
        root_start = '<span class="root">'
        root_end = '</span>\n'

        root_html = root.html()
        # Remove the root tag
        root_html = root_html[len(root_start):]  # strip the start
        root_html = root_html[:(len(root_html) - len(root_end))]  # strip end
        assert root_html == ('\n  <span class="marginfig">\n'
                             '    <span class="caption">\n'
                             '      <span id="fig-1" class="figure-label">'
                             'Fig. 1.</span>\n'
                             '      <span class="caption-text">This is my '
                             'caption</span>\n'
                             '    </span>\n'
                             '  </span>\n')


def test_figure_caption_with_id_tex(tmpdir):
    """Tests the tex generation of captions in figure tags when an id is
    specified."""
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
    srcs = ("@marginfig[id=fig-1]{@caption{This is my caption}}",
            "@marginfig{@caption[id=fig-1]{This is my caption}}")
    for count, src in enumerate(srcs):
        # Generate a tag and compare the generated tex to the answer key
        root = process_ast(src, context=doc.context)
        label_man.register_labels()

        root_tex = root.tex()
        assert root_tex == ('\n\\begin{marginfigure}\n'
                            'Fig. 1. \\caption{This is my caption}\n'
                            '\\end{marginfigure}\n')


def test_ref_missing(tmpdir):
    """Test the ref tag for a missing caption"""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup without an id
    src = "@ref{test} @caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Trying to convert the root ast to a target type, like html, will raise
    # an LabelNotFound error
    with pytest.raises(LabelNotFound):
        root.html()

    # There should be only one label for the document
    assert len(label_man.labels) == 1
    assert len(label_man.get_labels(kinds='document')) == 1


def test_ref_html(tmpdir):
    """Test the ref tag for a present caption in the html format"""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_ref'] = "Fig. {number}"
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['targets'] = '.html'
    label_man = doc.context['label_manager']

    # Generate the markup with an id. The marginfig tag is needed to
    # set the kind of the label.
    src = "@ref{test} @marginfig{@caption[id=test]{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    #  Test the ref's html
    root_html = root.html()

    # The following root tags have to be stripped for the html strings
    root_start = '<span class="root">'
    root_end = '</span>\n'

    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    assert ('<a class="figure-ref" href="/main.html#test">'
            'Fig. 1</a>') in root_html

    # Try removing the '.html' target for the document. In this case, a link
    # should not be rendered.
    doc.context['targets'] = ''

    root_html = root.html()
    # Remove the root tag
    root_html = root_html[len(root_start):]  # strip the start
    root_html = root_html[:(len(root_html) - len(root_end))]  # strip end

    assert ('<a class="figure-ref" href="/main.html#test">'
            'Fig. 1</a>') not in root_html
    assert ('<span id="test" class="figure-label">Fig. 1.</span>'
            in root_html)


def test_ref_tex(tmpdir):
    """Test the ref tag for a present caption in the texformat"""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    label_man = doc.context['label_manager']

    doc.context['figure_ref'] = "Fig. {number}"
    doc.context['figure_label'] = "Fig. {number}."
    doc.context['figure_link_tex'] = ('\\hyperlink{{{id}}}{{Fig. '
                                      '{number}}}')
    doc.context['targets'] = '.tex'

    # Generate the markup without an id. A reference cannot be made, and a
    # LabelNotFound exception is raised
    src = "@ref{test} @marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Rendering the tex raises the LabelNotFound exception
    with pytest.raises(LabelNotFound):
        root.tex()

    # Generate the markup with an id. The marginfig tag is needed to
    # set the kind of the label.
    src = "@ref{test} @marginfig{@caption[id=test]{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    #  Test the ref's html
    root_tex = root.tex()
    assert root_tex.startswith('\hyperlink{test}{Fig. 1}')
