"""
Converters for ASY files.
"""
import os

from .converter import Converter
from .pdf import Pdf2svg
from .arguments import PathArgument


class Asy2pdf(Converter):
    """Converter for an asy file to a pdf file."""

    order = 10000

    from_formats = ('.asy',)
    to_formats = ('.pdf',)

    required_execs = ['asy', ]

    def convert(self):
        """Convert an asy file to a pdf file."""
        asy_exec = self.find_executable('asy')

        # Convert the file to pdf
        # asy -pdf infile.asy -o outfile.pdf
        args = [asy_exec, '-f', 'pdf', self.src_filepath.value_string,
                '-o', self.target_filepath()]
        self.run(args, raise_error=True)
        return True


class Asy2svg(Pdf2svg):
    """Converter for an asy file to an svg file."""

    order = 10100

    from_formats = ('.asy',)
    to_formats = ('.svg',)

    required_execs = ['asy']

    page_no = None
    scale = None

    def __init__(self, src_filepath, target_basefilepath, page_no=None,
                 scale=None, crop=False, **kwargs):
        super(Asy2svg, self).__init__(src_filepath, target_basefilepath,
                                      page_no, scale, crop, **kwargs)

    def convert(self):
        """Convert an asy file to a pdf file."""

        # Setup a temporary file for the intermediary pdf
        temp_filepath = self.temp_filepath()
        temp_basefilepath = os.path.splitext(temp_filepath)[0]
        src_filepath = self.src_filepath.value_string

        # Convert asy->pdf
        ast2pdf = Asy2pdf(src_filepath=src_filepath,
                          target_basefilepath=temp_basefilepath,
                          target='.pdf')
        success = ast2pdf.convert()
        if success is None:
            return False

        # Now the target of ast2pdf is the source for this file
        self.src_filepath = PathArgument('src_filepath',
                                         ast2pdf.target_filepath(),
                                         required=True)

        return super(Asy2svg, self).convert()
