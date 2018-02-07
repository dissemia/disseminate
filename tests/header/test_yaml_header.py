"""
Test the yaml_header functions.
"""
from disseminate.header import load_yaml_header


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

    This is a @13C variable, but this is an email address: justin@lorieau.com

    Here is a new paragraph.
"""


def test_yaml_header():
    """Tests the correct parsing of a header."""

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
