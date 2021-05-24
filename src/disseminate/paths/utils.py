"""
Utilities for paths.
"""
import pathlib
import io


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


def find_files(string, context):
    """Determine if filenames for valid files are present in the given
    string.

    Parameters
    ----------
    string : str
        The string that may contain filenames
    context : :obj:`.DocumentContext`
        A document context that contains paths to search.

    Returns
    -------
    filepaths : List[:obj:`pathlib.Path`]
        List of found paths
    """
    assert 'paths' in context and isinstance(context['paths'], list)

    # Setup arguments and return values
    # First remove extra spaces and newlines on the ends.
    string = str(string).strip()
    filepaths = list()

    # Go line-by-line and find valid files. Stop when no more lines can
    # be found
    for line in string.splitlines():
        # Skip empty lines
        if line == "":
            continue

        filepath = find_file(line, context=context, raise_error=False)
        if filepath is not None:
            filepaths.append(filepath)

    return filepaths


def find_file(path, context, raise_error=True):
    """Search for an existing file given the path and, if needed, the 'paths'
    entry from a context.

    Parameters
    ----------
    path : Union[str, :obj:`pathlib.Path`]
        The path stub to search.
    context : :obj:`.context.Context`
        The document's context with an entry of 'paths' to search.
    raise_error : Optional[bool]
        If True (default), raise error if a file isn't found.

    Returns
    -------
    valid_path : :obj:`pathlib.Path`
        A path for a file that exists.

    Raises
    ------
    FileNotFoundError
        Raised if the file could not be found.
    """
    assert 'paths' in context and isinstance(context['paths'], list)

    # Prepare the parameters
    if isinstance(path, str):
        path_strs = path.strip().splitlines()  # Keep only the first line
        path = pathlib.Path(path_strs[0] if path_strs else '')

    # If it's not a path at this stage, return None--no path can be found
    if not isinstance(path, pathlib.Path):
        if raise_error:
            msg = "Could not find file '{}'".format(path)
            raise FileNotFoundError(msg)
        return None

    # See if the file is itself a valid file. This might fail if the string
    # in the path would make a filename that is too long, raising an OSError
    try:
        if path.is_file():
            return path
    except OSError as e:
        if raise_error:
            raise e

    # See if it's an absolute file that doesn't exist
    if path.is_absolute():
        if raise_error:
            msg = "Could not find file '{}'".format(path)
            raise FileNotFoundError(msg)
        return None

    # Otherwise see if the path can be reconstructed
    paths = ['.'] + context['paths']
    for p in paths:
        # Treat SourcePath and TargetPath in a special way to correctly set the
        # subpath
        if hasattr(p, 'use_subpath'):
            subpath = p.subpath / path if p.subpath is not None else path
            new_path = p.use_subpath(subpath)
        else:
            new_path = p / path

        try:
            if new_path.is_file():
                return new_path
        except OSError as e:
            if raise_error:
                raise e

    # I'm out of ideas and places to search! Raise an error
    if raise_error:
        msg = "Could not find file '{}' in the paths: '{}'".format(path, paths)
        raise FileNotFoundError(msg)
    return None


def load_io_stream(filepath_or_buffer, context):
    """Convert a string, path or file stream into a string stream.

    Parameters
    ----------
    filepath_or_buffer : Union[str, :obj:`pathlib.Path`, :obj:`io.BaseIO`]
        A filepath, string or IO stream
    context : :obj:`.context.Context`
        The document's context with an entry of 'paths' to search.

    Returns
    -------
    stream : :obj:`io.BaseIO`
        An IO stream

    Raises
    ------
    FileNotFoundError
        Raised if the path is for a file that cannot be found
    """
    # See if it's already a file or string stream
    if isinstance(filepath_or_buffer, io.IOBase):
        return filepath_or_buffer

    # See if it's a pathlib.Path. If so, return a text stream of its
    # contents
    if isinstance(filepath_or_buffer, pathlib.Path):
        # Raises FileNotFound error if file not found
        return io.StringIO(filepath_or_buffer.read_text())

    # Otherwise try it as a string
    if isinstance(filepath_or_buffer, str):
        # See if it's a string that can be turned into a path
        filepaths = find_files(filepath_or_buffer, context=context)
        if len(filepaths) > 0:
            return load_io_stream(filepaths[0], context=context)

        # Otherwise return a text stream directory
        return io.StringIO(filepath_or_buffer)

    # I don't know what to do with filepath_or_buffer at this stage
    raise ValueError("The filepath_or_buffer cannot be converted to a "
                     "text stream")
