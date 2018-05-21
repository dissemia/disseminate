"""
Test string utilities.
"""
from disseminate.utils.string import hashtxt, titlelize


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
