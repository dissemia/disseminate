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
    with pytest.raises(DocumentError):
        doc.render()


def test_ast_caching(tmpdir):
    """Tests the caching of the AST based on file modification times."""
    # Get a path to a temporary file
    temp_file = tmpdir.join("temp.html")

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm",
                   {'.html': temp_file})

    # The AST hasn't been loaded yet, so the attributes should be zero
    assert doc._ast is None
    assert doc._mtime is None

    # Load the AST, which should set the _ast and _mtime attributes
    doc.get_ast()
    ast = doc._ast
    mtime = doc._mtime
    assert ast is not None
    assert mtime is not None

    # Try loading the AST again. At this point, it shouldn't be different
    doc.get_ast()
    assert ast == doc._ast
    assert mtime == doc._mtime