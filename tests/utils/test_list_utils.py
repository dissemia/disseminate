"""
Test the list utilities.
"""
import pathlib

from disseminate.utils.list import md5hash


def test_md5hash(tmpdir):
    """Test the md5hash function"""
    tmpdir = pathlib.Path(tmpdir)

    # 1. Try a binary file
    test = tmpdir / 'test.bin'
    test.write_bytes(b'test')

    assert md5hash([test.read_bytes()]) == '27d99a0b1f43deed64c2a2030aa4337b'
