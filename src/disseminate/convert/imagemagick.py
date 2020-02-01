"""
Converters that use imagemagick's convert.
"""
from .converter import Converter, ConverterError


class Tif2png(Converter):
    """Converter for a tif file to a png file."""

    order = 11000

    from_formats = ('.tiff', '.tif')
    to_formats = ('.png',)

    required_execs = ['convert', ]

    def convert(self):
        """Convert a tif file to a png file."""
        convert_exec = self.find_executable('convert')

        # Convert the file from tif to png
        # convert infile.png outfile.tif
        target_filepath = self.target_filepath()
        src_filepath = self.src_filepath.value
        args = [convert_exec, str(src_filepath), str(target_filepath)]

        returncode, out, err = self.run(args, raise_error=True)

        # Raise a convert error, if the target file wasn't created.
        # (Unfortunately, the asymptote command-line program produces a return
        # code of 0, regardless of errors
        successful = (target_filepath.is_file() and
                      target_filepath.stat().st_mtime >
                      src_filepath.stat().st_mtime)
        if not successful:
            msg = ("Convert could not produce the target file using "
                   "the command: '{}'".format(' '.join(args)))
            e = ConverterError(msg)
            e.returncode = returncode
            e.shell_out = out
            e.shell_err = err
            raise e

        return successful
