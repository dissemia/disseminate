"""
Tests the CompiledDocument class and methods.
"""
import os.path

import pytest

from disseminate.document import CompiledDocument
from disseminate.convert import ConverterError


def test_pdflatex(tmpdir):
    """Tests the compilation of PDFs from tex files."""

    # Create a src document
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index1.dm")

    # Save text and create a new file
    f1.write("This is my first document")

    # Get the target_filepath for the pdf file
    target_filepath = str(src_path) + '/index1.pdf'

    # Generate a CompiledDocument for this file
    doc = CompiledDocument(src_filepath=str(f1),
                           targets={'.pdf': target_filepath})

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated
    assert os.path.exists(target_filepath)


def test_pdflatex_caching(tmpdir):
    """Tests the compilation of PDFs from tex files and the caching."""
    # Test that rendering it again doesn't create a new pdf
    # Create a src document
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index1.dm")

    # Save text and create a new file
    f1.write("This is my first document")

    # Get the target_filepath for the pdf file
    target_filepath = str(src_path) + '/index1.pdf'

    # Generate a CompiledDocument for this file
    doc = CompiledDocument(src_filepath=str(f1),
                           targets={'.pdf': target_filepath})

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated and get its mtime
    assert os.path.exists(target_filepath)
    mtime = os.path.getmtime(target_filepath)

    # Render again, and the mtime shouldn't change
    doc.render()
    assert os.path.getmtime(target_filepath) == pytest.approx(mtime, abs=0.0001)

    # Now change the src tex file and make sure the pdf has changed
    f1.write("New")

    # Render again, and the mtime should change
    doc.render()
    assert os.path.getmtime(target_filepath) != pytest.approx(mtime, abs=0.0001)


def test_compiled_with_existing_source(tmpdir):
    """A special case of CompiledDocument is when the source file format
    (ex: tex) is already a target for a compiled file format (ex: pdf). This
    tests that pattern. This is possibly buggy since the file is compiled in
    a separate test directory.
    """
    # Create a src document
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index3.dm")

    # Save text and create a new file
    f1.write("This is my third document")

    # Get the target_filepath for the pdf file

    # Generate a CompiledDocument for this file
    doc = CompiledDocument(src_filepath=str(f1),
                           targets={'.pdf': str(src_path) + '/index3.pdf',
                                    '.tex': str(src_path) + '/index3.tex'})

    # Render the document
    doc.render()

    # See if the PDF was succesfully generated
    assert os.path.exists(str(src_path) + '/index3.tex')
    assert os.path.exists(str(src_path) + '/index3.pdf')
