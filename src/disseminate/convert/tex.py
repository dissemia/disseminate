"""
Converters for TEX files.
"""
import os
import pathlib
from tempfile import mkdtemp

from ..paths import SourcePath, TargetPath
from .converter import Converter, convert
from .arguments import SourcePathArgument
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
        src_filepath = self.src_filepath.value

        # Setup temp directory and setup the path of the created pdf
        temp_dir = pathlib.Path(mkdtemp())
        filename_pdf = src_filepath.with_suffix('.pdf').name
        temp_filepath_pdf = TargetPath(target_root=temp_dir,
                                       subpath=filename_pdf)

        # Setup the environment. This will list the source tex directory and all
        # parent directories in the TEXINPUTS path
        texinputs = ':'.join(str(i) for i in src_filepath.parents)
        env = {'TEXINPUTS': ":" + texinputs}

        # Setup the command and run in
        args = [pdflatex_exec, "-interaction=nonstopmode",
                "-output-directory=" + str(temp_dir),
                str(self.src_filepath.value)]

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
        temp_basefilepath = TargetPath(target_root=temp_filepath.parent,
                                       subpath=temp_filepath.stem)
        src_filepath = self.src_filepath.value

        # Convert Tex->pdf
        target_filepath = convert(src_filepath=src_filepath,
                                  target_basefilepath=temp_basefilepath,
                                  targets=[".pdf"])

        if target_filepath is None:
            return False

        # Convert the target_filepath to a source path
        src_filepath = SourcePath(project_root=target_filepath.parent,
                                  subpath=target_filepath.name)

        # Now the target of tex->pdf is the source for this file
        self.src_filepath = SourcePathArgument('src_filepath',
                                               src_filepath,
                                               required=True)

        return super(Tex2svg, self).convert()
