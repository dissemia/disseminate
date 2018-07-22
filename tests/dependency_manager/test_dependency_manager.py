"""
Test the DependencyManager functionality
"""
import os.path

import pytest

from disseminate.dependency_manager import DependencyManager, MissingDependency

# Get the template path for disseminate
from disseminate import __file__ as root_path
template_path = os.path.join(os.path.split(root_path)[0],
                             'templates')


def test_target_path():
    """Tests the target_path method."""
    target_root = 'tests/dependency_manager/examples1'
    # With segregate_targets
    dep = DependencyManager(project_root='', target_root=target_root)
    assert dep.target_path('html') == target_root + '/html'


def test_search_file(tmpdir):
    """Test the search_file method."""
    # 1. Try finding a file in the disseminate templates directory
    dep = DependencyManager(project_root='', target_root='')
    path = dep.search_file('media/css/default.css')

    # The file should exist, and the media and render paths should be
    # returned
    assert path is not False
    assert path[0] == 'media/css/default.css'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join(template_path,
                                         'media/css/default.css')))

    # 2. Try finding a file in the project root. This path takes precedence
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

    # 3. Try finding a file with a render path.
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

    # 4. Try finding a file in a cache directory.
    # The example4 has a file at '.cache/media/file.txt'
    dep = DependencyManager(project_root='tests/dependency_manager/example4',
                            target_root='tests/dependency_manager/example4')
    path = dep.search_file('media/file.txt')
    assert path is not False
    assert path[0] == 'media/file.txt'
    assert (os.path.abspath(path[1]) ==
            os.path.abspath(os.path.join('tests/dependency_manager/example4/'
                                         '.cache/media/file.txt')))


def test_copy_file(tmpdir):
    """Tests the copy_file method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Copy a file using segregate_targets
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root)

    # Copy the file.
    path = 'tests/dependency_manager/example1/media/css/default.css'
    target_path = dep.copy_file(target='.html',
                                dep_filepath='media/css/default.css',
                                src_filepath=path)
    assert os.path.isfile(target_path)
    assert str(tmpdir.join('html/media/css/default.css')) == target_path


def test_add_file(tmpdir):
    """Tests the add_file method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Setup a dependency manager
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root)

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

    src_filepath = 'tests/dependency_manager/example1/media/css/default.css'
    assert dependency.src_filepath == src_filepath
    assert dependency.target_filepath == tmpdir.join('html/media/css/'
                                                      'default.css')
    assert dependency.dep_filepath == 'media/css/default.css'

    assert (dep.get_dependency('.html',src_filepath).dep_filepath ==
            'media/css/default.css')

    assert os.path.isfile(str(tmpdir.join('html/media/css/default.css')))

    # Now try adding a file that requires a conversion. The example2 directory
    # has a pdf file in 'media/images/sample.pdf'. This file will need to be
    # converted to an .svg file for an .html target.
    dep = DependencyManager(project_root='tests/dependency_manager/example2',
                            target_root=target_root)
    filepath = 'media/images/sample.pdf'
    targets_added = dep.add_file(targets=['.misc', '.html'], path=filepath)

    # Make sure the added file was correctly converted and added to the
    # dependency manager and that it was copied or linked to the right location
    assert targets_added == ['.html', ]
    dependency = list(dep.dependencies['.html'])[0]

    src_filepath = 'tests/dependency_manager/example2/media/images/sample.pdf'
    assert dependency.src_filepath == src_filepath
    assert dependency.target_filepath == (target_root +
                                          '/html/media/images/sample.svg')
    assert dependency.dep_filepath == 'media/images/sample.svg'

    assert (dep.get_dependency('.html', src_filepath).dep_filepath ==
            'media/images/sample.svg')

    assert os.path.isfile(target_root + '/html/media/images/sample.svg')

    # Try adding a dependency for missing files
    with pytest.raises(MissingDependency):
        targets_added = dep.add_file(targets=['.misc', '.html'],
                                     path='missing.pdf')

    with pytest.raises(MissingDependency):
        targets_added = dep.add_file(targets=['.misc', '.html'],
                                     path='missing.invalid')


def test_reset(tmpdir):
    """Test the reset method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Setup a dependency manager
    dep = DependencyManager(project_root='tests/dependency_manager/example3',
                            target_root=target_root)

    # Add a file for a target with a sample document_src_filepath. The
    # dependency is a '.png' file that works for .tex and .html targets
    filepath = 'tests/dependency_manager/example3/sample.png'
    targets_added = dep.add_file(targets=['.html', '.tex'], path=filepath,
                                 document_src_filepath="src/sample.dm")

    # Make sure the added file was correctly added
    assert len(dep.dependencies['.html']) == 1
    dependency = list(dep.dependencies['.html'])[0]
    assert dependency.document_src_filepath == "src/sample.dm"
    assert len(dep.dependencies['.tex']) == 1
    dependency = list(dep.dependencies['.tex'])[0]
    assert dependency.document_src_filepath == "src/sample.dm"

    # Try resetting a mismatched document_src_filepath. This doesn't remove
    # the dependencies
    dep.reset(document_src_filepath='src/mismatch.dm')
    assert len(dep.dependencies['.html']) == 1
    assert len(dep.dependencies['.tex']) == 1

    # Try resetting the correct document_src_filepath. This removes the
    # dependencies and target, since the target has no dependencies
    dep.reset(document_src_filepath='src/sample.dm')
    assert '.html' not in dep.dependencies
    assert '.tex' not in dep.dependencies


def test_add_file_duplicates(tmpdir):
    """Tests the add_file method when adding a file twice."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Setup a dependency manager
    dep = DependencyManager(project_root='tests/dependency_manager/example1',
                            target_root=target_root)

    # Try adding a file twice
    filepath = 'tests/dependency_manager/example1/media/css/default.css'
    targets_added = dep.add_file(targets=['.html'], path=filepath)
    targets_added = dep.add_file(targets=['.html'], path=filepath)

    # The number of dependencies should be 1, not 2. This is guaranteed because
    # the DependencyManager uses sets.
    assert len(dep.dependencies['.html']) == 1


def test_add_html(tmpdir):
    """Tests the add_html method."""
    # get a temporary target_root
    target_root = str(tmpdir)

    # Setup the dependency manager
    dep = DependencyManager(project_root='', target_root=target_root)

    # 1. Now try adding the 'template.html' file from the project. This file
    #    has a dependency on the 'media/css/default.css' file.
    dep.add_html(template_path + '/template_files/template.html')

    # Make sure the dependency was added and that it exists
    assert len(dep.dependencies) == 1
    dependency = list(dep.dependencies['.html'])[0]

    assert dependency.src_filepath == os.path.realpath(template_path +
                                                       '/media/css/default.css')
    assert dependency.target_filepath == (target_root +
                                          '/html/media/css/default.css')
    assert dependency.dep_filepath == 'media/css/default.css'

    assert os.path.isfile(target_root + '/html/media/css/default.css')

    # 2. Now try adding the 'tree.html' file from the project. This has a css
    #    file, the same as 'template.html', and a link to a font, which should
    #    not be added.
    dep.add_html(template_path + '/template_files/tree.html')
    assert len(dep.dependencies) == 1
