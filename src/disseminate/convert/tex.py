"""
Converters for TEX files.
"""
import os
from tempfile import mkdtemp

from .converter import Converter


class Pdflatex(Converter):
    """Converter for a tex file to a pdf file."""

    order = 500

    from_formats = ('.tex',)
    to_formats = ('.pdf',)

    required_execs = ['pdflatex', ]

    def convert(self):
        """Convert a tex to a pdf file."""
        pdflatex_exec = self.find_executable('pdflatex')

        # Setup temp directory and setup the path of the created pdf
        temp_dir = mkdtemp()
        filename = os.path.split(self.src_filepath.value_string)[1]
        filename_pdf = os.path.splitext(filename)[0] + '.pdf'
        temp_filepath_pdf = os.path.join(temp_dir, filename_pdf)

        # Setup the command
        args = [pdflatex_exec, "-interaction=nonstopmode",
                "-output-directory="+temp_dir, self.src_filepath.value_string]
        self.run(args, raise_error=True)

        # Copy the processed file to the target
        try:
            os.link(temp_filepath_pdf, self.target_filepath.value_string)
        except FileExistsError:
            os.remove(self.target_filepath.value_string)
            os.link(temp_filepath_pdf, self.target_filepath.value_string)
        return True
