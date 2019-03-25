"""
Test the functionality of macros.
"""
from collections import namedtuple

from disseminate.macros import replace_macros, process_context_macros
from disseminate.ast import process_context_asts
from disseminate.paths import SourcePath
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

expected_result_txt = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with bolded text as an example.
    
      
      
    This is my first figure.

    This is a 13C variable, an 15N, and a H2O macro. but this is an email 
    address: justin.com

    Here is a new paragraph."""


def test_macros_basic(context_cls):
    """Basic tests of macros."""

    context = context_cls({'@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O'})

    result = replace_macros(test, context=context)
    assert result == expected_result

    # Conduct some basic string tests
    assert (replace_macros("This is my @test.", context={'@test': 'TEST'}) ==
            'This is my TEST.')
    assert (replace_macros("This is my @missing.", context={'@test': 'TEST'}) ==
            'This is my @missing.')


def test_macros_specific(context_cls):
    """Test specific macros."""

    context = context_cls({'@deg': '@sup{○}'})

    result = replace_macros("90@deg", context=context)
    assert result == '90@sup{○}'

    # Try a 2nd time to ensure that the macro isn't replaced again
    result = replace_macros(result, context=context)
    assert result == '90@sup{○}'


def test_macros_multiple_substitutions(context_cls):
    """Test multiple substitutions of macros."""

    context = context_cls({'@p90x': '90@deg@sub{x}',
                           '@deg': '@sup{○}'})

    result = replace_macros("My @p90x pulse.", context)
    assert result == "My 90@sup{○}@sub{x} pulse."


def test_macros_recursive(context_cls):
    """Test substitution of macros with recursive references."""

    context = context_cls({'@test': '@test'})

    result = replace_macros("My @@test pulse.", context)
    assert result == "My @@test pulse."


def test_macros_attributes(context_cls):
    """Test the replacement of macros and values with attributes."""

    context = context_cls({"@feature": "@div[class=col-md-4]"})

    result = replace_macros("My @feature{is good}.", context=context)
    assert result == "My @div[class=col-md-4]{is good}."


def test_macros_submatches(context_cls):
    """Test the replacement of macros with submatches marked by periods."""

    # Create a test object
    class Test(object):
        def __repr__(self):
            return 'TEST'
    test = Test()

    # First try the object itself
    context = context_cls({'@test': test})

    assert (replace_macros("This is my @test.", context=context) ==
            "This is my TEST.")
    assert (replace_macros("This is my @ test.", context=context) ==
            "This is my @ test.")

    # Now try with a subattribute
    test.a = 1
    assert (replace_macros("This is my @test.", context=context) ==
            "This is my TEST.")
    assert (replace_macros("This is my @test.a.", context=context) ==
            "This is my 1.")
    assert (replace_macros("This is my @test.b.", context=context) ==
            "This is my TEST.b.")
    assert (replace_macros("This is my @test.@test.", context=context) ==
            "This is my TEST.TEST.")
    assert (replace_macros("This is my @test@test.", context=context) ==
            "This is my TESTTEST.")
    assert (replace_macros("This is my @test @test.", context=context) ==
            "This is my TEST TEST.")

    # Substitutions with named tuples.
    Vector = namedtuple('Vector', 'x y z')
    vec = Vector(x='x', y='y', z='z')
    assert (replace_macros('My @vec.x component.', context={'@vec': vec}) ==
            'My x component.')
    assert (replace_macros('My {@vec.y} component.', context={'@vec': vec}) ==
            'My {y} component.')
    assert (replace_macros('My @vec component.', context={'@vec': vec}) ==
            "My Vector(x='x', y='y', z='z') component.")


def test_process_context_macros(context_cls):
    """Test the process_context_macros function."""

    # 1. Test a reference example
    body_attr = settings.body_attr
    context = context_cls({body_attr: test,
                           '@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O'})

    process_context_macros(context)
    assert context[body_attr] == expected_result

    # 2. Try running it a second time
    process_context_macros(context)
    assert context[body_attr] == expected_result

    # 3. Try multiple substitutions
    test3 = "My @13C nucleus is the @13C isotope."
    context = context_cls({body_attr: test3,
                           '@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O'})
    process_context_macros(context)
    assert context[body_attr] == ('My @sup{13}C nucleus is the @sup{13}C '
                                  'isotope.')


def test_process_context_macros_with_process_context_asts(context_cls):
    """Test the process_context_macros function in conjunction with the
    process_context_asts function."""

    # 1. Test a reference example
    body_attr = settings.body_attr
    context = context_cls({body_attr: test,
                           '@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O',
                           'src_filepath': SourcePath('.'),
                           })

    process_context_macros(context)
    process_context_asts(context)
    assert context[body_attr].txt == expected_result_txt

    # 2. Try it a second time. The macros are already substituted.
    context[body_attr] = test
    process_context_macros(context)
    process_context_asts(context)
    assert context[body_attr].txt == expected_result_txt

    # 3. Now try it again after resetting the context to make sure it works.
    context.reset()
    context[body_attr] = test
    process_context_macros(context)
    process_context_asts(context)
    assert context[body_attr].txt == expected_result_txt
