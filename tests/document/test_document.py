"""
Tests for Document classes and functions.
"""
import pathlib

import pytest

from disseminate.document import Document, DocumentError
from disseminate.paths import SourcePath, TargetPath
from disseminate.utils.tests import strip_leading_space
from disseminate import settings


def test_document_paths(tmpdir):
    """Tests the setting of paths for documents."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a test source file
    src_path = tmpdir / 'src'
    src_path.mkdir()
    src_filepath = src_path / 'file1.dm'
    src_filepath.write_text("""
    ---
    targets: html
    ---
    """)

    # Create the test document
    doc = Document(src_filepath, tmpdir)

    # Test the paths
    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == str(src_filepath)
    assert str(doc.src_filepath.project_root) == str(src_path)

    assert isinstance(doc.project_root, SourcePath)
    assert str(doc.project_root) == str(src_path)

    assert isinstance(doc.target_root, TargetPath)
    assert str(doc.target_root) == str(tmpdir)
    assert str(doc.target_root.target_root) == str(tmpdir)


def test_document_numbers(tmpdir):
    """Tests the document number property."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a document tree.
    src_path = tmpdir / 'src'
    src_path.mkdir()

    src_filepath1 = src_path / 'file1.dm'
    src_filepath2 = src_path / 'file2.dm'
    src_filepath3 = src_path / 'file3.dm'

    src_filepath1.write_text("""---
include:
  file2.dm
  file3.dm
---""")
    src_filepath2.touch()
    src_filepath3.touch()

    # 1. Load the root document
    doc = Document(src_filepath=src_filepath1, target_root=tmpdir)

    doc_list = doc.documents_list(only_subdocuments=False)
    assert doc.number == 1
    assert doc_list[0].src_filepath == src_filepath1
    assert doc_list[0].number == 1
    assert doc_list[1].src_filepath == src_filepath2
    assert doc_list[1].number == 2
    assert doc_list[2].src_filepath == src_filepath3
    assert doc_list[2].number == 3

    # Reorder the documents and reload the document.
    src_filepath1.write_text("""---
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


def test_document_src_filepaths():
    """Test the src_filepaths of documents."""
    # 1. Example1 does not have markup source files in a src
    #    directory.
    doc = Document("tests/document/example1/dummy.dm")

    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == "tests/document/example1/dummy.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example1"
    assert str(doc.src_filepath.subpath) == "dummy.dm"

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert str(doc.src_filepath) == "tests/document/example4/src/file.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example4/src"
    assert str(doc.src_filepath.subpath) == "file.dm"

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")

    assert isinstance(doc.src_filepath, SourcePath)
    assert str(doc.src_filepath) == "tests/document/example5/index.dm"
    assert str(doc.src_filepath.project_root) == "tests/document/example5"
    assert str(doc.src_filepath.subpath) == "index.dm"

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]

    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub1/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub1/index.dm"

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub2/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub2/index.dm"

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.src_filepath, SourcePath)
    assert str(subdoc.src_filepath) == "tests/document/example5/sub3/index.dm"
    assert str(subdoc.src_filepath.project_root) == "tests/document/example5"
    assert str(subdoc.src_filepath.subpath) == "sub3/index.dm"


def test_document_targets():
    """Test the document targets method."""
    doc = Document("tests/document/example1/dummy.dm")

    # dummy.dm has the entry 'html, tex' set in the header.
    targets = doc.targets

    assert '.html' in targets
    assert isinstance(targets['.html'], TargetPath)
    assert str(targets['.html']) == 'tests/document/example1/html/dummy.html'
    assert str(targets['.html'].target_root) == 'tests/document/example1'
    assert str(targets['.html'].target) == 'html'
    assert str(targets['.html'].subpath) == 'dummy.html'

    assert '.tex' in targets
    assert str(targets['.tex']) == 'tests/document/example1/tex/dummy.tex'
    assert str(targets['.tex'].target_root) == 'tests/document/example1'
    assert str(targets['.tex'].target) == 'tex'
    assert str(targets['.tex'].subpath) == 'dummy.tex'


def test_document_target_list():
    """Test the setting of the target_list property."""
    doc = Document("tests/document/example1/dummy.dm")

    # dummy.dm has the entry 'html, tex' set in the header.
    assert doc.target_list == ['.html', '.tex']

    # Test an empty target list
    doc.context['targets'] = ''
    assert doc.target_list == []


def test_document_target_filepath():
    """Test the target_filepath method."""

    # 1. Example1 does not have markup source files in a source
    #    directory. Target files will be saved in the project directory
    doc = Document("tests/document/example1/dummy.dm")

    assert isinstance(doc.target_filepath('.html'), TargetPath)
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example1/html/dummy.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example1")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "dummy.html")

    # 2. Example4 has a markup source file in a source directory,
    #    'src'. Target files will be saved in the parent directory of the 'src'
    #    directory
    doc = Document("tests/document/example4/src/file.dm")
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example4/html/file.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example4")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "file.html")

    # 3. Example5 has markup source files in the root project directory, and
    #    in the sub1, sub2 and sub3 directories.
    doc = Document("tests/document/example5/index.dm")
    assert (str(doc.target_filepath('.html')) ==
            "tests/document/example5/html/index.html")
    assert (str(doc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(doc.target_filepath('.html').target) ==
            "html")
    assert (str(doc.target_filepath('.html').subpath) ==
            "index.html")

    # Check the subdocuments
    subdoc = list(doc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub1/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub1/index.html")

    subdoc = list(doc.subdocuments.values())[1]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub2/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub2/index.html")

    subdoc = list(subdoc.subdocuments.values())[0]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub2/subsub2/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub2/subsub2/index.html")

    subdoc = list(doc.subdocuments.values())[2]
    assert isinstance(subdoc.target_root, TargetPath)
    assert str(subdoc.target_root) == 'tests/document/example5'
    assert (str(subdoc.target_filepath('.html')) ==
            "tests/document/example5/html/sub3/index.html")
    assert (str(subdoc.target_filepath('.html').target_root) ==
            "tests/document/example5")
    assert (str(subdoc.target_filepath('.html').target) ==
            "html")
    assert (str(subdoc.target_filepath('.html').subpath) ==
            "sub3/index.html")


def test_document_target_list_update(tmpdir):
    """Tests the proper updating of the target list."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a test source document
    project_root = tmpdir / 'src'
    project_root.mkdir()
    src_filepath = project_root / 'test.dm'

    markup = """---
    targets: txt
    ---
    """
    src_filepath.write_text(strip_leading_space(markup))

    doc = Document(src_filepath, tmpdir)

    assert doc.target_list == ['.txt']

    # Update the header
    markup = """---
        targets: tex
        ---
        """
    src_filepath.write_text(strip_leading_space(markup))
    doc.load_document()

    assert doc.target_list == ['.tex']


def test_document_ast_caching(tmpdir):
    """Tests the caching of the AST based on file modification times."""
    tmpdir = pathlib.Path(tmpdir)

    # Load the document and render it with no template. Opening the document
    # loads the ast.
    doc = Document("tests/document/example1/dummy.dm", tmpdir)

    body_attr = settings.body_attr
    ast = doc.context[body_attr]
    mtime = doc.mtime
    assert ast is not None
    assert mtime is not None

    # Try loading the AST again. At this point, it shouldn't be different
    doc.load_document()
    assert ast == doc.context[body_attr]
    assert mtime == doc.mtime


def test_document_custom_template(tmpdir):
    """Tests the loading of custom templates from the yaml header."""
    tmpdir = pathlib.Path(tmpdir)

    # Write a temporary file. We'll use the tree.html template, which contains
    # the text "Disseminate Project Index"
    project_root = tmpdir / 'src'
    project_root.mkdir()
    in_file = project_root / "index.dm"
    out_file = tmpdir / 'html' / "index.html"

    markup = """
    ---
    template: server/tree
    targets: html
    ---
    """
    in_file.write_text(strip_leading_space(markup))

    # Make document
    doc = Document(in_file)
    doc.render()
    assert "Disseminate Project Index" in out_file.read_text()

    # Write to the file again, but don't include the template. This time it
    # shouldn't contain the text "Disseminate Project Index"
    in_file.write_text("test")
    target_filepath = doc.targets['.html']
    assert doc.render_required(target_filepath=target_filepath)
    doc.render()
    assert "Disseminate Project Index" not in out_file.read_text()


def test_document_template_updates(tmpdir):
    """Tests the update of rendered targets when the template changes."""
    tmpdir = pathlib.Path(tmpdir)

    # Create the markup source file and a test template
    project_root = tmpdir / 'src'
    project_root.mkdir()
    template = project_root / "index.html"
    in_file = project_root / "index.dm"
    target = tmpdir / 'html'
    target.mkdir()
    out_file = target / "index.html"

    template.write_text("""test1""")
    in_file.write_text("""---
    targets: html
    template: index
    ---""")

    # Load the document and test its contents
    doc = Document(in_file)
    doc.render()

    assert not doc.render_required(out_file)
    assert out_file.read_text() == 'test1'

    # Change the template and see if the rendered output changes
    template.write_text("""test2""")

    assert doc.render_required(out_file)
    doc.render()
    assert out_file.read_text() == 'test2'


def test_document_context_update(tmpdir):
    """Tests that the context is properly updated in subsequent renders."""
    tmpdir = pathlib.Path(tmpdir)

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", tmpdir)

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
    doc.src_filepath = SourcePath(project_root="tests/document/example2",
                                  subpath="noheader.dm")
    doc.load_document(reload=True)

    # Check the contents  of the local_context
    assert 'title' not in doc.context
    assert 'author' not in doc.context
    assert '@macro' not in doc.context

    # The 'targets' entry should revert to the default
    assert doc.context['targets'] == settings.default_context['targets']

    assert id(doc.context) == context_id


def test_document_macros(tmpdir):
    """Tests that macros defined in the header of a document are properly
    processed."""
    tmpdir = pathlib.Path(tmpdir)

    temp_file = TargetPath(target_root=tmpdir,
                           target='html',
                           subpath='withheader.html')

    # First load a file with a header
    doc = Document("tests/document/example2/withheader.dm", tmpdir)

    doc.render()
    # See if the macro was properly replaced
    rendered_html = temp_file.read_text()

    assert '@macro' not in rendered_html
    assert '<i>example</i>' in rendered_html


# Test targets
@pytest.fixture(params=['.html', '.tex'])
def target(request):
    return request.param


def test_document_render(tmpdir, target):
    """Tests the conversion of a basic html file."""
    tmpdir = pathlib.Path(tmpdir)

    ext = target
    stripped_ext = ext.strip('.')

    # Get a path to a temporary file
    temp_file = TargetPath(target_root=tmpdir,
                           target=stripped_ext,
                           subpath='dummy' + ext)

    # Load the document and render it with no template
    doc = Document("tests/document/example1/dummy.dm", tmpdir)

    targets = {k: v for k, v in doc.targets.items() if k == ext}
    doc.render(targets=targets)

    # Make sure the output matches the answer key
    render_file = doc.target_filepath(target=ext)
    assert temp_file.read_text() == render_file.read_text()

    # An invalid file raises an error
    with pytest.raises(DocumentError):
        doc = Document("tests/document/missing.dm")
