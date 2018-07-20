"""
Tests for Document classes and functions.
"""
import pytest

from disseminate.document import Document, DocumentError
from disseminate.utils.tests import strip_leading_space
from disseminate import settings


def test_number_property(tmpdir):
    """Tests the document number property."""
    # Create a document tree.
    src_path = tmpdir.join('src')
    src_path.mkdir()

    src_filepath1 = src_path.join('file1.dm')
    src_filepath2 = src_path.join('file2.dm')
    src_filepath3 = src_path.join('file3.dm')

    src_filepath1.write("""---
include:
  file2.dm
  file3.dm
---""")
    src_filepath2.ensure()
    src_filepath3.ensure()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=str(tmpdir))

    doc_list = doc.documents_list(only_subdocuments=False)
    assert doc.number == 1
    assert doc_list[0].src_filepath == str(src_filepath1)
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == str(src_filepath2)
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == str(src_filepath3)
    assert doc_list[2].number == 3

    # Reorder the documents and reload the document.
    src_filepath1.write("""---
include:
  file3.dm
  file2.dm
---""")
    doc.load_document()

    doc_list = doc.documents_list(only_subdocuments=False)
    assert doc.number == 1
    assert doc_list[0].number == 1
    assert doc_list[1].number == 2
    assert doc_list[2].number == 3


def test_ast_caching(tmpdir):
    """Tests the caching of the AST based on file modification times."""
    # Load the document and render it with no template. Opening the document
    # loads the ast.
    doc = Document("tests/document/example1/dummy.dm",
                   str(tmpdir))

    body_attr = settings.body_attr
    ast = doc.context[body_attr]
    mtime = doc.mtime
    assert ast is not None
    assert mtime is not None

    # Try loading the AST again. At this point, it shouldn't be different
    doc.load_document()
    assert ast == doc.context[body_attr]
    assert mtime == doc.mtime


def test_target_list():
    """Test the setting of the target_list property."""
    doc = Document("tests/document/example1/dummy.dm")

    # dummy.dm has the entry 'html, tex' set in the header.
    assert doc.target_list == ['.html', '.tex']

    # Test an empty target list
    doc.context['targets'] = ''
    assert doc.target_list == []


