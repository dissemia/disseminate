"""
Test the functionality of macros.
"""
from disseminate.macros import replace_macros, process_context_macros
from disseminate import settings

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

    result = replace_macros(test, context={})

    assert result == expected_result


def test_process_context_macros():
    """Test the process_context macros function."""
    # Test the process_context_macros function
    body_attr = settings.body_attr
    context = {body_attr: test}
    process_context_macros(context)

    assert context[body_attr] == expected_result


def test_macros_specific():
    """Test specific macros."""

    result = replace_macros("90@deg", context={})
    assert result == '90@sup{○}'

    # Try a 2nd time to ensure that the macro isn't replaced again
    result = replace_macros(result, context={})
    assert result == '90@sup{○}'


def test_macros_multiple_substitutions():
    """Test multiple substitutions of macros."""

    context = {'@p90x': '90@deg@sub{x}'}

    result = replace_macros("My @p90x pulse.", context)
    assert result == "My 90@sup{○}@sub{x} pulse."


def test_macros_attributes():
    """Test the replacement of macros and values with attributes."""

    context = {"@feature": "@div[class=col-md-4]"}

    result = replace_macros("My @feature{is good}.", context=context)
    assert result == "My @div[class=col-md-4]{is good}."
