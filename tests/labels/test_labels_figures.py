"""
Test labels for figures
"""
from lxml import etree

from disseminate import Document


def test_label_figure_html(tmpdir):
    """Tests the generation of figure labels for html"""
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

    # 1. Test with a label label

    # Generate a specific labels
    label1 = label_man.add_label(document=doc,  kind='figure', id='fig:image1')

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == '<span id="fig:image1" class="figure-label">Fig. 1.1.</span>'

    # Check the html label using the a tag_format from the context
    doc.context['figure_label'] = "context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span id="fig:image1" class="figure-label">'
                    'context 1</span>')


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

    # Generate a specific labels
    label1 = label_man.add_label(document=doc, kind='figure', id='fig:image1')

    # Check the html reference (from inside the document)
    html = etree.tostring(label1.ref(target='.html'))
    html = html.decode('utf-8')
    assert html == ('<a class="figure-ref" '
                    'href="/main.html#fig:image1">Fig. 1.1</a>')
