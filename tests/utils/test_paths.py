"""
Tests for Paths objects.
"""

from disseminate.utils.paths import SourcePath, TargetPath


def test_path_seggregation():
    """Test the seggregation of parts for a path."""

    src_path = SourcePath('src', 'main.dm')
    assert str(src_path) == 'src/main.dm'
    assert src_path.project_root == 'src'
    assert src_path.subpath == 'main.dm'

    tgt_path = TargetPath(target_root='target',
                          target='.html',
                          subpath='sub1/file.jpg')
    assert str(tgt_path) == 'target/html/sub1/file.jpg'
    assert tgt_path.target_root == 'target'
    assert tgt_path.target == 'html'
    assert tgt_path.subpath == 'sub1/file.jpg'


def test_path_immutability():
    """Tests whether the new path objects can be used as keys."""
    src_path = SourcePath('src', 'main.dm')

    # Test a dict
    d = {src_path: 'test'}
    assert d[src_path] == 'test'

    # Test a tuple
    a = (1, src_path, 3)
    assert a == (1, src_path, 3)


def test_path_filesystem(tmpdir):
    """Tests the filesystem behavior of the new path objects."""
    src_path = SourcePath(tmpdir.join('src'), 'main.dm')

    # Create missing sub-directories
    subdir = src_path.parent
    subdir.mkdir(parents=True, exist_ok=True)

    assert subdir.is_dir()
    assert not subdir.is_file()

    # Test file existence and creation
    assert not src_path.exists()
    assert not src_path.is_file()

    src_path.touch()
    assert src_path.exists()
    assert src_path.is_file()
