"""
Test the DependencyManager functionality
"""
import os.path
import pathlib

import pytest

from disseminate.dependency_manager import (DependencyManager,
                                            FileDependency)
from disseminate import SourcePath, TargetPath

# Get the template path for disseminate
from disseminate import __file__ as root_path
template_path = pathlib.Path(pathlib.Path(root_path).parent, 'templates')


def test_file_dependency_get_url(context_cls):
    """Test the get_url method of FileDependency objects."""

    context = context_cls(base_url='')

    dep = FileDependency(dep_filepath=SourcePath(project_root='',
                                                 subpath=''),
                         dest_filepath=TargetPath(target_root='',
                                                  target='.pdf',
                                                  subpath='test.pdf'))

    # Empty base_url gives an empty url
    assert dep.get_url(context) == ''

    # A base_url with just a subpath
    context['base_url'] = '{subpath}'
    assert dep.get_url(context) == 'test.pdf'

    context['base_url'] = '{target}/{subpath}'
    assert dep.get_url(context) == 'pdf/test.pdf'

    context['base_url'] = '/{target}/{subpath}'
    assert dep.get_url(context) == '/pdf/test.pdf'

    context['base_url'] = 'https://www.test.com/{target}/{subpath}'
    assert dep.get_url(context) == 'https://www.test.com/pdf/test.pdf'


