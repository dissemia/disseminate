"""
Test the processing of macros in tags
"""

from disseminate.tags import Tag


test = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @myfig[offset=-1.0em]{
      @myimg{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @13C variable, an @15N, and a @H2O macro. but this is an email 
    address: justin@lorieau.com

    Here is a new paragraph."""

expected_result = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with @b{bolded} text as an example.
    @myfig[offset=-1.0em]{
      @myimg{media/files}
      @caption{This is my @i{first} figure.}
    }

    This is a @sup{13}C variable, an @sup{15}N, and a H@sub{2}O macro. but this is an email 
    address: justin@lorieau.com

    Here is a new paragraph."""

expected_result_txt = """
    This is my test document. It has multiple paragraphs.

    Here is a new one with bolded text as an example.
    
      media/files
      This is my first figure.
    

    This is a 13C variable, an 15N, and a H2O macro. but this is an email 
    address: justin.com

    Here is a new paragraph."""


def test_process_macros(context_cls):
    """Test the process_context_macros function."""

    # 1. Test a reference example
    context = context_cls({'@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O'})

    # Process the body tag and check it
    body = Tag(name='body', content=test, attributes='', context=context)
    assert body.txt == expected_result_txt

    # 3. Try multiple substitutions
    test3 = "My @13C nucleus is the @13C isotope."
    context = context_cls({'body': test3,
                           '@13C': '@sup{13}C',
                           '@15N': '@sup{15}N',
                           '@H2O': 'H@sub{2}O'})
    body = Tag(name='body', content=context['body'], attributes='',
               context=context)
    assert body.txt == 'My 13C nucleus is the 13C isotope.'


def test_process_nested_macros_and_tags(context_cls):
    """Test the combination of process_context_tags and process_macros with nested
    macros."""

    test1 = "My @p90x pulse."
    context = context_cls(**{'@p90x': '90@deg@sub{x}',
                             'test': test1,
                             'process_context_tags': ['test']})
    test = Tag(name='root', content=test1, attributes='', context=context)

    assert test.content[0] == 'My 90'
    assert test.content[1].name == 'deg'
    assert test.content[2].name == 'sub'
    assert test.content[3] == ' pulse.'

    assert test.txt == 'My 90x pulse.'


def test_process_recursive_macros_and_tags(context_cls):
    """Tests the application of macros."""

    # 1. Test with a basic macro
    test1 = "This is my @test string."
    context = context_cls(**{'@test': 'substituted',
                             'test': test1})
    tag = Tag(name='root', content=test1, attributes='', context=context)
    assert tag.txt == 'This is my substituted string.'

    # 2. Test with a recursive macro
    test21 = "This is my @test string."
    context = context_cls(**{'@test': 'substituted @test',
                             'test': test21})
    tag = Tag(name='root', content=test21, attributes='', context=context)
    assert tag.txt == 'This is my substituted substituted  string.'
