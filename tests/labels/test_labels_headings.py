"""
Test labels for headings
"""
from lxml import etree

from disseminate import Document
from disseminate.tags.headings import Section
from disseminate.labels import LabelManager


def test_label_heading_html(tmpdir):
    """Tests the generation of headinglabels for html"""
    # Create a test document
    src_filepath = tmpdir.join('src').join('main.dm')
    tmpdir.join('src').mkdir()
    markup = """
    ---
    targets: html, tex
    ---
    """
    src_filepath.write(markup)

    doc = Document(str(src_filepath), str(tmpdir))

    # Get the label manager
    label_man = doc.context['label_manager']

    # Generate a specific labels. This will add the label to the label_manager
    section = Section(name='section', content='My first section',
                      attributes=(('id', 'sec:section1'),),
                      context=doc.context)

    label1 = label_man.get_label('sec:section1')

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span id="sec:section1" class="section-label">'
                    'My first section</span>')

    # Check the html label using the a tag_format from the context
    doc.context['heading_label'] = "context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span id="sec:section1" class="section-label">'
                    'context 1</span>')

    # Generate a specific labels with a short label.
    # Reset contexts
    del doc.context['heading_label']

    section = Section(name='section', content='My first section',
                      attributes=(('short', 'short'),),
                      context=doc.context)
    label2 = label_man.add_label(document=doc, tag=section,
                                 kind=('header', 'section'))

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label2.label('.html'))
    html = html.decode('utf-8')
    assert html == '<span class="section-label">short</span>'


def test_ref_heading_html(tmpdir):
    pass