def test_dependency_manager_copy_file(tmpdir, context_cls):
    """Tests the _copy_file method."""
    tmpdir = pathlib.Path(tmpdir)

    # setup the paths
    project_root = SourcePath(project_root='tests/dependency_manager/example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Create the dependency manager
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Check that the file hasn't been copied yet
    correct_path = TargetPath(target_root=tmpdir,
                              target='.html',
                              subpath='media/css/default.css')
    assert not correct_path.is_file()

    # Copy the file.
    dep_filepath = SourcePath(project_root='tests/dependency_manager/example1',
                              subpath='media/css/default.css')

    deps = dep_manager.add_dependency(dep_filepath=dep_filepath, target='.html',
                                     context=context)

    # Check the copied file
    assert len(deps) == 1
    dep = deps.pop()
    assert dep_filepath == dep.dep_filepath
    assert correct_path == dep.dest_filepath
    assert correct_path.is_file()

    # Make sure the dependencies dict was properly populated
    assert src_filepath in dep_manager.dependencies
    assert dep_manager.dependencies[src_filepath] == {dep}


def test_dependency_manager_duplicates(tmpdir, context_cls):
    """Tests the add of duplicate files."""
    tmpdir = pathlib.Path(tmpdir)

    # setup the paths
    project_root = SourcePath(project_root='tests/dependency_manager/example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Create the dependency manager
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Copy the file.
    dep_filepath = SourcePath(project_root='tests/dependency_manager/example1',
                              subpath='media/css/default.css')

    deps = dep_manager.add_dependency(dep_filepath=dep_filepath, target='.html',
                                      context=context)
    deps = dep_manager.add_dependency(dep_filepath=dep_filepath, target='.html',
                                      context=context)

    # There should only be 1 dependency in the dependency manager
    assert len(dep_manager.dependencies[src_filepath]) == 1


def test_dependency_manager_missing(tmpdir, context_cls):
    """Test the dependency manager with a missing source file."""
    tmpdir = pathlib.Path(tmpdir)

    # setup the paths
    project_root = SourcePath(project_root='tests/dependency_manager/example1')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Copy a file using segregate_targets
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Try to create the dependency
    dep_filepath = SourcePath(project_root='tests/dependency_manager/example1',
                              subpath='media/css/missing')

    with pytest.raises(FileNotFoundError):
        deps = dep_manager.add_dependency(dep_filepath=dep_filepath,
                                          target='.html',
                                          context=context)


def test_dependency_manager_convert_file(tmpdir, context_cls):
    """Tests the _convert_file method."""
    # Test the converstion of pdf->svg for an .html target

    tmpdir = pathlib.Path(tmpdir)

    # setup the paths
    project_root = SourcePath(project_root='tests/dependency_manager/example2')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Copy a file using segregate_targets
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Check that the file hasn't been converted yet
    correct_path = TargetPath(target_root=tmpdir,
                              target='.html',
                              subpath='media/images/sample.svg')
    assert not correct_path.is_file()

    # Convert the file.
    dep_filepath = SourcePath(project_root=project_root,
                              subpath='media/images/sample.pdf')

    deps = dep_manager.add_dependency(dep_filepath=dep_filepath,
                                      target='.html',
                                      context=context)

    # Check the copied file
    assert len(deps) == 1
    dep = deps.pop()
    assert dep_filepath == dep.dep_filepath
    assert correct_path == dep.dest_filepath
    assert correct_path.is_file()

    # Make sure the dependencies dict was properly populated
    assert src_filepath in dep_manager.dependencies
    assert dep_manager.dependencies[src_filepath] == {dep}


def test_dependency_manager_covert_file_reuse(tmpdir, context_cls):
    """Test the reuse of converted files with the dependency manager."""
    # Test the converstion of pdf->svg for an .html target

    tmpdir = pathlib.Path(tmpdir)

    # setup the paths
    project_root = SourcePath(project_root='tests/dependency_manager/example2')
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Copy a file using segregate_targets
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Check that the file hasn't been converted yet
    correct_path = TargetPath(target_root=tmpdir,
                              target='.html',
                              subpath='media/images/sample.svg')
    assert not correct_path.is_file()

    # Convert the file.
    dep_filepath = SourcePath(project_root=project_root,
                              subpath='media/images/sample.pdf')

    deps = dep_manager.add_dependency(dep_filepath=dep_filepath,
                                      target='.html',
                                      context=context)

    # Get the information on the file
    assert len(deps) == 1
    dep = deps.pop()
    mtime = dep.dest_filepath.stat().st_mtime
    ino = dep.dest_filepath.stat().st_ino

    # Try the conversion again and see if the file has changed. (It shouldn't)
    deps = dep_manager.add_dependency(dep_filepath=dep_filepath,
                                     target='.html',
                                     context=context)

    assert len(deps) == 1
    dep = deps.pop()
    assert mtime == dep.dest_filepath.stat().st_mtime
    assert ino == dep.dest_filepath.stat().st_ino

    # Make sure the dependencies dict was properly populated
    assert src_filepath in dep_manager.dependencies
    assert dep_manager.dependencies[src_filepath] == {dep}


def test_dependency_manager_scape_html(tmpdir, context_cls):
    """Test the scrape_html method."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the test html string
    html = """
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="/media/css/default.css">
    </head>
    </html>"""

    # setup the paths
    project_root = SourcePath(project_root=tmpdir)
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths,
                          base_url='/{target}/{subpath}')

    # Setup a file copy using segregate_targets
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # 1. Scrape the html with a missing file. The file is not found because
    # the 'media/css/default.css' file is not in the paths entry of the context
    with pytest.raises(FileNotFoundError):
        html = dep_manager.scrape_html(html=html, target='.html',
                                       context=context)

    # Add the path
    context['paths'].append(pathlib.Path(template_path, 'default'))

    # 2. Scrape the html with a file that can be found.
    html = dep_manager.scrape_html(html=html, target='.html', context=context)

    # Check that the url has been correctly inserted. These should be
    # rewritten for the target directory.
    assert 'href="/media/css/default.css"' not in html
    assert 'href="/html/media/css/default.css"' in html

    # Make sure the dependencies dict was properly populated
    assert src_filepath in dep_manager.dependencies
    assert len(dep_manager.dependencies[src_filepath]) == 1

    # 3. Scrape the html with a url instead of a file. A url doesn't count
    #    as a file dependency, so no file should be added to the dependency
    #    manager.
    dep_manager.dependencies.clear()  # reset dependencies

    html = """
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://www.google.com/default.css">
    </head>
    </html>"""

    html = dep_manager.scrape_html(html=html, target='.html', context=context)
    assert 'href="https://www.google.com/default.css"' in html

    # Make sure the dependencies dict was properly populated
    assert src_filepath not in dep_manager.dependencies


def test_dependency_manager_scape_css(tmpdir, context_cls):
    """Test the scrape_css method."""
    tmpdir = pathlib.Path(tmpdir)

    # Setup the test html string
    css = """
    @import "/media/css/default.css";
    body {
        background-color: lightblue;
    }"""

    # setup the paths
    project_root = SourcePath(project_root=tmpdir)
    target_root = TargetPath(target_root=tmpdir)
    src_filepath = SourcePath(project_root=project_root,
                              subpath='index.dm')

    # Setup the context_cls
    context_cls.validation_types = {'src_filepath': SourcePath,
                                    'paths': list}
    paths = [target_root]
    context = context_cls(src_filepath=src_filepath, paths=paths)

    # Setup a file copy using segregate_targets
    dep_manager = DependencyManager(project_root=project_root,
                                    target_root=target_root)

    # Add the path
    context['paths'].append(pathlib.Path(template_path, 'default'))

    # 2. Scrape the html with a file that can be found.
    css = dep_manager.scrape_css(css=css, target='.html', context=context)

    # Check the dependency's paths. These should be rewritten for the target
    # directory.
    assert '@import "/media/css/default.css";' not in css
    assert '@import "/html/media/css/default.css";' in css

    # Check the dependencies
    deps = dep_manager.dependencies[src_filepath]
    assert len(deps) == 1
    dep = deps.pop()
    assert (dep.dep_filepath ==
            SourcePath(project_root=template_path,
                       subpath='default/media/css/default.css'))
    assert (dep.dest_filepath ==
            TargetPath(target_root=tmpdir,
                       target='html',
                       subpath='media/css/default.css'))

    # 3. Scrape the html with a url instead of a file. A url doesn't count
    #    as a file dependency, so no file should be added to the dependency
    #    manager.
    dep_manager.dependencies.clear()  # reset dependencies

    css = """
    @import "https://google.com/default.css";
    body {
        background-color: lightblue;
    }"""

    css = dep_manager.scrape_css(css=css, target='.html', context=context)

    # Check that the paths remain unchanged
    assert '@import "https://google.com/default.css"' in css

    # Check that no dependencies were created
    assert src_filepath not in dep_manager.dependencies


# def test_dependency_manager_convert_file_attributes():
#     raise NotImplementedError
#
#
# def test_dependency_manager_unsupported_filetype():
#     raise NotImplementedError
#
#
# def test_dependency_manager_template_override(tmpdir, context_cls):
#     """Test copying of template files and overriding them with files in the
#     project directory."""
