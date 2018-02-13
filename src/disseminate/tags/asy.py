"""
Asymptote tags
"""
import os.path
from tempfile import mkdtemp
from hashlib import md5

from .core import Tag
from .img import Img


class Asy(Img):
    """The asy tag for inserting asymptote images."""

    src_filepath = None
    manage_dependencies = True
    _temp_dir = None

    def __init__(self, name, content, attributes,
                 local_context, global_context):
        Tag.__init__(self, name, content, attributes, local_context,
                     global_context)

        # Initialize the attributes
        if self.attributes is None:
            self.attributes = []

        # Get the contents of the tag
        contents = self.content
        self.content = None

        # Determine with the contents is a file or asy code
        if os.path.isfile(contents):
            self.src_filepath = contents
        else:
            # If it's code, save it to a temporary file. Use the hash as the
            # filename so that the file can be cached

            # Initialize a temp directory
            if Asy._temp_dir is None:
                Asy._temp_dir = mkdtemp()

            # Get a filename from a hash
            filename = md5(contents) + '.asy'
            temp_filepath = os.path.join(Asy._temp_dir, filename)

            # Write the file
            with open(temp_filepath, 'w') as f:
                f.write(contents)

            # Set the src_filepath as the temp_filepath
            self.src_filepath = temp_filepath

