"""
Test the caption and reg tags.
"""
import pathlib

from lxml.html import etree

from disseminate import Document, SourcePath, TargetPath
from disseminate.ast import process_ast
from disseminate.tags.ref import Ref
from disseminate.labels import LabelManager


def test_naked_caption(tmpdir, context_cls):
    """Tests the parsing of naked captions (i.e. those not nested in a figure
    or table)."""
    tmpdir = pathlib.Path(tmpdir)

    # Create the context and a label manager
    target_root = TargetPath(target_root=tmpdir)
    context = context_cls(target_root=target_root)
    label_man = LabelManager(root_context=context)
    context['label_manager'] = label_man

    # Generate the markup without an id
    src = "@caption{This is my caption}"

    # Generate a tag and compare the generated tex to the answer key
    caption = process_ast(src, context=context)

    assert caption.name == 'caption'
    assert caption.attributes == {}
    assert caption.content == 'This is my caption'

    # Naked captions do not register labels
    assert len(label_man.labels) == 0


# html tests

def test_ref_figure_html(tmpdir):
    """Tests the generation of figure references for html"""
    # Create a temporary document
    src_path = pathlib.Path(tmpdir, 'src')
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='main.dm')
    src_filepath.touch()
    target_root = TargetPath(tmpdir)

    markup = """
    ---
    targets: html
    ---
    """
    src_filepath.write_text(markup)

    doc = Document(src_filepath, target_root)

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a specific label
    label_man.add_content_label(id='fig:image1', kind='figure',
                                title='Figure 1', context=doc.context)
    label_man.register_labels()
    label1 = label_man.get_label('fig:image1')

    # Generate a reference tag and html
    ref = Ref(name='ref', content=label1.id, attributes=(), context=doc.context)
    html = etree.tostring(ref.html).decode('utf-8')

    key = ('<span class="ref">'
           '<a href="main.html#fig:image1">'
           '<strong>Fig. .1</strong></a>'
           '</span>')
    assert html == key
