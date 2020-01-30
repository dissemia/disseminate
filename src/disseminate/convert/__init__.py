"""Converters are wrappers to external programs to convert from one file format
to another. Converters that take in parameters, specified by tag attributes
and other sources. Converter sub-classes are used, and each of these specifies
a file format to convert from and a file format to convert to.

Converters have the following responsibilities:

1. *Parameter validation*. Converters check the command-line parameters to make
   sure they're correct for the executed external program.
2. *Caching*. Converters cache the converted (or intermediary) files and will
   reuse these as long as the source file's modification time (mtime) is not
   newer than the target file.
3. *External executable management*. Converters search the path for available
   external programs and will report whether a specific converter is available
   to use.
4. *Paths*. Users of converters must specify the source filepath for the file
   to be converter from, and the base filepath for the target file (without
   the extension), and the converter will decide which converter to use and
   which file extension to convert to, based on the render target being used.
   This decision is deferred to the converters because different rendered
   targets may require different formats for media files.
"""
from .converter import convert, ConverterError
from . import pdf, tex, asy, imagemagick
