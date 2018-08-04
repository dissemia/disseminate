"""
Test converters for TEX files.
"""
import pathlib

import pytest

from disseminate.convert import convert, ConverterError
from disseminate import SourcePath, TargetPath


valid_tex = """
\\documentclass{article}
\\begin{document}
test
\\end{document}
"""

invalid_tex = """
\\documentclass{article}
\\begin{baddocument}
test
\\end{baddocument}
"""


def test_pdflatex(tmpdir):
    """Test the tex to pdf converter."""
    tmpdir = pathlib.Path(tmpdir)

    # write an invalid tex file
    invalid_tex_file = SourcePath(project_root=tmpdir, subpath='invalid.tex')
    invalid_tex_file.write_text(invalid_tex)

    # Setup a target_basefilepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.pdf',
                                     subpath='invalid')

    # Try an unavailable: pdf->pdf
    with pytest.raises(ConverterError):
        target_filepath = convert(src_filepath=invalid_tex_file,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.pdf'])
    assert not target_basefilepath.with_suffix('.pdf').is_file()

    # write an valid tex file
    valid_tex_file = SourcePath(tmpdir, 'valid.tex')
    valid_tex_file.write_text(valid_tex)

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, target='.pdf',
                                     subpath='valid')

    # Try a tex->pdf run
    target_filepath = convert(src_filepath=valid_tex_file,
                              target_basefilepath=target_basefilepath,
                              targets=['.pdf'])

    # See if the file was created
    correct_path = TargetPath(target_root=tmpdir, target='.pdf',
                              subpath='valid.pdf')
    assert target_filepath == correct_path
    assert target_filepath.is_file()


def test_pdflatex_bad_tex(tmpdir):
    """Tests the compilation of a PDF from a tex file with an error."""
    tmpdir = pathlib.Path(tmpdir)

    # Create a src document
    src_filepath = SourcePath(project_root=tmpdir / 'src', subpath='index1.tex')
    target_basepath = TargetPath(target_root=tmpdir, subpath='index1')

    # Make the directories for the src_filepath
    src_filepath.parent.mkdir(parents=True, exist_ok=False)

    # Save text and create a new file
    src_filepath.write_text("This is my \\bad{first} document")

    # Get the target_filepath for the pdf file
    target_filepath = target_basepath.with_suffix('.pdf')

    # Render the document. This will raise a CompiledDocumentError
    with pytest.raises(ConverterError) as e:
        convert(src_filepath=src_filepath,
                target_basefilepath=target_basepath,
                targets=['.pdf'])

    assert e.match("index1.tex")  # the intermediary file should be in error
    assert e.value.returncode != 0  # unsuccessful run

    assert "! Undefined control sequence." in e.value.shell_out
    assert "This is my \\bad" in e.value.shell_out


def test_tex2svg(tmpdir):
    """Test the tex to svg converter."""
    tmpdir = pathlib.Path(tmpdir)

    # write an invalid tex file
    invalid_tex_file = SourcePath(project_root=tmpdir, subpath='invalid.tex')
    invalid_tex_file.write_text(invalid_tex)

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, subpath='invalid')

    # Try a tex->svg run. It should fail.
    with pytest.raises(ConverterError):
        target_filepath = convert(src_filepath=invalid_tex_file,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.svg'])

    # write a valid tex file
    valid_tex_file = SourcePath(project_root=tmpdir, subpath='valid.tex')
    valid_tex_file.write_text(valid_tex)

    # Setup a target_filepath
    target_basefilepath = TargetPath(target_root=tmpdir, subpath='valid')

    # Try a tex->svg run
    target_filepath = convert(src_filepath=valid_tex_file,
                              target_basefilepath=target_basefilepath,
                              targets=['.svg'])

    # See if the file was created
    correct_path = TargetPath(target_root=tmpdir, subpath='valid.svg')
    assert target_filepath == correct_path
    assert target_filepath.is_file()

