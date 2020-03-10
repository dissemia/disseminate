"""
Builders that use ImageMagick's convert.
"""
from .builder import Builder


class ImageMagick(Builder):
    """An abstract base class for ImageMagick's convert."""

    action = 'convert {builder.infilepaths} {builder.outfilepath}'
    available = False
    priority = 10000
    required_execs = ('convert',)


class Tif2png(ImageMagick):
    """Converter for a tif file to a png file."""

    available = True
    infilepath_ext = '.tif'
    outfilepath_ext = '.png'


class Tiff2png(ImageMagick):
    """Converter for a tiff file to a png file."""

    available = True
    infilepath_ext = '.tiff'
    outfilepath_ext = '.png'
