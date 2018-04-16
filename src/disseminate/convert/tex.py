"""
Converters for TEX files.
"""
import os
from tempfile import mkdtemp

from .converter import Converter, convert
from .arguments import PathArgument
from ..utils.file import parents
from .pdf import Pdf2svg


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

        # Setup the environment. This will list the source tex directory and all
        # parent directories in the TEXINPUTS path
        texinputs = ':'.join(parents(self.src_filepath.value_string))
        env = {'TEXINPUTS': ":" + texinputs}

        # Setup the command and run in
        args = [pdflatex_exec, "-interaction=nonstopmode",
                "-output-directory="+temp_dir, self.src_filepath.value_string]

        # Run twice
        for i in range(2):
            self.run(args, env=env, raise_error=True)

        # Copy the processed file to the target
        try:
            os.link(temp_filepath_pdf, self.target_filepath())
        except FileExistsError:
            os.remove(self.target_filepath())
            os.link(temp_filepath_pdf, self.target_filepath())
        return True


class Tex2svg(Pdf2svg):
    """Converter for a tex file to an svg file."""

    order = 600

    from_formats = ('.tex',)
    to_formats = ('.svg',)

    page_no = None
    scale = None

    def convert(self):
        """Convert an asy file to a pdf file."""

        # Setup a temporary file for the intermediary pdf
        temp_filepath = self.temp_filepath()
        temp_basefilepath = os.path.splitext(temp_filepath)[0]
        src_filepath = self.src_filepath.value_string

        # Convert Tex->pdf
        target_filepath = convert(src_filepath=src_filepath,
                                  target_basefilepath=temp_basefilepath,
                                  targets=[".pdf"])

        if target_filepath is None:
            return False

        # Now the target of tex->pdf is the source for this file
        self.src_filepath = PathArgument('src_filepath',
                                         target_filepath,
                                         required=True)

        return super(Tex2svg, self).convert()
