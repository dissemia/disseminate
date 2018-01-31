"""
Classes and functions for managing dependencies like static files (.css) and
images.
"""


class Dependencies(object):
    """A class to keep track of the dependency files for each target type.

    Attributes
    ----------
    dependencies : dict of sets
        - The key is the target type. ex: '.html' or '.tex'
        - The value is a set of the src_filepaths for dependency files.
          ex: {'media/img.src', 'static/img.src'}


    """

    dependencies = None