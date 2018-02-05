"""
Utilities for manipulating files and paths
"""
import os
import errno


def mkdir_p(path):
    """Creates directories for the given filepath or directory, if needed.

    Parameters
    ----------
    path : str
        A filepath or directory.
    """
    # Determine if it's a directory or a file
    is_dir = os.path.splitext(path)[1] == ""
    
    if is_dir:
        base = path
    else:
        base, _ = os.path.split(path)
    try:
        os.makedirs(base)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(base):
            pass
        else:
            raise
