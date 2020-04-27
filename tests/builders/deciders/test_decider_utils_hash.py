"""
Test Decider utils for calculating hashes.
"""
import pathlib

from disseminate.builders.deciders.utils_hash import hash_items


def test_hash_items_simple_strings():
    """Test the hash_items function with simple strings."""

    # 1. Test string order
    assert hash_items('one', 'two') == '5b9164ad6f496d9dee12ec7634ce253f'
    assert hash_items('two', 'one') == '66058ec26cd62e957604145e726b0f0b'

    # 2. Test binary strings
    assert hash_items('one', b'two') == '5b9164ad6f496d9dee12ec7634ce253f'


def test_hash_items_txt_files(tmpdir):
    """Test the hash_items function with text files"""
    p1 = pathlib.Path(tmpdir) / 'file1.txt'
    p2 = pathlib.Path(tmpdir) / 'file2.txt'
    p3 = pathlib.Path(tmpdir) / 'file3.txt'

    p1.write_text('one')
    p2.write_text('one')
    p3.write_text('three')

    assert hash_items(p1) == 'f9b4018028d097c99d5827f9fd8a6557'
    assert hash_items(p1, p2) == 'b786b137035ec184992d55013cfd3e0b'
    assert hash_items(p1) == hash_items(p2)
    assert hash_items(p1) != hash_items(p3)
    assert hash_items(p1) != hash_items(p1, p2)


def test_hash_items_pdf_files():
    """Test the hash_items function with pdf files, where metadata is stripped.
    """
    p1 = pathlib.Path('tests/builders/examples/ex9/1.pdf')
    p2 = pathlib.Path('tests/builders/examples/ex9/2.pdf')

    for chunk_size in (8, 16, 64, 128, 4096):  # try different chunk sizes
        assert hash_items(p1, chunk_size=chunk_size) == hash_items(p2)
