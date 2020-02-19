"""
A builder to crop pdf files
"""

from .builder import Builder


class PdfCrop(Builder):
    """A fixed builder to crop a pdf and form a cropped pdf."""

    priority = 1000
    required_execs = ('pdf-crop-margins',)

    infilepath_ext = '.pdf'
    outfilepath_ext = 'pdf'
    outfilepath_append = '_crop'

    def build(self):
        """Run the build"""
        # Build the subbuilders
        status = super().build()

        if status == 'done':
            pass
        return status

