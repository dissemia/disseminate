"""
Tests for Paths objects.
"""
import copy

from disseminate.paths import SourcePath, TargetPath


def test_path_seggregation():
    """Test the seggregation of parts for a path."""

    src_path = SourcePath('src', 'main.dm')
    assert str(src_path) == 'src/main.dm'
    assert isinstance(src_path.project_root, SourcePath)
    assert str(src_path.project_root) == 'src'
    assert isinstance(src_path.subpath, SourcePath)
    assert str(src_path.subpath) == 'main.dm'

    tgt_path = TargetPath(target_root='target',
                          target='.html',
                          subpath='sub1/file.jpg')
    assert str(tgt_path) == 'target/html/sub1/file.jpg'
    assert isinstance(tgt_path.target_root, TargetPath)
    assert str(tgt_path.target_root) == 'target'
    assert isinstance(tgt_path.target, TargetPath)
    assert str(tgt_path.target) == 'html'
    assert isinstance(tgt_path.subpath, TargetPath)
    assert str(tgt_path.subpath) == 'sub1/file.jpg'


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


def test_path_empty_attributes():
    """Test the behavior of the ProjectPath and TargetPath with empty optional
    arguments."""
    src_path = SourcePath(project_root='src')
    assert str(src_path) == 'src'
    assert str(src_path.project_root) == 'src'
    assert src_path.subpath == SourcePath('.')

    tgt_path = TargetPath(target_root='tgt', target='html')
    assert str(tgt_path) == 'tgt/html'
    assert str(tgt_path.target_root) == 'tgt'
    assert str(tgt_path.target) == 'html'
    assert tgt_path.subpath == TargetPath('.')


def test_path_target_get_url():
    """Test the get_url method for TargetPath objects."""
    # Default
    tgt_path = TargetPath(target_root='tgt', target='html')
    assert tgt_path.get_url() == '/html'

    tgt_path = TargetPath(target_root='tgt')
    assert tgt_path.get_url() == ''

    tgt_path = TargetPath(target_root='tgt', subpath='sub1/main.jpg')
    assert tgt_path.get_url() == '/sub1/main.jpg'

    tgt_path = TargetPath(target_root='tgt', target='.html')
    assert tgt_path.get_url() == '/html'

    # Custom
    context = {'base_url': 'https://app.disseminate.press/{target}/{subpath}'}
    tgt_path = TargetPath(target_root='tgt', target='html', subpath='test.html')
    key = 'https://app.disseminate.press/html/test.html'
    assert tgt_path.get_url(context) == key

    tgt_path = TargetPath(target_root='tgt', subpath='test.html')
    key = 'https://app.disseminate.press/test.html'
    assert tgt_path.get_url(context) == key

    tgt_path = TargetPath(target_root='tgt')
    key = 'https://app.disseminate.press'
    assert tgt_path.get_url(context) == key


def test_path_types():
    """Test the behavior of the Path classes."""
    src_path = SourcePath(project_root='src')
    assert isinstance(src_path, SourcePath)

    tgt_path = TargetPath(target_root='tgt', target='html')
    assert isinstance(tgt_path, TargetPath)

    # Test the equivalence of paths
    assert SourcePath(project_root='src') == SourcePath(project_root='src')
    assert SourcePath(project_root='src2') != SourcePath(project_root='src')


def test_path_repr():
    """Test the repr of Path classes."""
    src_path = SourcePath(project_root='src')
    assert repr(src_path) == "SourcePath('src')"


def test_path_copy():
    """Tests shallow and deep copy of Path classes."""
    # test SourcePath
    for project_root, subpath in (('.', None),
                                  ('test', 'test.dm')):
        src_filepath = SourcePath(project_root=project_root, subpath=subpath)
        shallow_copy = copy.copy(src_filepath)
        deep_copy = copy.deepcopy(src_filepath)

        assert src_filepath == shallow_copy
        assert src_filepath.project_root == shallow_copy.project_root
        assert src_filepath.subpath == shallow_copy.subpath

        assert src_filepath == deep_copy
        assert src_filepath.project_root == deep_copy.project_root
        assert src_filepath.subpath == deep_copy.subpath

    # test TargetPath
    for target_root, target, subpath in (('.', None, None),
                                         ('test', None, 'test.dm'),
                                         ('test', '.html', 'tester.dm')):
        tgt_filepath = TargetPath(target_root=target_root, target=target,
                                  subpath=subpath)
        shallow_copy = copy.copy(tgt_filepath)
        deep_copy = copy.deepcopy(tgt_filepath)

        assert tgt_filepath == shallow_copy
        assert tgt_filepath.target_root == shallow_copy.target_root
        assert tgt_filepath.target == shallow_copy.target
        assert tgt_filepath.subpath == shallow_copy.subpath

        assert tgt_filepath == deep_copy
        assert tgt_filepath.target_root == deep_copy.target_root
        assert tgt_filepath.target == deep_copy.target
        assert tgt_filepath.subpath == deep_copy.subpath
