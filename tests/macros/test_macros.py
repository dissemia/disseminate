"""
Test the functionality of macros.
"""
from disseminate.macros import replace_macros


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, an @15N, and a @H2O macro. but this is an email 
    address: justin@lorieau.com

    Here is a new paragraph."""

expected_result = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @marginfig[offset=-1.0em]{
      @img{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @sup{13}C variable, an @sup{15}N, and a H@sub{2}O macro. but this is an email 
    address: justin@lorieau.com

    Here is a new paragraph."""


def test_macros_basic():
    """Basic tests of macros."""

    result = replace_macros(test, local_context={}, global_context={})

    assert result == expected_result


def test_macros_multiple_substitutions():
    """Test multiple substitutions of macros."""

    local_context = {'macros': {'@p90x': '90@deg@sub{x}'}}
    global_context = {}

    result = replace_macros("My @p90x pulse.", local_context=local_context,
                            global_context=global_context)
    assert result == "My 90@symbol{deg}@sub{x} pulse."
