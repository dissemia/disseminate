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


def test_custom_template(tmpdir):
    """Tests the loading of custom templates from the yaml header."""
    # Write a temporary file. We'll use the tree.html template, which contains
    # the text "Disseminate Project Index"
    in_file = tmpdir.join("index.dm")
    out_file = tmpdir.join("index.html")
    input = ["---",
             "template: tree",
             "---",
             ""]
    in_file.write('\n'.join(input))

    # Make document
    doc = Document(str(in_file), {'.html': str(out_file)})
    doc.render()

    assert "Disseminate Project Index" in out_file.read()

    # Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "Disseminate Project Index"
    in_file.write("test")
    doc.render()
    assert "Disseminate Project Index" not in out_file.read()


def test_local_context_update(tmpdir):
    """Tests that the local_context is properly updated in subsequent
    renders."""
    temp_file = tmpdir.join("temp.html")

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm",
                   {'.html': temp_file})
    doc.get_ast()

    # Check the contents  of the local_context
    assert 'title' in doc.local_context
    assert doc.local_context['title'] == 'My first title'

    assert 'author' in doc.local_context
    assert doc.local_context['author'] == 'Justin L Lorieau'

    assert 'macros' in doc.local_context

    # Get the local_context id to make sure it stays the same
    local_context_id = id(doc.local_context)

    # Now switch to a file without a header and make sure the header values
    # are removed
    doc.src_filepath = "tests/document/example2/noheader.dm"
    doc.get_ast(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.local_context
    assert 'author' not in doc.local_context
    assert 'macros' not in doc.local_context

    assert id(doc.local_context) == local_context_id


def test_local_macros(tmpdir):
    """Tests that macros defined in the header of a document are properly
    processed."""
    temp_file = tmpdir.join("temp.html")

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm",
                   {'.html': temp_file})
    doc.render()

    # See if the macro was properly replaced
    rendered_html = temp_file.read()

    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


# TODO: implement test
# def test_dependencies(tmpdir):
#     """Tests that the dependencies are correctly reset when the AST is
#     reprocessed."""

