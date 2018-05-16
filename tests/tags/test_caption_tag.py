"""
Test the caption and reg tags.
"""
import pytest
from lxml.html import etree

from disseminate import Document
from disseminate.ast import process_ast
from disseminate.tags.caption import Ref
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


# html tests

def test_ref_figure_html(tmpdir):
    """Tests the generation of figure references for html"""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()

    markup = """
    ---
    targets: html
    ---
    """
    src_filepath.write(markup)

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a specific label
    label_man.add_label(document=doc, kind='figure', id='fig:image1')
    label_man.register_labels()
    label1 = label_man.get_label('fig:image1')

    # Generate a reference tag and html
    ref = Ref(name='ref', content=label1.id, attributes=(), context=doc.context)
    html = etree.tostring(ref.html()).decode('utf-8')

    key = ('<a href="/main.html#fig:image1">'
           '<span class="label"><strong>Fig. .1</strong></span>'
           '</a>')
    assert html == key


def test_ref_html(tmpdir):
    """Test the ref tag for a present caption in the html format"""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    doc.context['figure_label'] = "Fig. {label.number}."
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

    key = '<a href="/main.html#test"><span class="label">Fig. 1.</span></a>'

    assert key in root_html


# tex tests

def test_ref_tex(tmpdir):
    """Test the ref tag for a present caption in the texformat"""
    # Create a temporary document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    src_filepath.ensure(file=True)

    doc = Document(src_filepath=src_filepath)
    label_man = doc.context['label_manager']

    doc.context['figure_label'] = "Fig. {label.number}"
    doc.context['targets'] = '.tex'

    # Generate the markup without an id. A reference cannot be made, and a
    # LabelNotFound exception is raised
    src = "@ref{test} @marginfig{@caption{This is my caption}}"

    # Generate a tag and compare the generated tex to the answer key
    root = process_ast(src, context=doc.context)
    label_man.register_labels()

    # Rendering the tex raises the LabelNotFound exception since the label
    # with id 'test' wasn't defined.
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
    assert root_tex.startswith('\\hyperref[test]{Fig. 1}')
