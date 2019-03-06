"""
Tests the core Tag and TagFactory classes.
"""
import pathlib

import pytest

from disseminate.document import Document
from disseminate.ast import process_ast
from disseminate.tags import Tag, TagError
from disseminate.tags.text import P
from disseminate import settings, SourcePath, TargetPath


def test_tag_attributes(context_cls):
    """Test the get and set methods for attributes of tags"""

    context = context_cls()

    tag = Tag(name='tag', content='', attributes=(('class', 'one'),),
              context=context)

    assert tag.attributes == (('class', 'one'),)
    assert tag.get_attribute('class') == 'one'

    tag.set_attribute(('class', 'two'), 'r')

    assert tag.get_attribute('class') == 'two'


def test_flatten_tag(context_cls):
    """Test the flatten method."""
    context = context_cls()

    # Setup a test source string
    test = """
            This is my test document. It has multiple paragraphs.

            Here is a new one with @b{bolded} text as an example.
            @figuretag[offset=-1.0em]{
              @imgtag{media/files}
              @captiontag{This is my @i{first} figure.}
            }

            This is a @13C variable.

            Here is a @i{new} paragraph."""

    # Parse it
    root = process_ast(test, context=context)

    # Convert the root tag to a flattened list and check the items
    flattened_tag = root.flatten(filter_tags=False)

    assert len(flattened_tag) == 20
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
    assert flattened_tag[16].name == '13C'
    assert isinstance(flattened_tag[17], str)
    assert flattened_tag[18].name == 'i'
    assert isinstance(flattened_tag[19], str)

    # Convert the root tag to a flattened list with only tags
    flattened_tag = root.flatten(filter_tags=True)

    assert len(flattened_tag) == 8
    assert flattened_tag[0].name == 'root'
    assert flattened_tag[1].name == 'b'
    assert flattened_tag[2].name == 'figuretag'
    assert flattened_tag[3].name == 'imgtag'
    assert flattened_tag[4].name == 'captiontag'
    assert flattened_tag[5].name == 'i'
    assert flattened_tag[6].name == '13C'
    assert flattened_tag[7].name == 'i'


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
    label_manager = doc.context['label_manager']

    # Get the two documents
    docs = doc.documents_list(only_subdocuments=False, recursive=False)
    assert len(docs) == 2
    doc1, doc2 = docs  # doc1 == doc; doc2 is sub.dm

    # Get the body root tag and the mtimes
    body_attr = settings.body_attr
    root1 = doc1.context[body_attr]
    root2 = doc2.context[body_attr]

    # Check that the mtimes match the file modification times
    assert src_filepath1.mtime() == root1.mtime
    assert src_filepath2.mtime() == root2.mtime

    # Now change the two src files. Add a reference to the 2nd file in the
    # first.
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

    # Reload the documents
    doc1.load()
    doc2.load()

    # Get the root tag and the mtimes
    root1 = doc1.context[body_attr]
    root2 = doc2.context[body_attr]

    # Check that the first file was written before the second.
    assert src_filepath1.mtime() < src_filepath2.mtime()

    # The labels haven't been registered yet, so the root tags should have the
    # same modification time as the files
    assert src_filepath1.mtime() == root1.mtime
    assert src_filepath2.mtime() == root2.mtime

    # Registering the labels with the 'get_labels' method will update the tag
    # mtimes so that root1, which references the 2nd document, gets its mtime,
    # while root2 stays the same
    labels = label_manager.get_labels()
    assert src_filepath2.mtime() == root1.mtime
    assert src_filepath2.mtime() == root2.mtime


