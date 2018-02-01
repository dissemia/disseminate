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
    """Tests the link files method"""

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
    dep.link_files(target_root=str(tmpdir), segregate_targets=True)

    # Check to make sure the file is correctly linked
    src_file_path = [v for v in dep.dependencies['.html'].values()
                     if v.endswith('default.css')][0]
    new_file_path = os.path.join(tmpdir, 'html/media/css/default.css')
    assert os.path.isfile(new_file_path)  # file exists
    assert (os.stat(new_file_path).st_ino ==
            os.stat(src_file_path).st_ino)
