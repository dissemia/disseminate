"""
Utilities for manipulating files and paths
"""
import os
import errno


def mkdir_p(filepath):
    """Creates directories for the given filepath, if needed.

    Parameters
    ----------
    filepath : str
        A filepath that includes a directory *and* and filename.
    """
    base, file = os.path.split(filepath)
    try:
        os.makedirs(base)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(base):
            pass
        else:
            raise
