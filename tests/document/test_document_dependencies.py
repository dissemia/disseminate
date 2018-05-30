"""
Test the dependency manager with documents.
"""
import pytest
from shutil import copyfile

from disseminate.document import Document
from disseminate.utils.tests import strip_leading_space
from disseminate.dependency_manager import MissingDependency


def test_dependencies_img(tmpdir):
    """Tests that the image dependencies are correctly reset when the AST is
    reprocessed."""
    # Setup the project_root in a temp directory
    project_root = tmpdir.join('src')
    project_root.mkdir()
    target_root = str(tmpdir)

    # Copy a dependency image file to this directory
    img_path = str(project_root.join('sample.png'))
    copyfile('tests/document/example3/sample.png',
             img_path)

    # Make a document source file
    markup = """
    ---
    targets: html
    ---
    @img{sample.png}
    """

    src_filepath = project_root.join('test.dm')
    src_filepath.write(strip_leading_space(markup))

    # Create a document
    doc = Document(str(src_filepath), tmpdir)

    # Check that the document and dependency manager paths are correct
    assert doc.project_root == str(project_root)
    assert doc.target_root == str(target_root)

    dep = doc.context['dependency_manager']
    assert dep.project_root == str(project_root)
    assert dep.target_root == str(target_root)

    # Render the document
    doc.render()

    # The img file should be a dependency in the '.html' target
    d = dep.get_dependency(target='.html', src_filepath=img_path)
    assert d.dep_filepath == 'sample.png'

    # Rewrite the document source file without the dependency
    markup = ""
    src_filepath.write(markup)

    # Render the document and the dependency should have been removed.
    doc.render()

    # A missing dependency raises a MissingDependency exception
    with pytest.raises(MissingDependency):
        d = dep.get_dependency(target='.html', src_filepath=img_path)
