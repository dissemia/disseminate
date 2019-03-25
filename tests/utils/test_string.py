"""
Test string utilities.
"""
from disseminate.utils.string import (hashtxt, titlelize, str_to_dict,
                                      str_to_list)


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
    Phone\: xxx-yyy-zzz""") ==
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
