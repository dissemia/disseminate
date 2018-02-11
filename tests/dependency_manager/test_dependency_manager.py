"""
Test the DependencyManager functionality
"""
import os.path

from disseminate.dependency_manager import DependencyManager

# Get the template path for disseminate
from disseminate.templates import __file__ as template_path
template_path = os.path.split(template_path)[0]


def test_target_path():
    """Tests the target_path method."""
    target_root = 'tests/dependency_manager/examples1'
    # With segregate_targets
    dep = DependencyManager(project_root='', target_root=target_root,
                            segregate_targets=True)
    assert dep.target_path('html') == target_root + '/html'

    # Without segregate_targets
    dep = DependencyManager(project_root='', target_root=target_root,
                            segregate_targets=False)
    assert dep.target_path('html') == target_root


def test_search_file():
    """Test the search_file method."""
    # Try finding a file in the disseminate templates directory
    dep = DependencyManager(project_root='', target_root='')
    path = dep.search_file('media/css/default.css')

    # The file should exist, and the media and render paths should be
    # returned
    assert path is not False
    assert path[0] == 'media/css/default.css'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join(template_path,
                                         'media/css/default.css')))

    # Try finding a file in the project root. This path takes precedence
    # over the module path. The example1 directory has a default.css file in
    # the media/css directory
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root='')
    path = dep.search_file('media/css/default.css')

    # The file should exist, and the media and render paths should be
    # returned
    assert path is not False
    assert path[0] == 'media/css/default.css'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join('tests/dependency_manager/example1',
                                         'media/css/default.css')))

    # Try finding a file with a render path.
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root='')
    search_path = 'tests/dependency_manager/example1/media/css/default.css'
    path = dep.search_file(search_path)

    # The file should exist, and the media and render paths should be
    # returned
    assert path is not False
    assert path[0] == 'media/css/default.css'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join('tests/dependency_manager/example1',
                                         'media/css/default.css')))


def test_copy_file(tmpdir):
    """Tests the copy_file method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Copy a file using segregate_targets
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root, segregate_targets=True)

    # Copy the file.
    path = 'tests/dependency_manager/example1/media/css/default.css'
    target_path = dep.copy_file(target='.html',
                                media_path='media/css/default.css', path=path)
    assert os.path.isfile(target_path)
    assert str(tmpdir.join('html/media/css/default.css')) == target_path

    # Try again, but this time without segregate_targets
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root, segregate_targets=False)

    # Copy the file.
    path = 'tests/dependency_manager/example1/media/css/default.css'
    target_path = dep.copy_file(target='.html',
                                media_path='media/css/default.css', path=path)
    assert os.path.isfile(target_path)
    assert str(tmpdir.join('media/css/default.css')) == target_path


def test_add_file(tmpdir):
    """Tests the add_file method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Setup a dependency manager
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root, segregate_targets=True)

    # Try adding a file for a target that doesn't support it. The add_file
    # will return False in this case.
    filepath = 'tests/dependency_manager/example1/media/css/default.css'
    targets_added = dep.add_file(targets=['.misc'], path = filepath)

    # The targets_added should be empty in this case.
    assert targets_added == []

    # Now try adding a file for a target that does support it.
    targets_added = dep.add_file(targets=['.misc', '.html'], path=filepath)

    # Make sure the added file was correctly added to the dependency manager
    # and that it was copied or linked to the right location
    assert targets_added == ['.html', ]
    dependency = list(dep.dependencies['.html'])[0]
    assert dependency.media_path == 'media/css/default.css'
    assert dependency.path == ('tests/dependency_manager/example1'
                               '/media/css/default.css')
    assert os.path.isfile(tmpdir.join('html/media/css/default.css'))

    # Now try adding a file that requires a conversion. The example2 directory
    # has a pdf file in 'media/images/sample.pdf'. This file will need to be
    # converted to an .svg file for an .html target.
    dep = DependencyManager(project_root='tests/dependency_manager/example2',
                            target_root=target_root, segregate_targets=True)
    filepath = 'media/images/sample.pdf'
    targets_added = dep.add_file(targets=['.misc', '.html'], path=filepath)

    # Make sure the added file was correctly converted and added to the
    # dependency manager and that it was copied or linked to the right location
    assert targets_added == ['.html', ]
    dependency = list(dep.dependencies['.html'])[0]
    assert dependency.media_path == 'media/images/sample.svg'
    assert dependency.path == (target_root + '/html/media/images/sample.svg')
    assert os.path.isfile(target_root + '/html/media/images/sample.svg')



