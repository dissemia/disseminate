"""
Converters for ASY files.
"""
import os

from .converter import Converter, convert
from .arguments import PositiveIntArgument, PositiveFloatArgument


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
                '-o', self.target_filepath.value_string]
        self.run(args, raise_error=False)
        return True


class Asy2svg(Converter):
    """Converter for an asy file to an svg file."""

    order = 10100

    from_formats = ('.asy',)
    to_formats = ('.svg',)

    required_execs = ['asy']

    page_no = None
    scale = None

    def __init__(self, src_filepath, target_filepath, page_no=None, scale=None,
                 crop=False, **kwargs):
        super(Asy2svg, self).__init__(src_filepath, target_filepath, **kwargs)

        self.crop = crop
        self.page_no = (PositiveIntArgument('page_no', page_no, required=False)
                        if page_no is not None else None)
        self.scale = (PositiveFloatArgument('scale', scale, required=False)
                      if scale is not None else None)

    def convert(self):
        """Convert an asy file to a pdf file."""
        # Setup a temporary file for the intermediary pdf
        temp_filepath = self.temp_filepath(self.target_filepath)
        temp_basefilepath = os.path.splitext(temp_filepath)[0]

        # Convert asy->pdf
        temp_filepath_pdf = convert(src_filepath=self.src_filepath.value_string,
                                    target_basefilepath=temp_basefilepath,
                                    targets=['.pdf'])
        if temp_filepath_pdf is None:
            return False

        # Convert pdf->svg
        target_filepath = self.target_filepath.value_string
        target_basefilepath = os.path.splitext(target_filepath)[0]

        kwargs = {}
        if self.page_no:
            kwargs['page_no'] = self.page_no
        if self.scale:
            kwargs['scale'] = self.scale
        if self.crop:
            kwargs['crop'] = self.crop

        target_filepath = convert(src_filepath=temp_filepath_pdf,
                                  target_basefilepath=target_basefilepath,
                                  targets=['.svg'],
                                  **kwargs)
        
        if target_filepath is None:
            return False

        return True
