"""
Test the Ref tag.
"""
import pytest

from disseminate.tags import Tag
from disseminate.tags.ref import Ref
from disseminate.label_manager import LabelNotFound


def test_ref_missing(doc):
    """Test the ref tag for a missing caption"""

    # Prepare a ref tag
    src = "@ref{test}"

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)

    # Trying to convert the root ast to a target type, like html, will raise
    # an LabelNotFound error
    with pytest.raises(LabelNotFound):
        root.html


# tex tests

def test_ref_tex(doc):
    """Test the ref tag for a present caption in the texformat"""

    # Prepare a ref tag and the formatting string
    src = "@ref{test}"
    fmt = '@b{My Fig. @label.number}'
    doc.context['label_fmts']['ref_caption_figure_tex'] = fmt

    # Create a label in the label manager
    label_manager = doc.context['label_manager']
    label_manager.add_content_label(id='test', kind=('caption', 'figure'),
                                    title='my test', context=doc.context)

    # Generate a tag and compare the generated tex to the answer key
    root = Tag(name='root', content=src, attributes='', context=doc.context)

    # Generate the tag and test the ref tag's html content
    ref = root.content

    assert isinstance(ref, Ref)
    assert ref.tex == '\\href{#test}{\\textbf{My Fig. 1}}'


# html tests

def test_ref_html(doc):
    """Test the ref tag for a present caption in the html format"""

    # Prepare a ref tag and the formatting string
    src = "@ref{test}"
    fmt = '@b{My Fig. @label.number}'
    doc.context['label_fmts']['ref_caption_figure_html'] = fmt

    # Create a label in the label manager
    label_manager = doc.context['label_manager']
    label_manager.add_content_label(id='test', kind=('caption', 'figure'),
                                    title='my test', context=doc.context)

    # Generate a root tag with a ref tag
    root = Tag(name='root', content=src, attributes='', context=doc.context)

    # Generate the tag and test the ref tag's html content
    ref = root.content

    assert isinstance(ref, Ref)
    assert ref.html == ('<a href="#test" class="ref">'
                        '<strong>My Fig. 1</strong></a>')


def test_ref_html_crossreference_html(doctree):
    """Test the ref tag between documents, using the html target."""

    # Use the doctree to setup ref tags
    doc1 = doctree
    doc2, doc3 = doc1.documents_list(only_subdocuments=True)

    assert doc1.doc_id == 'test.dm'
    assert doc2.doc_id == 'test2.dm'

    # Create label for doc1 and doc2
    label_manager = doc1.context['label_manager']
    label_manager.add_content_label(id='doc1', kind=('caption', 'figure'),
                                    title='my test', context=doc1.context)
    label_manager.add_content_label(id='doc2', kind=('caption', 'figure'),
                                    title='my test', context=doc2.context)

    # Prepare the format string for the ref tag
    fmt = '@b{My Fig. @label.number}'
    doc1.context['label_fmts']['ref_caption_figure_html'] = fmt

    # Generate a root tag with a ref tag
    root1 = Tag(name='root', content='@ref{doc2}', attributes='',
                context=doc1.context)
    root2 = Tag(name='root', content='@ref{doc1}', attributes='',
                context=doc2.context)

    # Generate the tag and test the ref tag's html content
    ref1 = root1.content
    ref2 = root2.content

    assert isinstance(ref1, Ref)
    assert ref1.html == ('<a href="test2.html#doc2" class="ref">'
                         '<strong>My Fig. 2</strong></a>')
    assert isinstance(ref2, Ref)
    assert ref2.html == ('<a href="test.html#doc1" class="ref">'
                         '<strong>My Fig. 1</strong></a>')


# xhtml tests

def test_ref_xhtml(doc, is_xml):
    """Test the ref tag for a present caption in the xhtml format"""

    # Prepare a ref tag and the formatting string
    src = "@ref{test}"
    fmt = '@b{My Fig. @label.number}'
    doc.context['label_fmts']['ref_caption_figure_html'] = fmt

    # Create a label in the label manager
    label_manager = doc.context['label_manager']
    label_manager.add_content_label(id='test', kind=('caption', 'figure'),
                                    title='my test', context=doc.context)

    # Generate a root tag with a ref tag
    root = Tag(name='root', content=src, attributes='', context=doc.context)

    # Generate the tag and test the ref tag's html content
    ref = root.content

    assert isinstance(ref, Ref)
    assert ref.xhtml == ('<a href="#test" class="ref">'
                         '<strong>My Fig. 1</strong></a>')
    assert is_xml(ref.xhtml)


def test_ref_html_crossreference_xhtml(doctree, is_xml):
    """Test the ref tag between documents, using the xhtml target."""

    # Use the doctree to setup ref tags
    doc1 = doctree
    doc2, doc3 = doc1.documents_list(only_subdocuments=True)

    # Add xhtml to the document target list
    doc1.src_filepath.write_text("""
    ---
    targets: xhtml
    include:
      test2.dm
      test3.dm
    ---
    """)
    doc1.load()

    assert doc1.doc_id == 'test.dm'
    assert doc2.doc_id == 'test2.dm'

    # Create label for doc1 and doc2
    label_manager = doc1.context['label_manager']
    label_manager.add_content_label(id='doc1', kind=('caption', 'figure'),
                                    title='my test', context=doc1.context)
    label_manager.add_content_label(id='doc2', kind=('caption', 'figure'),
                                    title='my test', context=doc2.context)

    # Prepare the format string for the ref tag
    fmt = '@b{My Fig. @label.number}'
    doc1.context['label_fmts']['ref_caption_figure_html'] = fmt

    # Generate a root tag with a ref tag
    root1 = Tag(name='root', content='@ref{doc2}', attributes='',
                context=doc1.context)
    root2 = Tag(name='root', content='@ref{doc1}', attributes='',
                context=doc2.context)

    # Generate the tag and test the ref tag's html content
    ref1 = root1.content
    ref2 = root2.content

    assert isinstance(ref1, Ref)
    assert ref1.xhtml == ('<a href="test2.xhtml#doc2" class="ref">'
                          '<strong>My Fig. 2</strong></a>')
    assert is_xml(ref1.xhtml)

    assert isinstance(ref2, Ref)
    assert ref2.xhtml == ('<a href="test.xhtml#doc1" class="ref">'
                          '<strong>My Fig. 1</strong></a>')
    assert is_xml(ref2.xhtml)
