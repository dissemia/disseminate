"""
Test labels for headings
"""
from lxml import etree

from disseminate import Document
from disseminate.tags.headings import Section
from disseminate.labels import LabelManager


def test_label_heading_html(tmpdir):
    """Tests the generation of headinglabels for html"""
    # Create a test document and global_context
    global_context = {'_target_root': str(tmpdir),
                      '_segregate_targets': True}
    src_filepath = tmpdir.join('src').join('main.dm')
    doc = Document(src_filepath=str(src_filepath),
                   targets={'.html': str(tmpdir.join('html').join('main.html')),
                            '.tex': str(tmpdir.join('html').join('main.html'))},
                   global_context=global_context)

    # Get a label manager
    label_man = LabelManager()

    # Generate a specific labels
    section = Section(name='section', content='My first section',
                      attributes=tuple(), local_context=doc.local_context,
                      global_context=doc.global_context)
    label1 = label_man.add_label(document=doc, tag=section,
                                 kind=('header', 'section'))

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == '<span class="section-label">My first section</span>'

    # Check the html label using the a tag_format from the global_context
    doc.global_context['header_label'] = "global_context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span class="section-label">'
                    'global_context 1</span>')

    # Check the html label using the a tag_format from the local_context
    doc.local_context['header_label'] = "local_context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span class="section-label">'
                    'local_context 1</span>')

    # Generate a specific labels with a short label.
    # Reset contexts
    doc.local_context.clear()
    doc.global_context.clear()

    section = Section(name='section', content='My first section',
                      attributes=(('short', 'short'),),
                      local_context=doc.local_context,
                      global_context=doc.global_context)
    label2 = label_man.add_label(document=doc, tag=section,
                                 kind=('header', 'section'))

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label2.label('.html'))
    html = html.decode('utf-8')
    assert html == '<span class="section-label">short</span>'


def test_ref_heading_html(tmpdir):
    pass