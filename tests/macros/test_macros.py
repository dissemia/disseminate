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


def test_macros_basic(context_cls):
    """Basic tests of macros."""

    context = context_cls({'13C': '@sup{13}C',
                           '15N': '@sup{15}N',
                           'H2O': 'H@sub{2}O'})

    result = replace_macros(test, context=context)
    assert result == expected_result


def test_process_context_macros(context_cls):
    """Test the process_context macros function."""

    body_attr = settings.body_attr
    context = context_cls({body_attr: test,
                           '13C': '@sup{13}C',
                           '15N': '@sup{15}N',
                           'H2O': 'H@sub{2}O'})

    process_context_macros(context)
    assert context[body_attr] == expected_result


def test_macros_specific(context_cls):
    """Test specific macros."""

    context = context_cls({'deg': '@sup{○}'})

    result = replace_macros("90@deg", context=context)
    assert result == '90@sup{○}'

    # Try a 2nd time to ensure that the macro isn't replaced again
    result = replace_macros(result, context=context)
    assert result == '90@sup{○}'


def test_macros_multiple_substitutions(context_cls):
    """Test multiple substitutions of macros."""

    context = context_cls({'p90x': '90@deg@sub{x}',
                           'deg': '@sup{○}'})

    result = replace_macros("My @p90x pulse.", context)
    assert result == "My 90@sup{○}@sub{x} pulse."


def test_macros_recursive(context_cls):
    """Test substitution of macros with recursive references."""

    context = context_cls({'test': '@test'})

    result = replace_macros("My @@test pulse.", context)
    assert result == "My @@test pulse."


def test_macros_attributes(context_cls):
    """Test the replacement of macros and values with attributes."""

    context = context_cls({"feature": "@div[class=col-md-4]"})

    result = replace_macros("My @feature{is good}.", context=context)
    assert result == "My @div[class=col-md-4]{is good}."
