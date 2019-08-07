"""
Test the dependency manager with documents.
"""
import pathlib
from shutil import copyfile

from disseminate.document import Document
from disseminate.utils.tests import strip_leading_space
from disseminate import SourcePath, TargetPath


def test_dependencies_img(tmpdir, wait):
    """Tests that the image dependencies are correctly reset when the AST is
    reprocessed."""
    # Setup the project_root in a temp directory
    project_root = SourcePath(project_root=tmpdir / 'src')
    project_root.mkdir()
    target_root = TargetPath(target_root=tmpdir)

    # Copy a dependency image file to this directory
    img_path = project_root / 'sample.png'
    copyfile(pathlib.Path('tests/document/example3/sample.png'),
             img_path)

    # Make a document source file
    markup = """
    ---
    targets: html
    ---
    @img{sample.png}
    """

    src_filepath = SourcePath(project_root=project_root,
                              subpath='test.dm')
    src_filepath.write_text(strip_leading_space(markup))

    # Create a document
    doc = Document(src_filepath, tmpdir)

    # Get the template renderer
    renderer = doc.context['renderers']['template']

    # Check that the document and dependency manager paths are correct
    assert doc.project_root == project_root
    assert doc.target_root == target_root

    dep_manager = doc.context['dependency_manager']
    assert dep_manager.project_root == project_root
    assert dep_manager.target_root == target_root

    # Render the document
    doc.render()

    # The img file should be a dependency
    deps = list(sorted(dep_manager.dependencies[src_filepath]))
    dep1 = deps[0]
    dep2 = deps[1]
    assert dep1.dep_filepath.match('default/media/css/default.css')
    assert dep1.dest_filepath.match('html/media/css/default.css')
    assert dep2.dep_filepath.match('sample.png')
    assert dep2.dest_filepath.match('html/sample.png')

    # Rewrite the document source file without the dependency
    wait()  # sleep time offset needed for different mtimes
    markup = ""
    src_filepath.write_text(markup)

    # Render the document and the dependency should have been removed.
    doc.render()

    # The rendered document no longer has a dependency on the image.
    assert len(dep_manager.dependencies[src_filepath]) == 1
    assert dep_manager.dependencies[src_filepath] == {dep1}
