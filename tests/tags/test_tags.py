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


