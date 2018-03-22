"""
Test the yaml_header functions.
"""
from disseminate.header import load_yaml_header


def test_yaml_header():
    """Tests the correct parsing of a header."""

    test_header = """
    ---
    title: My first title
    author: Justin L Lorieau
    ---
"""

    test = """
        This is my test document. It has multiple paragraphs.

        Here is a new one with @b{bolded} text as an example.
        @marginfig[offset=-1.0em]{
          @img{media/files}
          @caption{This is my @i{first} figure.}
        }

        This is a @13C variable, but this is an email address: 
        justin@lorieau.com

        Here is a new paragraph.
    """

    combined_test = test_header + test
    context = {}

    # Process the header
    processed_string = load_yaml_header(combined_test, context)

    # Check the contents  of the local_context
    assert 'title' in context
    assert context['title'] == 'My first title'

    assert 'author' in context
    assert context['author'] == 'Justin L Lorieau'

    # Check the correct rendering of the AST html
    assert processed_string == test


def test_yaml_nonyaml():
    """Test the parsing of a yaml header with a non-yaml like block in the
    source."""

    src = """
    ---
    title: yaml header
    ---
    
    ---
    type: non-parsed
    ---
    """

    context = {}

    # Process the header
    processed_string = load_yaml_header(src, context)

    # Check the contents  of the local_context
    assert 'title' in context
    assert context['title'] == 'yaml header'

    assert processed_string == ("    \n"
                                "    ---\n"
                                "    type: non-parsed\n"
                                "    ---\n"
                                "    ")


def test_yaml_macros():
    """Test the parsing of macros in a yaml header."""

    src = """
    ---
    macros:
        "@feature": "@div[class=col-md-4]"
    ---
    """

    # 1. Test a basic macro
    context = {}

    # Process the header
    processed_string = load_yaml_header(src, context)

    # Check the contents of the local_context
    assert 'macros' in context
    assert '@feature' in context['macros']
    assert context['macros']['@feature'] == "@div[class=col-md-4]"

    # 2. Test macros with quotes
    src = """
        ---
        macros:
            "@feature": "@div[class='col-md-4 test']"
        ---
        """

    context = {}

    # Process the header
    processed_string = load_yaml_header(src, context)

    # Check the contents of the local_context
    assert 'macros' in context
    assert '@feature' in context['macros']
    assert context['macros']['@feature'] == "@div[class='col-md-4 test']"
