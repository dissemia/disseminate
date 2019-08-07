"""
Tests the core Tag and TagFactory classes.
"""
import pytest

from disseminate.tags import Tag, TagError
from disseminate.tags.text import P


def test_tag_basic_strings(context_cls):
    """Test the parsing of basic tag strings."""

    context = context_cls()

    # 1. Test tags with empty contents
    root = Tag(name='root', content='@test', attributes='', context=context)
    test = root.content
    assert test.name == 'test'
    assert test.content == ''
    assert test.txt == ''
    assert root.txt == ''
    assert len(root) == 1

    root = Tag(name='root', content='@test{}', attributes='', context=context)
    test = root.content
    assert test.name == 'test'
    assert test.content == ''
    assert test.txt == ''
    assert root.txt == ''
    assert len(root) == 1

    root = Tag(name='root', content=' empty ', attributes='', context=context)
    assert isinstance(root.content, str)
    assert root.content == ' empty '

    # 2. Test tags with nested curly braces
    test1 = "This is my @marginfig{{Margin figure}}."
    root = Tag(name='root', content=test1, attributes='', context=context)
    assert root.content[0] == 'This is my '
    assert root.content[1].name == 'marginfig'
    assert root.content[1].content == '{Margin figure}'
    assert root.content[2] == '.'


def test_tag_strings(context_cls):
    """Test the creation of tags with standard and nested strings."""

    context = context_cls()

    # 1. Use an example string with nested tags
    test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfigtag[offset=-1.0em]{
      @imgtag{media/files}
      @captiontag{This is my @i{first} figure.}
    }

    This is a @13C variable.

    Here is a new paragraph."""

    root = Tag(name='root', content=test, attributes='', context=context)

    assert isinstance(root, Tag) and root.name == 'root'  # root tag

    assert isinstance(root[0], str)
    assert root[0] == ('\n    '
                       'This is my test document. It has multiple paragraphs.'
                       '\n\n    '
                       'Here is a new one with ')

    assert isinstance(root[1], Tag) and root[1].name == 'b'

    assert isinstance(root[2], str)  # string

    assert isinstance(root[3], Tag) and root[3].name == 'marginfigtag'
    assert isinstance(root[3].content, list)  # margin tag has subtags

    assert isinstance(root[3][0], str)  # string

    assert isinstance(root[3][1], Tag) and root[3][1].name == 'imgtag'
    assert root[3][1].content == 'media/files'

    assert isinstance(root[3][2], str)  # string

    assert isinstance(root[3][3], Tag) and root[3][3].name == 'captiontag'
    assert isinstance(root[3][3].content, list)  # contents includes
    # strings and tags

    assert isinstance(root[3][3][0], str)  # string

    assert isinstance(root[3][3][1], Tag) and root[3][3][1].name == 'i'
    assert root[3][3][1].content == "first"  # i contents

    assert isinstance(root[3][3][2], str)  # string

    assert isinstance(root[4], str)  # string
    assert root[4] == '\n\n    This is a '

    assert isinstance(root[5], Tag) and root[5].name == '13C'
    assert root[5].content == ''

    assert isinstance(root[6], str)  # string
    assert root[6] == ' variable.\n\n    Here is a new paragraph.'

    assert len(root) == 7


def test_tag_attributes(context_cls):
    """Test the get and set methods for attributes of tags"""

    context = context_cls()

    tag = Tag(name='tag', content='', attributes='class=one', context=context)

    assert tag.attributes == {'class': 'one'}
    assert tag.attributes['class'] == 'one'

    tag.attributes['class'] = 'two'
    assert tag.attributes.get('class') == 'two'


def test_tag_double_convert(context_cls):
    """Tests the default conversion run twice of a tag to make sure the
    Tag stays the same."""

    context = context_cls()

    # 1. Use an example string with nested tags
    test = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @captiontag{This is my @i{first} figure.}
        }

        This is a @13C variable.

        Here is a new paragraph."""

    # Generate the txt string
    root = Tag(name='root', content=test, attributes='', context=context)
    txt = root.default

    # Generate the txt string
    root2 = Tag(name='root', content=root, attributes='', context=context)
    txt2 = root2.default
    assert txt == txt2


