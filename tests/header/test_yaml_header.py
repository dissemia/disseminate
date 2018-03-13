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
    local_context = {}
    global_context = {}

    # Process the header
    processed_string = load_yaml_header(combined_test, local_context,
                                        global_context)

    # Check the contents  of the local_context
    assert 'title' in local_context
    assert local_context['title'] == 'My first title'

    assert 'author' in local_context
    assert local_context['author'] == 'Justin L Lorieau'

    # The global_context should have nothing in it
    assert len(global_context) == 0

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

    local_context = {}
    global_context = {}

    # Process the header
    processed_string = load_yaml_header(src, local_context,
                                        global_context)

    # Check the contents  of the local_context
    assert 'title' in local_context
    assert local_context['title'] == 'yaml header'

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
    local_context = {}
    global_context = {}

    # Process the header
    processed_string = load_yaml_header(src, local_context,
                                        global_context)

    # Check the contents of the local_context
    assert 'macros' in local_context
    assert '@feature' in local_context['macros']
    assert local_context['macros']['@feature'] == "@div[class=col-md-4]"

    # 2. Test macros with quotes
    src = """
        ---
        macros:
            "@feature": "@div[class='col-md-4 test']"
        ---
        """

    local_context = {}
    global_context = {}

    # Process the header
    processed_string = load_yaml_header(src, local_context,
                                        global_context)

    # Check the contents of the local_context
    assert 'macros' in local_context
    assert '@feature' in local_context['macros']
    assert local_context['macros']['@feature'] == "@div[class='col-md-4 test']"
