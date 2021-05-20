"""
Utilities for manipulating files and paths
"""
import os
import shutil
import logging


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


def link_or_copy(src, dst):
    """Create a hard link, if possible, between a src filepath to a dst
    filepath, or copy if a link is not possible.
    """
    logging.debug("Linking file '{}' -> '{}'".format(str(src), str(dst)))

    # Determine whether dst exists and whether is has the same inode as src
    src_inode = os.stat(src).st_ino
    try:
        dst_inode = os.stat(dst).st_ino
        dst_exists = True  # the destination file exists exist
    except FileNotFoundError:
        dst_inode = None
        dst_exists = False  # the destination file doesn't exist

    dst_different = (src_inode != dst_inode)

    # Remove the destination file if it exists and it's different from the
    # source
    if dst_exists and dst_different:
        os.remove(dst)
    elif dst_exists:
        # In this case, the destination exists and the destination is the same
        # file (by inode). The objective is already achieved and nothing else
        # needs to be done
        return None

    # Try create a hard link, if possible
    try:
        return os.link(src, dst)
    except OSError:
        return shutil.copyfile(src, dst)
