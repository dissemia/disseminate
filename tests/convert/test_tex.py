"""
Test converters for TEX files.
"""
import os

import pytest

from disseminate.convert import convert, ConverterError


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

    # write an invalid tex file
    invalid_tex_file = tmpdir.join('invalid.tex')
    invalid_tex_file.write(invalid_tex)

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('invalid')

    # Try an unavailable: pdf->pdf
    with pytest.raises(ConverterError):
        target_filepath = convert(src_filepath=str(invalid_tex_file),
                                  target_basefilepath=str(target_basefilepath),
                                  targets=['.pdf'])
    assert not os.path.isfile(str(target_basefilepath) + '.pdf')

    # write an invalid tex file
    valid_tex_file = tmpdir.join('valid.tex')
    valid_tex_file.write(valid_tex)

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('valid')

    # Try a tex->pdf run
    target_filepath = convert(src_filepath=str(valid_tex_file),
                              target_basefilepath=str(target_basefilepath),
                              targets=['.pdf'])

    # See if the file was created
    assert target_filepath == str(tmpdir.join('valid.pdf'))
    assert tmpdir.join('valid.pdf').check()


def test_tex2svg(tmpdir):
    """Test the tex to svg converter."""

    # write an invalid tex file
    invalid_tex_file = tmpdir.join('invalid.tex')
    invalid_tex_file.write(invalid_tex)

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('invalid')

    # Try a tex->svg run. It should fail.
    with pytest.raises(ConverterError):
        target_filepath = convert(src_filepath=str(invalid_tex_file),
                                  target_basefilepath=str(target_basefilepath),
                                  targets=['.svg'])

    # write a valid tex file
    valid_tex_file = tmpdir.join('valid.tex')
    valid_tex_file.write(valid_tex)

    # Setup a target_filepath
    target_basefilepath = tmpdir.join('valid')

    # Try a tex->svg run
    target_filepath = convert(src_filepath=str(valid_tex_file),
                              target_basefilepath=str(target_basefilepath),
                              targets=['.svg'])

    # See if the file was created
    assert target_filepath == str(tmpdir.join('valid.svg'))
    assert tmpdir.join('valid.svg').check()