def test_target_filepath():
    """Test the target_filepath method."""

    # 1. Example1 does not have markup source files in a source
    #    directory. Target files will be saved in the project directory
    doc = Document("tests/document/example1/dummy.dm")

    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example1/html/dummy.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "dummy.html")
    assert (doc.target_filepath('.tex', render_path=True) ==
            "tests/document/example1/tex/dummy.tex")
    assert (doc.target_filepath('.tex', render_path=False) ==
            "dummy.tex")

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example4/html/file.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "file.html")

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")
    assert doc.target_root == 'tests/document/example5'
    assert (doc.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/index.html")
    assert (doc.target_filepath('.html', render_path=False) ==
            "index.html")

    # Check the subdocuments
    subdocument = list(doc.subdocuments.values())[0]
    assert subdocument.target_root == 'tests/document/example5'
    assert (subdocument.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub1/index.html")

    subdocument = list(doc.subdocuments.values())[1]
    assert subdocument.target_root == 'tests/document/example5'
    assert (subdocument.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub2/index.html")

    subdocument = list(subdocument.subdocuments.values())[0]
    assert subdocument.target_root == 'tests/document/example5'
    assert (subdocument.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub2/subsub2/index.html")

    subdocument = list(doc.subdocuments.values())[2]
    assert subdocument.target_root == 'tests/document/example5'
    assert (subdocument.target_filepath('.html', render_path=True) ==
            "tests/document/example5/html/sub3/index.html")


def test_custom_template(tmpdir):
    """Tests the loading of custom templates from the yaml header."""
    # Write a temporary file. We'll use the tree.html template, which contains
    # the text "Disseminate Project Index"
    tmpdir.mkdir('src')
    in_file = tmpdir.join('src').join("index.dm")
    out_file = tmpdir.join('html').join("index.html")

    markup = """
    ---
    template: tree
    targets: html
    ---
    """
    in_file.write(strip_leading_space(markup))

    # Make document
    doc = Document(str(in_file))
    doc.render()
    assert "Disseminate Project Index" in out_file.read()

    # Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "Disseminate Project Index"
    in_file.write("test")
    target_filepath = doc.targets['.html']
    assert doc.render_required(target_filepath=target_filepath)
    doc.render()
    assert "Disseminate Project Index" not in out_file.read()


def test_template_updates(tmpdir):
    """Tests the update of rendered targets when the template changes."""

    # Create the markup source file and a test template
    tmpdir.mkdir('src')
    template = tmpdir.join('src').join("index.html")
    in_file = tmpdir.join('src').join("index.dm")
    out_file = tmpdir.join('html').join("index.html")

    template.write("""test1""")
    in_file.write("""---
    targets: html
    template: index
    ---""")

    # Load the document and test its contents
    doc = Document(str(in_file))
    doc.render()

    assert not doc.render_required(str(out_file))
    assert out_file.read() == 'test1'

    # Change the template and see if the rendered output changes
    template.write("""test2""")

    assert doc.render_required(str(out_file))
    doc.render()
    assert out_file.read() == 'test2'


def test_context_update(tmpdir):
    """Tests that the context is properly updated in subsequent renders."""
    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", str(tmpdir))

    # Check the contents of the context.
    # The title entry is converted to a tag.
    assert 'title' in doc.context
    assert doc.context['title'] == 'My first title'

    # The author entry is converted to a tag.
    assert 'author' in doc.context
    assert doc.context['author'] == 'Justin L Lorieau'

    # The target 'tex' is specified. It should not match the default setting,
    # for the later test.
    assert 'targets' in doc.context
    assert doc.context['targets'] != settings.default_context['targets']
    assert doc.context['targets'] == 'html, tex'

    assert '@macro' in doc.context

    # Get the local_context id to make sure it stays the same
    context_id = id(doc.context)

    # Now switch to a file without a header and make sure the header values
    # are removed
    doc.src_filepath = "tests/document/example2/noheader.dm"
    doc.load_document(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.context
    assert 'author' not in doc.context
    assert '@macro' not in doc.context

    # The 'targets' entry should revert to the default
    assert doc.context['targets'] == settings.default_context['targets']

    assert id(doc.context) == context_id


def test_target_list_update(tmpdir):
    """Tests the proper updating of the target list."""

    # Create a test source document
    tmpdir.join('src').mkdir()
    src_filepath = tmpdir.join('test.dm')

    markup = """---
    targets: txt
    ---
    """
    src_filepath.write(strip_leading_space(markup))

    doc = Document(src_filepath, str(tmpdir))

    assert doc.target_list == ['.txt']

    # Update the header
    markup = """---
        targets: tex
        ---
        """
    src_filepath.write(strip_leading_space(markup))
    doc.load_document()

    assert doc.target_list == ['.tex']


def test_document_macros(tmpdir):
    """Tests that macros defined in the header of a document are properly
    processed."""
    temp_file = tmpdir.join('html').join('withheader.html')

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm",
                   str(tmpdir))

    doc.render()
    # See if the macro was properly replaced
    rendered_html = temp_file.read()

    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


# Test targets
@pytest.fixture(params=['.html', '.tex'])
def target(request):
    return request.param


def test_render(tmpdir, target):
    """Tests the conversion of a basic html file."""
    ext = target
    stripped_ext = ext.strip('.')

    # Get a path to a temporary file
    temp_file = str(tmpdir.join(stripped_ext, 'dummy' + ext))

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm",
                   str(tmpdir))

    targets = {k: v for k, v in doc.targets.items() if k == ext}
    doc.render(targets=targets)

    # Make sure the output matches the answer key
    with open(temp_file, 'r') as f, \
         open("tests/document/example1/dummy" + ext) as g:
        assert f.read() == g.read()

    # An invalid file raises an error
    with pytest.raises(DocumentError):
        doc = Document("tests/document/missing.dm")
