"""
Tests the core Tag and TagFactory classes.
"""
import pytest

from disseminate.document import Document
from disseminate.ast import process_ast
from disseminate.tags import Tag, TagError
from disseminate.tags.text import P


def test_flatten_tag():
    """Test the flatten method."""
    # Setup a test source string
    test = """
            This is my test document. It has multiple paragraphs.

            Here is a new one with @b{bolded} text as an example.
            @figuretag[offset=-1.0em]{
              @imgtag{media/files}
              @captiontag{This is my @i{first} figure.}
            }

            This is a @13C variable, but this is an email address: justin@lorieau.com

            Here is a @i{new} paragraph."""

    # Parse it
    root = process_ast(test)

    # Convert the root tag to a flattened list and check the items
    flattened_tag = root.flatten(filter_tags=False)

    assert len(flattened_tag) == 18
    assert flattened_tag[0].name == 'root'
    assert isinstance(flattened_tag[1], str)
    assert flattened_tag[2].name == 'b'
    assert isinstance(flattened_tag[3], str)
    assert flattened_tag[4].name == 'figuretag'
    assert isinstance(flattened_tag[5], list)
    assert isinstance(flattened_tag[6], str)
    assert flattened_tag[7].name == 'imgtag'
    assert isinstance(flattened_tag[8], str)
    assert flattened_tag[9].name == 'captiontag'
    assert isinstance(flattened_tag[10], list)
    assert isinstance(flattened_tag[11], str)
    assert flattened_tag[12].name == 'i'
    assert isinstance(flattened_tag[13], str)
    assert isinstance(flattened_tag[14], str)
    assert isinstance(flattened_tag[15], str)
    assert flattened_tag[16].name == 'i'
    assert isinstance(flattened_tag[17], str)

    # Convert the root tag to a flattened list with only tags
    flattened_tag = root.flatten(filter_tags=True)

    assert len(flattened_tag) == 7
    assert flattened_tag[0].name == 'root'
    assert flattened_tag[1].name == 'b'
    assert flattened_tag[2].name == 'figuretag'
    assert flattened_tag[3].name == 'imgtag'
    assert flattened_tag[4].name == 'captiontag'
    assert flattened_tag[5].name == 'i'
    assert flattened_tag[6].name == 'i'


def test_tag_mtime(tmpdir):
    """Test the calculation of mtimes for labels."""
    # Prepare two files
    tmpdir.mkdir('src')
    src_filepath1 = tmpdir.join('src').join('main.dm')
    src_filepath2 = tmpdir.join('src').join('sub.dm')

    # Write to the files
    src_filepath1.write("""
    ---
    target: html
    include:
        sub.dm
    ---
    @chapter[id=chapter-one]{Chapter One}
    """)

    src_filepath2.write("""
    ---
    target: html
    ---
    @chapter[id=chapter-two]{Chapter Two}
    """)

    doc = Document(str(src_filepath1), tmpdir)  # main.dm

    # Get the two documents
    docs = doc.documents_list(only_subdocuments=False, recursive=False)
    assert len(docs) == 2
    doc1, doc2 = docs  # doc1 == doc; doc2 is sub.dm

    # Get the root tag and the mtimes
    root1 = doc1.get_ast()
    root2 = doc2.get_ast()

    # Check that the mtimes match the file modification times
    assert src_filepath1.mtime() == root1.mtime
    assert src_filepath2.mtime() == root2.mtime

    # Now change the two src files
    src_filepath1.write("""
    ---
    target: html
    include:
        sub.dm
    ---
    @ref{chapter-two}
    @chapter[id=chapter-one]{Chapter One}
    """)

    src_filepath2.write("""
    ---
    target: html
    ---
    @chapter[id=chapter-two]{Chapter Two}
    """)

    # Get the root tag and the mtimes
    root1 = doc1.get_ast()
    root2 = doc2.get_ast()

    # Check that the first file was written before the second.
    assert src_filepath1.mtime() < src_filepath2.mtime()

    print("src_filepath1.mtime", src_filepath1.mtime())
    print("src_filepath2.mtime", src_filepath2.mtime())
    print("root1.mtime", root1.mtime)
    print("root2.mtime", root2.mtime)
    # Both root tags should have the modification time of the 2nd file
    assert src_filepath2.mtime() < root1.mtime
    assert src_filepath2.mtime() < root2.mtime


# Tests for html targets

def test_html():
    """Test the conversion of tags to html strings."""

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               context=dict())
    assert root.html() == '<span class="root">base string</span>\n'

    # Generate a nested root tag with sub-tags
    b = Tag(name='b', content='bolded', attributes=None, context=dict())
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=dict())
    assert root.html() == ('<span class="root">'
                           'my first<b>bolded</b>string'
                           '</span>\n')

    # Test the rendering of a tag with content for an invalid type.
    # This should raise an exception
    root = Tag(name='root', content=set(), attributes=None, context=dict())
    with pytest.raises(TagError):
        root.html()


def test_html_invalid_tag():
    """Test the rendering of invalid tags into html."""

    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='eqn', content='my eqn', attributes=None, context=dict())
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=dict())
    assert root.html() == ('<span class="root">my first'
                           '<span class=\"eqn\">my eqn</span>'
                           'string</span>\n')


def test_html_excluded_tag():
    """Test the rendering of an excluded tag."""

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='my eqn', attributes=None, context=dict())
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=dict())
    assert root.html() == ('<span class="root">my first'
                           '<span class=\"script\">my eqn</span>'
                           'string</span>\n')


def test_html_unsafe_tag():
    """Test the rendering of an unsafe tag in the string content of a tag."""

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='<script>', attributes=None,
              context=dict())
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=dict())
    assert root.html() == ('<span class="root">my first'
                           '<span class=\"script\">&lt;script&gt;</span>'
                           'string</span>\n')


def test_html_nested():
    """Nest nested tags with html"""

    # Test a basic string without additional tags
    p = P(name='p', content='paragraph', attributes=None, context=dict())
    root = Tag(name='root', content=p, attributes=None, context=dict())
    assert root.html() == ('<span class="root">\n'
                           '  <p>paragraph</p>\n'
                           '</span>\n')

# Tests for tex targets

def test_tex():
    """Tests the rendering of latex tags."""

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               context=dict())
    assert root.tex() == "base string"

    # Generate a nested root tag with sub-tags
    b = Tag(name='textbf', content='bolded', attributes=None,
            context=dict())
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=dict())
    assert root.tex() == "my first\\textbf{bolded}string"

    # Test the rendering of a tag with content for an invalid type.
    # This should raise an exception
    root = Tag(name='root', content=set(), attributes=None,
               context=dict())
    with pytest.raises(TagError):
        root.tex()


def test_tex_nested():
    """Tests the rendering of nested tags in latex."""
    # Generate a nested root tag with sub-tags
    item1 = Tag(name='item', content='item 1', attributes=None,
                context=dict())
    item2 = Tag(name='item', content='item 2', attributes=None,
                context=dict())
    enum = Tag(name='enumerate', content=[item1, item2], attributes=None,
               context=dict())
    elements = ["my first", enum, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=dict())
    assert root.tex() == ('my first\n'
                          '\\begin{enumerate}\n'
                          '\\item item 1\n'
                          '\\item item 2\n'
                          '\\end{enumerate}\n'
                          'string')

    # Test a basic string without additional tags
    p = P(name='p', content='paragraph', attributes=None, context=dict())
    root = Tag(name='root', content=p, attributes=None, context=dict())
    assert root.tex() == '\nparagraph\n'
