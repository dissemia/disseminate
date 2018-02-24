"""
Converters for PDF files.
"""
import os

from .converter import Converter
from .arguments import PositiveIntArgument, PositiveFloatArgument


class Pdf2svg(Converter):
    """Converter for a PDF file to an SVG file."""

    order = 100

    from_formats = ('.pdf',)
    to_formats = ('.svg',)

    required_execs = ['pdf2svg', ]
    optional_execs = ['pdfcrop', 'rsvg-convert']

    page_no = None
    scale = None

    def __init__(self, src_filepath, target_basefilepath, page_no=None,
                 scale=None, crop=False, **kwargs):
        super(Pdf2svg, self).__init__(src_filepath, target_basefilepath,
                                      **kwargs)

        self.crop = crop
        if isinstance(page_no, PositiveIntArgument):
            self.page_no = page_no
        else:
            self.page_no = (PositiveIntArgument('page_no', page_no,
                                                required=False)
                            if page_no is not None else None)
        if isinstance(scale, PositiveFloatArgument):
            self.scale = scale
        else:
            self.scale = (PositiveFloatArgument('scale', scale, required=False)
                          if scale is not None else None)

    def target_filepath(self):
        target_basefilepath = self.target_basefilepath.value_string
        if self.crop:
            target_basefilepath += '_crop'
        if self.page_no is not None:
            target_basefilepath += '_pg' + str(self.page_no.value_string)
        if self.scale is not None:
            scale = round(float(self.scale.value_string), 0)
            target_basefilepath += '_scale{:.1f}'.format(scale)
        return target_basefilepath + self.target

    def convert(self):
        """Convert a pdf to an svg file."""
        pdfcrop_exec = self.find_executable('pdfcrop')
        pdf2svg_exec = self.find_executable('pdf2svg')
        rsvg_exec = self.find_executable('rsvg-convert')

        # Setup temp file. The returned file path is a .svg; get the .pdf and
        # .svg temp filepaths
        temp_filepath_svg = self.temp_filepath()
        temp_filepath_svg2 = os.path.splitext(temp_filepath_svg)[0] + '2.svg'
        temp_filepath_pdf = os.path.splitext(temp_filepath_svg)[0] + '.pdf'
        current_pdf = self.src_filepath.value_string
        current_svg = temp_filepath_svg

        # Crop the pdf, if specified
        if self.crop and pdfcrop_exec:
            # pdfcrop infile.pdf outfile.pdf
            args = [pdfcrop_exec, current_pdf, temp_filepath_pdf]
            self.run(args, raise_error=False)

            # Move the current pdf
            current_pdf = temp_filepath_pdf

        # Convert the file to svg
        # pdf2svg infile.pdf outfile.svg [page_no]
        args = [pdf2svg_exec, current_pdf, current_svg]
        if self.page_no is not None:
            args += self.page_no.value_string
        self.run(args, raise_error=True)

        if self.scale and pdfcrop_exec:
            # rsvg-convert -z {scale} -f svg -o {target_filepath}
            args = [rsvg_exec, "-z", self.scale.value_string,
                    "-f", "svg", "-o", temp_filepath_svg2, current_svg]
            self.run(args, raise_error=False)

            current_svg = temp_filepath_svg2

        # Copy the processed file to the target
        try:
            os.link(current_svg, self.target_filepath())
        except FileExistsError:
            os.remove(self.target_filepath())
            os.link(temp_filepath_svg, self.target_filepath())
        return True
