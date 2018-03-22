"""
Tests the core Tag and TagFactory classes.
"""
import pytest

from disseminate.tags import Tag, TagError
from disseminate.tags.text import P


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
