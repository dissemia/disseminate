"""
Test string utilities.
"""
from collections import namedtuple

from disseminate.utils.string import (hashtxt, titlelize, strip_end_quotes,
                                      str_to_dict, str_to_list, group_strings,
                                      replace_macros)


def test_hashtxt():
    """Test the hashtxt function."""

    assert 'b44117d75a' == hashtxt("My test hash")  # truncate to 10, be default
    assert ('b44117d75a6aaf964ae1f583f39dd417' ==
            hashtxt("My test hash", truncate=None))


def test_titlelize():
    """The the titlelize function."""

    assert "A first title in here" == titlelize("A first title in here")
    assert "A first title in here" == titlelize("A first title in here.")
    assert "A First Title in Here" == titlelize("A first title in here",
                                                capitalize=True)
    assert "My first title" == titlelize("My first title. Two lines")
    assert "My first title over two lines" == titlelize("My first title over\n"
                                                        "two lines. And two "
                                                        "sentences.")
    assert "Heading 4.1.3" == titlelize("Heading 4.1.3. The heading.")
    assert "Heading 4.1.3" == titlelize("Heading 4.1.3.\nThe heading.")
    assert "My sentence" == titlelize("My sentence.  Double space sentence")
    assert "My sentence" == titlelize("My sentence.\n\n  Double space sentence")
    assert ("My First SubSection, and it "
            "has multiple lines") == titlelize("My First SubSection, and"
                                               "      it has multiple lines.")


def test_strip_end_quotes():
    """Test the strip_end_quotes function."""

    # Basic tests
    assert (strip_end_quotes("'This is my test string '") ==
            'This is my test string ')
    assert (strip_end_quotes('"This is my test string "') ==
            'This is my test string ')
    assert (strip_end_quotes("""'"This is my test string "'""") ==
            '"This is my test string "')
    assert (strip_end_quotes('''"'This is my test string '"''') ==
            "'This is my test string '")
    assert (strip_end_quotes('"This is my test string" ') ==
            'This is my test string ')

    # Try escaped strings
    assert (strip_end_quotes("\'This is my test string \'") ==
            "This is my test string ")
    assert (strip_end_quotes(r"'This is my test string '") ==
            r"This is my test string ")
    assert (strip_end_quotes(r"\'This is my test string \'") ==
            r"\'This is my test string \'")
    assert (strip_end_quotes("''This is my test string ''") ==
            "'This is my test string '")
    assert (strip_end_quotes('""This is my test string ""') ==
            '"This is my test string "')

    # Multi-line
    assert (strip_end_quotes("'This is my test string '\n'second line'") ==
            'This is my test string \nsecond line')
    assert (strip_end_quotes("  'one'\n  'two'\n  'three'") ==
            "  one\n  two\n  three")


def test_str_to_list():
    """Tests the parsing of strings into lists."""

    # Test new lines
    l = str_to_list('  src/file1.tex\n  src/file2.tex\n  src/file 3.tex')
    assert l == ['src/file1.tex', 'src/file2.tex', 'src/file 3.tex']

    # Test commas
    l = str_to_list('src/file1.tex,  src/file2.tex,  src/file 3.tex')
    assert l == ['src/file1.tex', 'src/file2.tex', 'src/file 3.tex']

    # Test semicolons
    l = str_to_list('src/file1.tex;  src/file2.tex;  src/file 3.tex')
    assert l == ['src/file1.tex', 'src/file2.tex', 'src/file 3.tex']

    # Test semicolons with commas
    l = str_to_list('Lorieau, J;  Author, B;  Author, C')
    assert l == ['Lorieau, J', 'Author, B', 'Author, C']


def test_str_to_dict():
    """Tests the parsing of strings into dicts."""

    # Test simple 1-liners
    assert str_to_dict("""entry: one""") == {'entry': 'one'}
    assert str_to_dict("""entry: 1""") == {'entry': '1'}

    # Test simple multiple entries
    assert (str_to_dict("entry: one\ntest:two")
                            == {'entry': 'one', 'test': 'two'})
    assert (str_to_dict("entry: one\n@macro:two") ==
            {'entry': 'one', '@macro': 'two'})

    # Test macro entries
    assert (str_to_dict('@feature: @div[class="col-md-4" id=4]') ==
            {'@feature': '@div[class="col-md-4" id=4]'})

    # Entries with tags
    assert (str_to_dict("toc: @toc{all documents}") ==
            {'toc': '@toc{all documents}'})
    assert (str_to_dict("toc: @toc{all \n"
                             "documents}") ==
            {'toc': '@toc{all \ndocuments}'})
    assert (str_to_dict("""toc: @toc{all
                             documents}""") ==
            {'toc': '@toc{all\n                             documents}'})

    # Nested entries
    header = """
    contact:
      address: 1,2,3 lane
      phone: 333-333-4123.
    name: Justin L Lorieau
    """
    d = str_to_dict(header)
    assert (d == {'contact': '  address: 1,2,3 lane\n  phone: 333-333-4123.',
                  'name': 'Justin L Lorieau'})

    # Entries with colons
    assert (str_to_dict("toc: name: Justin Lorieau") ==
            {'toc': 'name: Justin Lorieau'})
    assert (str_to_dict("""toc: name: Justin Lorieau
    Phone: xxx-yyy-zzz""") ==
            {'toc': 'name: Justin Lorieau\n    Phone: xxx-yyy-zzz'})

    # Include entries
    header = """
    include:
      src/file1.tex
      src/file2.tex
      src/file 3.tex
    """
    d = str_to_dict(header)
    assert (d == {'include':
                  '  src/file1.tex\n  src/file2.tex\n  src/file 3.tex'})

    # Target entries
    header = "targets: pdf, tex"
    d = str_to_dict(header)
    assert (d == {'targets': 'pdf, tex'})
    l = str_to_list(d['targets'])
    assert l == ['pdf', 'tex']


