"""
Tests the CompiledDocument class and methods.
"""
import pathlib

import pytest

from disseminate.document import Document
from disseminate import SourcePath, TargetPath


def test_pdflatex(env):
    """Tests the compilation of PDFs from tex files."""

    # Create a src document
    doc = env.root_document
    src_filepath = doc.src_filepath

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    This is my first document""")

    # reload the file
    doc.load()

    # Make sure the target PDF hasn't been created yet.
    assert not doc.targets['.pdf'].is_file()

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated
    assert doc.targets['.pdf'].is_file()


def test_pdflatex_caching(env, wait):
    """Tests the compilation of PDFs from tex files and the caching."""

    # 1. Test that rendering the document multiple times doesn't create
    # a new pdf
    doc = env.root_document
    src_filepath = doc.src_filepath

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: pdf
    ---
    This is my first document""")

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated and get its mtime
    target_filepath = doc.targets['.pdf']
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


def test_compiled_with_existing_source(env):
    """A special case of CompiledDocument is when the source file format
    (ex: tex) is already a target for a compiled file format (ex: pdf). This
    tests that pattern. This is possibly buggy since the file is compiled in
    a separate test directory.
    """

    # Create a src document
    doc = env.root_document
    src_filepath = doc.src_filepath

    # Save text and create a new file
    src_filepath.write_text("""
    ---
    targets: tex, pdf
    ---
    This is my third document""")

    # Render the document
    doc.render()

    # See if the tex and pdf files were succesfully generated
    tex_filepath = TargetPath(target_root=env.target_root, target='tex',
                              subpath=src_filepath.name).use_suffix('.tex')
    assert tex_filepath.is_file()
    pdf_filepath = TargetPath(target_root=env.target_root, target='pdf',
                              subpath=src_filepath.name).use_suffix('.pdf')
    assert pdf_filepath.is_file()
