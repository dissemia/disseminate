"""
A scanner object to find implicit dependencies.
"""
from ...paths import SourcePath, TargetPath
from ...utils.classes import all_subclasses


class Scanner(object):
    """A scanner object parses the contents of a file and finds implicit file
    dependencies.
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
    def scan(cls, parameters, raise_error=True):
        """Scan parameters for dependencies.

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
        parameters = (parameters if isinstance(parameters, list) or
                      isinstance(parameters, tuple) else [parameters])

        new_infilepaths = []

        # Parse each filepath
        for parameter in parameters:
            if (not isinstance(parameter, SourcePath) and
               not isinstance(parameter, TargetPath)):
                continue

            # Make sure this scanner can deal with this type of infilepath
            if parameter.suffix not in cls.extensions:
                # See if an alternative scanner can be found
                scanner = cls.get_scanner(extension=parameter.suffix)
                if scanner is None:
                    # If not, skip this infilepath
                    continue
                else:
                    # If so, use it instead
                    new_infilepaths += scanner.scan(parameter,
                                                    raise_error=raise_error)
                    continue

            # Parse the infilepath, if it exists
            if not parameter.is_file():
                continue
            stubs = cls.scan_function(parameter.read_text())

            # Find the new, valid infilepaths. First, parse the source
            # infilepath.
            if getattr(parameter, 'project_root', None) is not None:
                root = parameter.project_root
            if getattr(parameter, 'target_root', None) is not None:
                root = parameter.target_root
            if getattr(parameter, 'target', None) is not None:
                root = root / parameter.target
            subpath = parameter.subpath.parent

            for stub in stubs:
                # Strip leading slashes so that the stub is not an absolute
                # path
                stub = stub.strip('/')

                test_paths = [SourcePath(project_root=root,
                                         subpath=subpath / stub),
                              SourcePath(project_root=root,
                                         subpath=stub)]
                valid_paths = [p for p in test_paths if p.is_file()]

                # If no files are found, raise an exception
                if not valid_paths and raise_error:
                    msg = "Could not find the file '{}' in paths: '{}'"
                    raise FileNotFoundError(msg.format(stub, test_paths))
                else:
                    new_infilepaths.append(valid_paths[0])

        return new_infilepaths
