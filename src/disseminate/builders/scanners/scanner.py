"""
A scanner object to find implicit dependencies.
"""
import pathlib

from ...paths import SourcePath
from ...utils.classes import all_subclasses


class Scanner(object):
    """A scanner object parses the contents of a file and finds implicit file
    dependencies.

    Works with parallel builders
    """

    extensions = tuple()

    _scanners = None

    def __init__(self):
        msg = "Scanner classes cannot be instantiated"
        raise TypeError(msg)

    @staticmethod
    def scan_function(content):
        """The function to scan content for new infilepaths.

        Subclasses derive this function."""
        return []

    @classmethod
    def get_scanner(cls, extension):
        """Get the scanner for the given extension"""
        if cls._scanners is None:
            # Get all subclasses
            scanners = all_subclasses(Scanner)

            # Create concrete scanners
            scanners_dict = {ext: scanner for scanner in scanners
                             for ext in scanner.extensions}
            cls._scanners = scanners_dict
        return cls._scanners.get(extension, None)

    @classmethod
    def scan(cls, infilepaths, raise_error=True):
        """Scan infilepaths for dependencies.

        Parameters
        ----------
        str_or_filepath : Union[str, :obj:`pathlib.Path`]
            A string or a filepath to a filename to scan.
        paths : List[:obj:`pathlib.Path`]
            A list of directories to search.
        raise_error : bool
            If True (default), raise a FileNotFoundError if a dependency
            file could not be found.

        Returns
        -------
        new_infilepaths : List[:obj:`.paths.SourcePath`]
            A list of infilepath dependencies.
        """
        # Prepare the arguments
        infilepaths = (infilepaths if isinstance(infilepaths, list)
                       or isinstance(infilepaths, tuple) else [infilepaths])

        new_infilepaths = []

        # Parse each filepath
        for infilepath in infilepaths:
            if isinstance(infilepath, SourcePath):
                pass
            else:
                continue

            # Make sure this scanner can deal with this type of infilepath
            if infilepath.suffix not in cls.extensions:
                # See if an alternative scanner can be found
                scanner = cls.get_scanner(extension=infilepath.suffix)
                if scanner is None:
                    # If not, skip this infilepath
                    continue
                else:
                    # If so, use it instead
                    new_infilepaths += scanner.scan(infilepath,
                                                    raise_error=raise_error)
                    continue

            # Parse the infilepath
            stubs = cls.scan_function(infilepath.read_text())

            # Find the new, valid infilepaths. First, parse the source
            # infilepath.
            project_root = infilepath.project_root
            subpath = infilepath.subpath.parent

            for stub in stubs:
                # Strip leading slashes so that the stub is not an absolute path
                stub = stub.strip('/')

                test_paths = [SourcePath(project_root=project_root,
                                         subpath=subpath / stub),
                              SourcePath(project_root=project_root,
                                         subpath=stub)]
                valid_paths = [p for p in test_paths if p.is_file()]

                # If no files are found, raise an exception
                if not valid_paths and raise_error:
                    msg = "Could not find the file '{}'".format(stub)
                    raise FileNotFoundError(msg)
                else:
                    new_infilepaths.append(valid_paths[0])

        return new_infilepaths
