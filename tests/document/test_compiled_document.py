"""
Tests the CompiledDocument class and methods.
"""
import os.path

import pytest

from disseminate.document import CompiledDocument, CompiledDocumentError


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

    # Test that rendering it again doesn't create a new pdf


def test_bad_pdflatex(tmpdir):
    """Tests the compilation of a PDF from a tex file with an error."""

    # Create a src document
    src_path = tmpdir.mkdir("src")
    f1 = src_path.join("index1.dm")

    # Save text and create a new file
    f1.write("This is my \\bad{first} document")

    # Get the target_filepath for the pdf file
    target_filepath = str(src_path) + '/index1.pdf'

    # Generate a CompiledDocument for this file
    doc = CompiledDocument(src_filepath=str(f1),
                           targets={'.pdf': target_filepath})

    # Render the document. This will raise a CompiledDocumentError
    with pytest.raises(CompiledDocumentError) as e:
        doc.render()
    assert e.match(target_filepath)
    assert e.value.exit_code != 0  # unsuccessful run
    assert "! Undefined control sequence." in e.value.shell_out
    assert "l.6 This is my \\bad" in e.value.shell_out
