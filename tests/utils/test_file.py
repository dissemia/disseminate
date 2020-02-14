"""
Test file utilities
"""
import pathlib

import pytest

from disseminate.utils.file import link_or_copy


def test_link_or_copy(tmpdir):
    """Test the link_or_copy function"""
    tmpdir = pathlib.Path(tmpdir)
    src = tmpdir / "source_file.txt"
    dst = tmpdir / "destination_file.txt"

    # 1. Try an example with no source file. A FileNotFoundError is raised.
    assert not src.exists()  # Not created yet
    assert not dst.exists()  # Not created yet
    with pytest.raises(FileNotFoundError):
        link_or_copy(src, dst)

    # Create the source file
    src.write_text('Initial')

    # 2. Copy the destination file
    assert not dst.exists()  # Not created yet
    link_or_copy(src, dst)

    assert dst.exists()  # Created by link_or_copy
    assert src.read_text() == dst.read_text()

    # 3. Running again doesn't
    dst_inode = dst.stat().st_ino
    link_or_copy(src, dst)
    assert dst_inode == dst.stat().st_ino  # new file not created

    # 4. Try changing the src and link_or_copy should overwrite it
    src.write_text('New')
    link_or_copy(src, dst)

    assert src.read_text() == dst.read_text()