def test_tag_invalid_inputs(context_cls):
    """Test the identification of invalid inputs in creating tags."""

    context = context_cls()

    # 1. Test open braces
    test_invalid = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfigtag[offset=-1.0em]{
          @imgtag{media/files}
          @caption{This is my @i{first} figure.}
    """
    with pytest.raises(TagError):
        Tag(name='root', content=test_invalid, attributes='', context=context)

    # 2. Test invalid content types
    with pytest.raises(TagError):
        root = Tag(name='root', content=set(), attributes=None, context=context)


def test_tag_processors(context_cls):
    """Test the tag processor functions."""

    # Create a mock tag
    context = context_cls()
    root = Tag(name='root', content='test', attributes='', context=context)

    # Retrieve the processors
    processors = root.processors()
    assert len(processors) > 0

    # Retrieve specific processors
    for name, cls_name in (('process_content', 'ProcessContent'),
                           ('process_paragraphs', 'ProcessParagraphs'),
                           ('process_macros', 'ProcessMacros'),
                           ('process_typography', 'ProcessTypography'),
                           ):
        processors = root.processors(names=name)
        assert len(processors) == 1

        processor = processors[0]
        assert processor.__class__.__name__ == cls_name

        # Try the class/instance attributes in filtering
        setattr(root, name, False)
        root.process_context = False
        assert (cls_name not in
                [p.__class__.__name__ for p in root.processors()])

        setattr(root, name, True)
        assert (cls_name in
                [p.__class__.__name__ for p in root.processors()])


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
    root = Tag(name='root', content=test, attributes='', context=context)

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


# Test for the default target

def test_tag_default(context_cls):
    """Test the conversion of tags to a default string."""

    context = context_cls()

    # 1. Use an example string with nested tags
    test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfigtag[offset=-1.0em]{
      @imgtag{media/files}
      @captiontag{This is my @i{first} figure.}
    }

    This is a @13C variable.

    Here is a new paragraph."""

    root = Tag(name='root', content=test, attributes='', context=context)

    key = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with bolded text as an example.
    
      media/files
      This is my first figure.
    

    This is a  variable.

    Here is a new paragraph."""

    assert root.txt == key


# Tests for html targets

def test_tag_html(context_cls):
    """Test the conversion of tags to html strings."""

    context = context_cls()

    # 1. Generate a simple root tag with a string as content
    root = Tag(name='root', content='base string', attributes=None,
               context=context)
    assert root.html == '<span class="root">base string</span>\n'

    # Generate a nested root tag with sub-tags
    b = Tag(name='b', content='bolded', attributes=None, context=context)
    b.html_name = 'strong'
    elements = ["my first", b, "string"]
    root = Tag(name='root', content=elements, attributes=None, context=context)
    assert root.html == ('<span class="root">'
                         'my first<strong>bolded</strong>string'
                         '</span>\n')


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

    # 1. The <script> tag is excluded in settings.html_excluded
    # Generate a simple root tag with an invalid tag in its content
    eqn = Tag(name='script', content='<script>', attributes=None,
              context=context)
    elements = ["my first", eqn, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=context)
    assert root.html == ('<span class="root">my first'
                         '<span class=\"script\">&lt;script&gt;</span>'
                         'string</span>\n')

    # 2. Test a body tag with html comments. These should be escaped.
    body = Tag(name='body', content='<!-- My escaped text -->', attributes=None,
               context=context)
    assert body.html == ('<span class="body">'
                         '&lt;!&#8211;My escaped text&#8211;&gt;'
                         '</span>\n')



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
    content = "my first @b{bolded} string"
    root = Tag(name='root', content=content, attributes=None,
               context=context)
    assert root.tex == "my first \\textbf{bolded} string"


def test_tag_tex_nested(context_cls):
    """Tests the rendering of nested tags in latex."""

    context = context_cls()

    # Generate a nested root tag with sub-tags
    item1 = Tag(name='bold', content='item 1', attributes=None,
                context=context)
    item1.tex_cmd = 'textbf'
    enum = Tag(name='enumerate', content=[item1], attributes=None,
               context=context)
    enum.tex_env = 'enumerate'
    elements = ["my first", enum, "string"]
    root = Tag(name='root', content=elements, attributes=None,
               context=context)
    assert root.tex == ('my first\n'
                        '\\begin{enumerate}\n'
                        '\\textbf{item 1}\n'
                        '\\end{enumerate}\n'
                        'string')

    # Test a basic string without additional tags
    p = P(name='p', content='paragraph', attributes=None, context=context)
    root = Tag(name='root', content=p, attributes=None, context=context)
    assert root.tex == '\nparagraph\n'
