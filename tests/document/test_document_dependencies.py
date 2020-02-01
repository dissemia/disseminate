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
    assert deps[0].dep_filepath.match('default/media/css/base.css')
    assert deps[0].dest_filepath.match('html/media/css/base.css')
    assert deps[1].dep_filepath.match('default/media/css/bootstrap.min.css')
    assert deps[1].dest_filepath.match('html/media/css/bootstrap.min.css')
    assert deps[2].dep_filepath.match('default/media/css/default.css')
    assert deps[2].dest_filepath.match('html/media/css/default.css')
    assert deps[3].dep_filepath.match('default/media/css/pygments.css')
    assert deps[3].dest_filepath.match('html/media/css/pygments.css')
    assert deps[4].dep_filepath.match('sample.png')
    assert deps[4].dest_filepath.match('html/sample.png')

    # Rewrite the document source file without the dependency
    wait()  # sleep time offset needed for different mtimes
    markup = ""
    src_filepath.write_text(markup)

    # Render the document and the dependency should have been removed.
    doc.render()

    # The rendered document no longer has a dependency on the image.
    assert len(dep_manager.dependencies[src_filepath]) == 4
    assert dep_manager.dependencies[src_filepath] == set(deps[0:4])


def test_dependencies_multiple_locations(doc_cls, tmpdir):
    """Test the addition of dependencies from multiple locations."""

    # 1. Test example10, which has an image file local to a sub-directory, one
    #    in the root directory and template files
    # tests/document/example10
    # └── src
    #     ├── chapter1
    #     │   ├── figures
    #     │   │   └── local_img.png
    #     │   └── index.dm
    #     ├── index.dm
    #     └── media
    #         └── ch1
    #             └── root_img.png
    # Load the root document and subdocument
    project_root = 'tests/document/example10/src'
    src_filepath = SourcePath(project_root=project_root, subpath='index.dm')
    target_root = TargetPath(target_root=tmpdir)

    doc = doc_cls(src_filepath=src_filepath, target_root=target_root)
    subdoc = doc.documents_list(only_subdocuments=True)[0]

    # Load the dependencies by rendering the root doc
    doc.render()

    dep_manager = doc.context['dependency_manager']

    doc_deps = dep_manager.dependencies[doc.src_filepath]
    subdoc_deps = dep_manager.dependencies[subdoc.src_filepath]

    # make sure the local_img.png and root_img.png are loaded in the subdoc but
    # not the doc. The local_img.png should be in the chapter1/figures directory
    # byt the root_img.png should be in the global media/ch1 directory.
    assert any(dep.dest_filepath.match("html/media/css/base.css")
               for dep in doc_deps)
    assert any(dep.dest_filepath.match("html/media/css/default.css")
               for dep in doc_deps)
    assert not any(dep.dest_filepath.match("tex/media/ch1/root_img.png")
                   for dep in doc_deps)
    assert not any(dep.dest_filepath.match("tex/chapter1/figures/local_img.png")
                   for dep in doc_deps)
    assert not any(dep.dest_filepath.match("html/media/ch1/root_img.png")
                   for dep in doc_deps)
    assert not any(dep.dest_filepath.match("html/chapter1/figures/local_img.png")
                   for dep in doc_deps)

    assert any(dep.dest_filepath.match("html/media/css/base.css")
               for dep in subdoc_deps)
    assert any(dep.dest_filepath.match("html/media/css/default.css")
               for dep in subdoc_deps)
    assert any(dep.dest_filepath.match("tex/media/ch1/root_img.png")
               for dep in subdoc_deps)
    assert any(dep.dest_filepath.match("tex/chapter1/figures/local_img.png")
               for dep in subdoc_deps)
    assert any(dep.dest_filepath.match("html/media/ch1/root_img.png")
               for dep in subdoc_deps)
    assert any(dep.dest_filepath.match("html/chapter1/figures/local_img.png")
               for dep in subdoc_deps)
