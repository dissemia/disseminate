"""Utilities for loading and dealing with paths."""
import pathlib


def load_path(string, context=None):
    """Load a path from a string into a string or, if the string isn't a path,
    just return the string.
    """
    # Get a list of paths to search
    paths = []
    if context is not None and 'paths' in context:
        paths += context['paths']

    # See if the lines of the string correspond to a path
    returned_string = ''
    for line in string.strip('\n').splitlines():
        # Skip empty strings
        if not line.strip():
            continue

        # See if the line matchs a path
        path_found = False
        for path in paths:
            filepath = path / pathlib.Path(line)
            if filepath.exists():
                path_found = True
                break

        # If the path count be found then the string is not interpreted as
        # a listing of paths
        if not path_found:
            break

        returned_string += filepath.read_text()

    return returned_string if returned_string else string
