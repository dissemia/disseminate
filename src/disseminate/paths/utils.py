"""
Utilities for paths.
"""
import pathlib


def rename(path, filename=None, append=None, extension=None):
    """Rename the filename from a path with optional modifiers.

    Parameters
    ----------
    path : Union[str, :obj:`pathlib.Path`]
        The path to rename
    filename : Optional[str]
        The new filename to rename the filename (without the extension)
    append : Optional[str]
        If specified, add the string to the filename
    extension : Optional[str]
        If specified, replace the extension with the given extension

    Returns
    -------
    new_path : :obj:`pathlib.Path`
        The new path with the filename renamed.

    Examples
    --------
    >>> rename('/tmp/ch1_file.png', filename='test')
    PosixPath('/tmp/test.png')
    >>> rename('/tmp/ch1_file.png', append='_crop2')
    PosixPath('/tmp/ch1_file_crop2.png')
    >>> rename('/tmp/ch1_file.png', append='_crop2', extension='ext')
    PosixPath('/tmp/ch1_file_crop2.ext')
    >>> rename('/tmp/ch1.1_file.png', filename='test')
    PosixPath('/tmp/test.png')
    >>> rename('/tmp/ch1.1_file.png', filename='test', append='_crop2')
    PosixPath('/tmp/test_crop2.png')
    >>> rename('/tmp/ch1.1_file.png', filename='test', append='_crop2',
    ...        extension='svg')
    PosixPath('/tmp/test_crop2.svg')
    >>> rename('/tmp/ch1.1_file', extension='html')  # this won't work
    PosixPath('/tmp/ch1.html')
    """
    # Prepare the path argument
    if isinstance(path, str):
        path = pathlib.Path(path)
    parent = path.parent  # directory of path

    # Get the base filename (stem) and workup as necessary
    filename = path.stem if filename is None else filename
    if append:
        filename += append

    # Get the extension and workup as necessary
    extension = path.suffix if extension is None else extension
    extension = '.' + extension if not extension.startswith('.') else extension

    # Return the renamed path
    return parent / (filename + extension)
