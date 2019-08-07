"""
Tests the CompiledDocument class and methods.
"""
import pathlib

import pytest

from disseminate.document import Document
from disseminate import SourcePath, TargetPath


def test_pdflatex(tmpdir):
    """Tests the compilation of PDFs from tex files."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a src document
    src_path = tmpdir / "src"
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath="index1.dm")

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    This is my first document""")

    # Get the target_filepath for the pdf file
    target_filepath = TargetPath(target_root=tmpdir,
                                 target='pdf',
                                 subpath='index1.pdf')

    # Generate a CompiledDocument for this file
    doc = Document(src_filepath=src_filepath, target_root=tmpdir)

    # Make sure the target PDF hasn't been created yet.
    assert not target_filepath.is_file()

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated
    assert target_filepath.is_file()


def test_pdflatex_caching(tmpdir, wait):
    """Tests the compilation of PDFs from tex files and the caching."""
    tmpdir = pathlib.Path(tmpdir)

    # 1. Test that rendering the document multiple times doesn't create
    # a new pdf
    # Create a src document
    src_path = tmpdir / "src"
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath="index1.dm")

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    This is my first document""")

    # Get the target_filepath for the pdf file
    target_filepath = TargetPath(target_root=tmpdir,
                                 target='pdf',
                                 subpath='index1.pdf')

    # Generate a CompiledDocument for this file
    doc = Document(src_filepath=src_filepath, target_root=tmpdir)

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated and get its mtime
    assert target_filepath.is_file()
    mtime = target_filepath.stat().st_mtime

    # Render again, and the mtime shouldn't change
    doc.render()
    assert target_filepath.stat().st_mtime == mtime

    # Now change the src tex file and make sure the pdf has changed
    wait()  # sleep time offset needed for different mtimes
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    new""")

    # Render again, and the mtime should change
    doc.render()
    assert target_filepath.stat().st_mtime != pytest.approx(mtime, abs=0.00001)


def test_compiled_with_existing_source(tmpdir):
    """A special case of CompiledDocument is when the source file format
    (ex: tex) is already a target for a compiled file format (ex: pdf). This
    tests that pattern. This is possibly buggy since the file is compiled in
    a separate test directory.
    """
    tmpdir = pathlib.Path(tmpdir)

    # Create a src document
    src_path = tmpdir / "src"
    src_path.mkdir()
    src_filepath = SourcePath(project_root=src_path, subpath="index3.dm")

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: tex, pdf
    ---
    This is my third document""")

    # Get the target_filepath for the pdf file

    # Generate a for this file
    doc = Document(src_filepath=src_filepath, target_root=tmpdir)

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated
    assert (tmpdir / 'tex/index3.tex').is_file()
    assert (tmpdir / 'pdf/index3.pdf').is_file()