def test_str_to_dict_with_quotes():
    """Tests the parsing of strings into dicts including quotes."""

    # Basic entries
    header = """
    title: 'my title '
    author: This is 'my' name
    """
    d = str_to_dict(header, strip_quotes=True)
    assert (d == {'title': 'my title ', 'author': "This is 'my' name"})

    # Include entries
    header = """
    include:
      "src/file1.tex"
      "src/file2.tex"
      "src/file 3.tex"
    """
    d = str_to_dict(header, strip_quotes=True)
    assert (d == {'include':
                  '  src/file1.tex\n  src/file2.tex\n  src/file 3.tex'})


def test_group_strings():
    """Test the group_strings function."""

    # Try simple flat lists
    assert group_strings(['a', 'b', 5, 'c', 'd']) == ['ab', 5, 'cd']
    assert group_strings([1, 2, 3, 4]) == [1, 2, 3, 4]

    # Try nested lists
    assert (group_strings(['a', 'b', [1, 2, 3], 'c', 'd']) ==
            ['ab', [1, 2, 3], 'cd'])
    assert (group_strings(['a', 'b', [1, 'c', 'd'], 'e', 'f']) ==
            ['ab', [1, 'cd'], 'ef'])


def test_replace_macros_basic():
    """Basic tests of the replace_macros function."""

    # Conduct some basic string tests
    assert (replace_macros("This is my @test.", {'@test': 'TEST'}) ==
            'This is my TEST.')
    assert (replace_macros("This is my @missing.", {'@test': 'TEST'}) ==
            'This is my @missing.')

    # Try missing attributes
    assert (replace_macros("This is my @missing.", {'@test': 'TEST'}) ==
            'This is my @missing.')
    assert (replace_macros("This is my @missing.",
                           {'@test': 'TEST'}, {'@missing': 'MISSING'}) ==
            'This is my MISSING.')
    assert (replace_macros("This is my @missing.",
                           {'@missing': 'TEST'}, {'@missing': 'MISSING'}) ==
            'This is my TEST.')


def test_replace_macros_specific(context_cls):
    """Test replace_macros for specific macros."""

    context = context_cls({'@deg': '@sup{○}'})

    result = replace_macros("90@deg", context)
    assert result == '90@sup{○}'

    # Try a 2nd time to ensure that the macro isn't replaced again
    result = replace_macros(result, context)
    assert result == '90@sup{○}'


def test_replace_macros_multiple_substitutions(context_cls):
    """Test replace_macros with multiple substitutions."""

    context = context_cls({'@p90x': '90@deg@sub{x}',
                           '@deg': '@sup{○}'})

    result = replace_macros("My @p90x pulse.", context)
    assert result == "My 90@sup{○}@sub{x} pulse."


def test_replace_macros_recursive(context_cls):
    """Test replace_macros with recursive references."""

    context = context_cls({'@test': '@test'})

    result = replace_macros("My @@test pulse.", context)
    assert result == "My @@test pulse."


def test_replace_macros_attributes(context_cls):
    """Test replace_macros with attributes."""

    context = context_cls({"@feature": "@div[class=col-md-4]"})

    result = replace_macros("My @feature{is good}.", context)
    assert result == "My @div[class=col-md-4]{is good}."


def test_replace_macros_submatches(context_cls):
    """Test replace_macros with submatches marked by periods."""

    # Create a test object
    class Test(object):
        def __repr__(self):
            return 'TEST'
    test = Test()

    # First try the object itself
    context = context_cls({'@test': test})

    assert (replace_macros("This is my @test.", context) ==
            "This is my TEST.")
    assert (replace_macros("This is my @ test.", context) ==
            "This is my @ test.")

    # Now try with a subattribute
    test.a = 1
    assert (replace_macros("This is my @test.", context) ==
            "This is my TEST.")
    assert (replace_macros("This is my @test.a.", context) ==
            "This is my 1.")
    assert (replace_macros("This is my @test.b.", context) ==
            "This is my TEST.b.")
    assert (replace_macros("This is my @test.@test.", context) ==
            "This is my TEST.TEST.")
    assert (replace_macros("This is my @test@test.", context) ==
            "This is my TESTTEST.")
    assert (replace_macros("This is my @test @test.", context) ==
            "This is my TEST TEST.")

    # Substitutions with named tuples.
    Vector = namedtuple('Vector', 'x y z')
    vec = Vector(x='x', y='y', z='z')
    assert (replace_macros('My @vec.x component.', {'@vec': vec}) ==
            'My x component.')
    assert (replace_macros('My {@vec.y} component.', {'@vec': vec}) ==
            'My {y} component.')
    assert (replace_macros('My @vec component.', {'@vec': vec}) ==
            "My Vector(x='x', y='y', z='z') component.")
