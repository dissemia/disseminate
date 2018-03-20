"""
Test labels for figures
"""
from lxml import etree

from disseminate import Document
from disseminate.labels import LabelManager


def test_label_figure_html(tmpdir):
    """Tests the generation of figure labels for html"""
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

    # 1. Test with a label label

    # Generate a specific labels
    label1 = label_man.add_label(document=doc,  kind='figure', id='fig:image1')

    # Check the html label using the default tag format from the settings
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == '<span id="fig:image1" class="figure-label">Fig. .1.</span>'

    # Check the html label using the a tag_format from the global_context
    doc.global_context['figure_label'] = "global_context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span id="fig:image1" class="figure-label">'
                    'global_context 1</span>')

    # Check the html label using the a tag_format from the local_context
    doc.local_context['figure_label'] = "local_context {number}"
    html = etree.tostring(label1.label('.html'))
    html = html.decode('utf-8')
    assert html == ('<span id="fig:image1" class="figure-label">'
                    'local_context 1</span>')


def test_ref_figure_html(tmpdir):
    """Tests the generation of figure references for html"""
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
    label1 = label_man.add_label(document=doc, kind='figure', id='fig:image1')

    # Check the html reference (from inside the document)
    html = etree.tostring(label1.ref(target='.html'))
    html = html.decode('utf-8')
    assert html == ('<a class="figure-ref" '
                    'href="/main.html#fig:image1">Fig. .1</a>')

    # Check the html reference (from outside the document and with a different
    # local_context)
    local_context = {'_src_filepath': 'different',
                     'figure': "Fig. {number}"}
    html = etree.tostring(label1.ref(target='.html'))
    html = html.decode('utf-8')
    assert html == ('<a class="figure-ref" '
                    'href="/main.html#fig:image1">Fig. .1</a>')
