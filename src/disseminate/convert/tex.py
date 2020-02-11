"""
Converters to convert from ``.tex`` TEX files to pdf using pdflatex.
"""
import os
import shutil
import pathlib
from tempfile import mkdtemp

from ..paths import SourcePath, TargetPath
from ..paths.utils import rename
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
        filename_pdf = rename(src_filepath, extension='.pdf').name
        temp_filepath_pdf = TargetPath(target_root=temp_dir,
                                       subpath=filename_pdf)

        # Setup the environment. This will list the source tex directory and all
        # parent directories in the TEXINPUTS path
        texinputs = ':'.join(str(i) for i in src_filepath.parents)
        env = {'TEXINPUTS': ":" + texinputs}

        # Setup the command and run in
        args = [pdflatex_exec, "-interaction=nonstopmode", "-halt-on-error",
                "-output-directory=" + str(temp_dir),
                str(self.src_filepath.value)]

        # Run twice
        try:
            for i in range(2):
                self.run(args, env=env, raise_error=True)
        except Exception as e:
            self.annotate_exception(e)
            raise e

        # Copy the processed file to the target
        try:
            os.link(temp_filepath_pdf, self.target_filepath())
        except FileExistsError:
            os.remove(self.target_filepath())
            os.link(temp_filepath_pdf, self.target_filepath())
        except OSError:
            shutil.copy2(temp_filepath_pdf, self.target_filepath())
        return True

    @staticmethod
    def annotate_exception(exception):
        """Add additional annotations to an exception raised from running
        pdflatex."""
        # Try to pull out the error from the terminal
        out = getattr(exception, 'shell_out', None)

        if out is not None:
            lines = out.splitlines()
            error_lines = [l for l in lines
                           if l.startswith('!') or l.startswith('l.')]
            exception.args += tuple(error_lines)


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
