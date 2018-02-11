"""
Test the DependencyManager functionality
"""
import os.path

from disseminate.dependency_manager import DependencyManager

# Get the template path for disseminate
from disseminate.templates import __file__ as template_path
template_path = os.path.split(template_path)[0]


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
    print("path:", path)
    assert path is not False
    assert path[0] == 'media/css/default.css'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join('tests/dependency_manager/example1',
                                         'media/css/default.css')))
