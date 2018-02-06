"""
Tests the core Tag and TagFactory classes.
"""
from disseminate.tags import Tag


def test_html():
    """Test the conversion of tags to html strings."""

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               local_context=None, global_context=None)
    assert root.html() == "<body>base string</body>\n"

    # Generate a nested root tag with sub-tags
    b = Tag(name='b', content='bolded', attributes=None,
            local_context="bolded", global_context=None)
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.html() == "<body>my first<b>bolded</b>string</body>\n"


def test_html_invalid_tag():
    """Test the rendering of invalid tags into html."""

    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='eqn', content='my eqn', attributes=None,
              local_context=None, global_context=None)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.html() == ("<body>my first"
                           "<span class=\"eqn\">my eqn</span>"
                           "string</body>\n")


def test_html_excluded_tag():
    """Test the rendering of an excluded tag."""

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='my eqn', attributes=None,
              local_context=None, global_context=None)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.html() == ("<body>my first"
                           "<span class=\"script\">my eqn</span>"
                           "string</body>\n")


def test_html_unsafe_tag():
    """Test the rendering of an unsafe tag in the string content of a tag."""

    # The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='<script>', attributes=None,
              local_context=None, global_context=None)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.html() == ("<body>my first"
                           "<span class=\"script\">&lt;script&gt;</span>"
                           "string</body>\n")


def test_tex():
    """Tests the rendering of latex tags."""

    # Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               local_context=None, global_context=None)
    assert root.tex() == "base string"

    # Generate a nested root tag with sub-tags
    b = Tag(name='textbf', content='bolded', attributes=None,
            local_context="bolded", global_context=None)
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.tex() == "my first\\textbf{bolded}string"


def test_tex_nested():
    """Tests the rendering of nested tags in latex."""
    # Generate a nested root tag with sub-tags
    item1 = Tag(name='item', content='item 1', attributes=None,
            local_context="bolded", global_context=None)
    item2 = Tag(name='item', content='item 2', attributes=None,
                local_context="bolded", global_context=None)
    enum = Tag(name='enumerate', content=[item1, item2], attributes=None,
               local_context="bolded", global_context=None)
    elements = ["my first", enum, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               local_context=None, global_context=None)
    assert root.tex() == ('my first\n'
                          '\\begin{enumerate}\n'
                          '\\item item 1\n'
                          '\\item item 2\n'
                          '\\end{enumerate}\n'
                          'string')
