"""
Tests for Document classes and functions.
"""
import pytest

from disseminate.document import Document, DocumentError


def test_basic_conversion_html(tmpdir):
    """Tests the conversion of a basic html file."""
    # Get a path to a temporary file
    temp_file = tmpdir.join("test_basic_conversion_html.html")
    temp_path = temp_file.strpath

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm",
                   {'.html': temp_path})
    doc.render()

    # Make sure the output matches the answer key
    with open(temp_path, 'r') as f, \
         open("tests/document/example1/test_basic_conversion_html.html") as g:
        assert f.read() == g.read()

    # An invalid file raises an error
    doc = Document("tests/document/missing.dm",
                   {'.html': temp_path})
    with pytest.raises(FileNotFoundError):
        doc.render()
