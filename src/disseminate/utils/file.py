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


def parents(path):
    """Generate a list of parent paths for the given path.

    Parameters
    ----------
    path : str
        A filepath or directory.

    Returns
    -------
    parents : List[str]
        The parents of the path

    Examples
    --------
    >>> parents('/home/jlorieau/Documents/test.txt')
    ['/home/jlorieau/Documents', '/home/jlorieau', '/home']
    >>> parents('tex/chapter1/chapter1.tex')
    ['tex/chapter1', 'tex']
    """
    # Determine if path is a directory or a file
    is_dir = os.path.splitext(path)[1] == ""

    current_path = path if is_dir else os.path.split(path)[0]

    parents = []
    while current_path not in ('/', '.', ''):
        parents.append(current_path)
        current_path = os.path.split(current_path)[0]

    return parents

