"""
Tests the Dependencies classes and functions.
"""
import os.path

import pytest

import disseminate
from disseminate.dependencies import Dependencies, DependencyError
from disseminate.templates import get_template


def test_add_html():
    """Tests the add_html method."""
    # Create a dependencies object
    dep = Dependencies()

    # Render an html string from a template. This template should have a
    # dependency on /css/default.css
    t = get_template("template", target='.html')
    html = t.render(body="")

    # Find the css/default.css dependency. We'll start by looking in the
    # template's directory
    dep.add_html(html, path=t.filename)

    # Get the module's directory
    module_root = disseminate.__path__[0]

    assert '/media/css/default.css' in dep.dependencies['.html']
    assert (dep.dependencies['.html']['/media/css/default.css'] ==
            os.path.join(module_root, 'templates/media/css/default.css'))


def test_add_html_local(tmpdir):
    """Tests add_html with a css file in the project directory."""
    # Load a template for examples1
    # The examples1 directory has an index.dm file, a template.html file
    # and a custom css, default.css, in media
    path = 'tests/dependencies/examples1'
    t = get_template(path + '/index.dm', '.html')
    html = t.render()

    # Create the dependencies object
    dep = Dependencies()
    dep.add_html(html, t.filename)

    # Check that the local file was added
    assert '.html' in dep.dependencies
    assert '/media/default.css' in dep.dependencies['.html']
    assert (dep.dependencies['.html']['/media/default.css'] ==
            'tests/dependencies/examples1/media/default.css')


def test_add_html_missing():
    """Tests the add_html method with a missing file"""
    # Create a dependencies object
    dep = Dependencies()

    # Generate an html string with an invalid file
    html = """
    <html>
    <head>
      <link rel="stylesheet" href="/css/missing.css">
    </head>
    <body>
    </body>
    </html>  
    """

    with pytest.raises(DependencyError):
        dep.add_html(html, path='.')


def test_link_files(tmpdir):
    """Tests the translate_files method"""

    # Create a dependencies object
    dep = Dependencies()

    # Render an html string from a template. This template should have a
    # dependency on /css/default.css
    t = get_template("template", target='.html')
    html = t.render(body="")

    # Find the css/default.css dependency. We'll start by looking in the
    # template's directory
    dep.add_html(html, path=t.filename)

    # Link files to a temporary directory
    dep.translate_files(target_root=str(tmpdir), segregate_targets=True)

    # Check to make sure the file is correctly linked
    src_file_path = [v for v in dep.dependencies['.html'].values()
                     if v.endswith('default.css')][0]
    new_file_path = os.path.join(tmpdir, 'html/media/css/default.css')
    assert os.path.isfile(new_file_path)  # file exists
    assert (os.stat(new_file_path).st_ino ==
            os.stat(src_file_path).st_ino)


def test_clean(tmpdir):
    """Tests the clean method"""

    # Create a dependencies object
    dep = Dependencies(target_root=str(tmpdir), segregate_targets=True)

    # Render an html string from a template. This template should have a
    # dependency on /css/default.css
    t = get_template("template", target='.html')
    html = t.render(body="")

    # Find the css/default.css dependency. We'll start by looking in the
    # template's directory
    dep.add_html(html, path=t.filename)

    # Link files to a temporary directory
    dep.translate_files()

    # Clean files. the default.css file should still be present, since it is
    # tracketd
    dep.clean()

    new_file_path = os.path.join(tmpdir, 'html/media/css/default.css')
    assert os.path.isfile(new_file_path)  # file exists

    # Now untrack the default.css, and it should be removed
    dep.dependencies['.html'] = {}
    dep.clean()

    assert not os.path.isfile(new_file_path)  # file does not exist


def test_local_dependency(tmpdir):
    """The the addition of a dependency in the local (project) directory"""