def test_label_tags(tmpdir):
    """Test the generation of label tags from the labels of a tag."""
    # Prepare test document
    tmpdir = pathlib.Path(tmpdir)
    src_path = tmpdir / 'src'
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath='test.dm')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath.touch()

    doc = Document(src_filepath, target_root)
    label_manager = doc.context['label_manager']

    # Create a tag and label
    root = Tag(name='root', content='base string', attributes=None,
               context=doc.context)
    root.set_label(id='test', kind='test')

    # Generate the tag for the label. This will raise an exception because
    # the context doesn't have a label_fmt for the kind 'test'
    with pytest.raises(KeyError):
        label_tag = root.get_label_tag()

    # Create a label_fmt for 'test'
    doc.context['label_fmts']['tag_test'] = 'test'
    label_tag = root.get_label_tag()

    assert label_tag.default == 'test'
    assert label_tag.html == '<span class="label">test</span>\n'
    assert label_tag.tex == 'test'

    # Create a label_fmt with formatting for 'test'
    doc.context['label_fmts']['tag_test'] = '@b{test}'
    label_tag = root.get_label_tag()

    assert label_tag.default == 'test'
    assert label_tag.html == ('<span class="label">\n'
                              '  <strong>test</strong>\n'
                              '</span>\n')
    assert label_tag.tex == '\\textbf{test}'

    # Test different label_fmts for different targets. These take priority.
    doc.context['label_fmts']['tag_test_html'] = 'html'
    doc.context['label_fmts']['tag_test_tex'] = 'tex'
    label_tag_html = root.get_label_tag(target='.html')
    label_tag_tex = root.get_label_tag(target='.tex')

    assert label_tag_html.html == '<span class="label">html</span>\n'
    assert label_tag_tex.tex == 'tex'


# Tests for html targets

def test_tag_html(context_cls):
    """Test the conversion of tags to html strings."""

    context = context_cls()

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               context=context)
    assert root.html == '<span class="root">base string</span>\n'

    # Generate a nested root tag with sub-tags
    b = Tag(name='b', content='bolded', attributes=None, context=context)
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=context)
    assert root.html == ('<span class="root">'
                         'my first<b>bolded</b>string'
                         '</span>\n')

    # Test the rendering of a tag with content for an invalid type.
    # This should raise an exception
    root = Tag(name='root', content=set(), attributes=None, context=context)
    with pytest.raises(TagError):
        root.html


def test_tag_html_invalid_tag(context_cls):
    """Test the rendering of invalid tags into html."""

    context = context_cls()

    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='eqn', content='my eqn', attributes=None, context=context)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=context)
    assert root.html == ('<span class="root">my first'
                         '<span class=\"eqn\">my eqn</span>'
                         'string</span>\n')


def test_tag_html_excluded_tag(context_cls):
    """Test the rendering of an excluded tag."""

    context = context_cls()

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='my eqn', attributes=None, context=context)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=context)
    assert root.html == ('<span class="root">my first'
                         '<span class=\"script\">my eqn</span>'
                         'string</span>\n')


def test_tag_html_unsafe_tag(context_cls):
    """Test the rendering of an unsafe tag in the string content of a tag."""

    context = context_cls()

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='<script>', attributes=None,
              context=context)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=context)
    assert root.html == ('<span class="root">my first'
                         '<span class=\"script\">&lt;script&gt;</span>'
                         'string</span>\n')


def test_tag_html_nested(context_cls):
    """Nest nested tags with html"""

    context = context_cls()

    # Test a basic string without additional tags
    p = P(name='p', content='paragraph', attributes=None, context=context)
    root = Tag(name='root', content=p, attributes=None, context=context)
    assert root.html == ('<span class="root">\n'
                         '  <p>paragraph</p>\n'
                         '</span>\n')


# Tests for tex targets

def test_tag_tex(context_cls):
    """Tests the rendering of latex tags."""

    context = context_cls()

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               context=context)
    assert root.tex == "base string"

    # Generate a nested root tag with sub-tags
    b = Tag(name='textbf', content='bolded', attributes=None,
            context=context)
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=context)
    assert root.tex == "my first\\textbf{bolded}string"

    # Test the rendering of a tag with content for an invalid type.
    # This should raise an exception
    root = Tag(name='root', content=set(), attributes=None,
               context=context)
    with pytest.raises(TagError):
        root.tex


def test_tag_tex_nested(context_cls):
    """Tests the rendering of nested tags in latex."""

    context = context_cls()

    # Generate a nested root tag with sub-tags
    item1 = Tag(name='item', content='item 1', attributes=None,
                context=context)
    item2 = Tag(name='item', content='item 2', attributes=None,
                context=context)
    enum = Tag(name='enumerate', content=[item1, item2], attributes=None,
               context=context)
    elements = ["my first", enum, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=context)
    assert root.tex == ('my first\n'
                        '\\begin{enumerate}\n'
                        '\\item item 1\n'
                        '\\item item 2\n'
                        '\\end{enumerate}\n'
                        'string')

    # Test a basic string without additional tags
    p = P(name='p', content='paragraph', attributes=None, context=context)
    root = Tag(name='root', content=p, attributes=None, context=context)
    assert root.tex == '\nparagraph\n'
