"""
Test the utility functions for tags.
"""
from disseminate import Document
from disseminate.tags.utils import format_label_tag


def test_format_tag_label_basic(tmpdir):
    """Test the generation of formatted tag labels."""
    # Create a basic test document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('src').join('test.dm')

    src_filepath.write("""
    ---
    target: html
    ---
    @chapter{Chapter One}
    """)

    doc = Document(str(src_filepath), str(tmpdir))
    doc.render()

    # Get the chapter tag.
    ast = doc.get_ast()
    tag = ast.content[1]

    # Get the label tag for the chapter using the default label format
    label_tag = format_label_tag(tag)
    assert label_tag.default() == 'Chapter One'

    # Try changing the label format in the context
    doc.context['chapter_label'] = '{label.tree_number}. {label.chapter_title}'
    label_tag = format_label_tag(tag)
    assert label_tag.default() == '1. Chapter One'

    # Try changing the label format in the attributes
    tag.attributes = (('fmt', 'format string'),)
    label_tag = format_label_tag(tag)
    assert label_tag.default() == 'format string'