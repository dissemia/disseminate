"""The base Converter class."""
import os.path
import subprocess
import logging
from tempfile import mkdtemp
from distutils.spawn import find_executable

from .arguments import PathArgument, Argument
from .. import settings


def kwargs_to_str(truncate_str_length=12, **kwargs):
    """Convert a kwargs dict into a string suitable for a filename.

    Since the kwargs may come from user input, the final string is limited
    somewhat to 6 modifiers and to the truncated_str_length for strings.

    Parameters
    ----------
    truncate_str_length : int, optional
        keys or values that generate strings longer than this number are
        truncated.
    kwargs : dict
        kwargs to convert to a string suitable for a filename.

    Returns
    -------
    str
        A string suitable for a filename.

    Examples
    --------
    >>> kwargs_to_str()
    ''
    >>> kwargs_to_str(scale='3.4', crop=True)
    'crop_scale3'
    >>> kwargs_to_str(scale='2.0', crop=False)
    'scale2'
    """
    pieces = []
    for k, v in sorted(kwargs.items())[:6]:  # Limit the number of arguments
        # Convert the value from a string, if needed
        if isinstance(v, str):
            if v.title() == 'True':
                v = True
            elif v.title() == 'False':
                v = False
            elif v.isnumeric():
                v = int(v)
            else:
                try:
                    v = round(float(v))  # need to remove decimals from floats.
                except ValueError:
                    pass

        if v is True:
            pieces.append(str(k)[:truncate_str_length])
        elif v is False:
            pass
        elif isinstance(v, float):
            pieces.append(str(k)[:truncate_str_length] +
                          str(v)[:truncate_str_length])
        else:
            pieces.append(str(k)[:truncate_str_length] +
                          str(v)[:truncate_str_length])
    return '_'.join(pieces)


def convert(src_filepath, target_basefilepath, targets, raise_error=True,
            cache=settings.convert_cache, **kwargs):
    """Convert a source file to a target file.

    Parameters
    ----------
    src_filepath : str
        The path and filename for the file to convert. This file must exist,
        and it's a render path.
        ex: 'src/media/img1.svg'
    target_basefilepath : str
        The path and filename (without extension) that the target file should
        adopt. This is a render path, and the final target will be determined
        by this function, if a conversion is possible.
        ex: 'tex/media/img'
    targets : list of strings
        A list of possible extensions for formats that the file can be
        converted to, depending on which programs are installed. This list
        is in decreasing order of preference.
        ex: ['.pdf', '.png', '.jpg]
    raise_error : bool, optional
        If True, a ConvertError will be raised if a suitable converter was not
        found or the conversion was not possible.
    cache : bool, optional
        If True, return an existing target file, rather than convert it, if
        the target file is newer than the source file (src_filepath)

    Raises
    ------
    ConvertError
        A ConvertError is raise if raise_error is True and a suitable converter
        was not found or the conversion was not possible.

    Returns
    -------
    target_filepath : str or bool
        The final path (render path) of the converted target file that was
        created.
        False is returned if the conversion was not possible.
        ex: 'tex/media/img.pdf'
    """
    # The src_filepath should exist
    if not os.path.isfile(src_filepath):
        if raise_error:
            msg = "Could not find the file to convert '{}'"
            raise ConverterError(msg.format(src_filepath))
        return False
    # The src file needs a valid extension
    if os.path.splitext(src_filepath)[1] == '':
        if raise_error:
            msg = "The file '{}' requires a valid extension"
            raise ConverterError(msg.format(src_filepath))
        return False

    # Get the modifier string and add it to the target_basefilepath
    kwargs_str = kwargs_to_str(**kwargs)

    if kwargs_str:
        target_basefilepath = target_basefilepath + '_' + kwargs_str

    # See if a target already exists and return an existing version if available
    # and update to date
    if cache:
        def test_target(t):
            target_filepath = target_basefilepath + t
            return target_filepath if os.path.isfile(target_filepath) else False

        valid_target_filepaths = filter(bool, map(test_target, targets))
        valid_target_filepaths = list(valid_target_filepaths)

        if (valid_target_filepaths and
           (os.path.getmtime(valid_target_filepaths[0]) >=
           os.path.getmtime(src_filepath))):

            return valid_target_filepaths[0]

    # Get a suitable converter subclass
    try:
        converter = Converter.get_converter(src_filepath, target_basefilepath,
                                            targets, **kwargs)
    except ConverterError as e:
        if __debug__:
            logging.debug("Converter subclasses:", Converter._converters)
        if raise_error:
            raise e
        return False

    # Try to convert the file with the converter
    try:
        successful = converter.convert()
    except ConverterError as e:
        successful = False
        if raise_error:
            raise e

    if successful:
        return converter.target_filepath.value_string
    else:
        return False


class ConverterError(Exception):
    """An error was encountered in converting a file.
    """
    #: (str) The shell command that generated the ConverterError
    cmd = None

    #: (int) The return code for the shell command.
    returncode = None

    #: The stdout for the shell command.
    shell_out = None

    #: The stderr for the shell command.
    shell_err = None


class Converter(object):
    """The base class for converting between file types.

    Attributes
    ----------
    from_formats = list of str
        A list of text format extensions that can be handled by this converter.
        ex: ['.png', '.svg']
    to_formats = list of str
        A list of text format extensions that can be generated by this
        converter.
        ex: ['.png', '.pdf']
    order : int
        The order for the converter. If multiple converters are available
        for a given combination of from_format and to_format, the one with
        the lower order will be used first.
    required_execs : list of str
        A list of required executables for a converter.
    optional_execs : list of str
        A list of optional executables for a converter
    src_file
    """

    from_formats = None
    to_formats = None
    order = 1000
    required_execs = None
    optional_execs = None

    src_filepath = None
    target_filepath = None

    _converters = None
    _temp_dir = None

    def __init__(self, src_filepath, target_filepath, **kwargs):
        self.src_filepath = PathArgument('src_filepath', str(src_filepath),
                                         required=True)
        self.target_filepath = PathArgument('target_filepath',
                                            str(target_filepath), required=True)

    @classmethod
    def is_available(cls):
        """Return True if this converter can be used (i.e. the required
        executables are all available)."""
        execs_paths = [cls.find_executable(e) for e in cls.required_execs]

        return None not in execs_paths

    @classmethod
    def find_executable(cls, executable_string):
        return find_executable(executable_string)

    @classmethod
    def temp_filepath(self, target_filepath):
        """Given a target file path, return the filepath that can be used
        as a temporary file for the converted file."""
        # Load the temp directory
        if getattr(Converter, '_temp_dir', None) is None:
            Converter._temp_dir = mkdtemp()

        # Generate the filename
        if isinstance(target_filepath, Argument):
            filename = os.path.split(target_filepath.value_string)[1]
        else:
            filename = os.path.split(target_filepath)[1]

        return os.path.join(self._temp_dir, filename)

    @classmethod
    def run(cls, args, env=None, error_msg=None, raise_error=True):
        """Run a command from the given arguments and either log a warning or
        raise an error with the given message, if it fails.

        Parameters
        ----------
        args : list of strings
            The arguments for the command. (Compatible with Popen)
        env : dict, optional
            If specified, the env dict will be used in running the command.
            Values will be appended to the current environment.
        error_msg : str, optional
            The warning or error message if the command fails. A command fails
            if the returncode is not 0.
            If no error message was specified, a default message will be
            created.
        raise_error : bool, optional
            If True, a ConverterError will be raised if the command failed.
            If False, a warning will be logged if the command failed.

        Raises
        ------
        ConverterError
            Raised if the command failed and raise_error is True.
        """
        if __debug__:
            msg = "Running conversion: {}".format(" ".join(args))
            logging.debug(msg)

        # Setup the environment
        if env is not None:
            current_env = os.environ.copy()
            for k, v in env.items():
                if k in current_env:
                    current_env[k] += ":" + v
                else:
                    current_env[k] = v
            env = current_env

        # Run the subprocess
        p = subprocess.Popen(args, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=4096, )

        # Check that it was succesfully converted
        out, err = p.communicate()
        returncode = p.returncode

        if returncode != 0:
            if error_msg is None:
                error_msg = ("The conversion command '{}' was "
                             "unsuccessful".format(' '.join(args)))
            if raise_error:
                e = ConverterError(error_msg)
                e.cmd = " ".join(args)
                e.returncode = None
                e.shell_out = out.decode('utf-8')
                e.shell_err = err.decode('utf-8')
                raise e
            else:
                logging.warning(error_msg)

    @classmethod
    def get_converter(cls, src_filepath, target_basefilepath, targets,
                      **kwargs):
        """Return a Converter subclass instance that can handle the conversion.

        .. note:: converters returned with this method are valid and their
                  required executables are available.

        Parameters
        ----------
        src_filepath : str
            The path with filename for the file to convert.
        target_basefilepath : str
            The path and filename (without extension) that the target file
            should adopt. This is a render path, and the final target will be
            determined by this function, if a conversion is possible.
            ex: 'tex/media/img'
        targets : list of strings
            A list of possible extensions for formats that the file can be
            converted to, depending on which programs are installed. This list
            is in decreasing order of preference.
            ex: ['.pdf', '.png', '.jpg]

        Returns
        -------
        converter : instance of a Converter subclass (:obj:`Converter`)
            A valid converter in which the available executables are available.
        """
        # Setup the converter subclasses
        if cls._converters is None:
            cls._converters = sorted(cls.__subclasses__(),
                                     key=lambda s: s.order)

        # Get the extension of the src_filepath and target_filepath
        from_format = os.path.splitext(src_filepath)[1]

        # Get a list of converters that could be used for this conversion
        valid_converters = []
        for target in targets:
            valid_converters += [c for c in cls._converters
                                 if from_format in c.from_formats
                                 and target in c.to_formats]

        # If valid_converters is empty, then no valid format was found. Raise
        # a ConverterError
        if len(valid_converters) == 0:
            msg = ("Could not find a converter for the file '{}' to any of the "
                   "following possible formats: {}")
            raise ConverterError(msg.format(src_filepath, ", ".join(targets)))

        # Check to make sure that the required executables are available
        available_converters = [c for c in valid_converters
                                if c.is_available()]

        if len(available_converters) == 0:
            required_execs = [", ".join(c.required_execs) for c in
                              valid_converters]
            exe_str = ", ".join(required_execs)

            msg = ("One of the following required program(s) '{}' needs to be "
                   "installed to convert the '{}' file.")
            raise ConverterError(msg.format(exe_str, src_filepath))

        # For the available converters find the converter that can handle the
        # preferred target extension
        best_target = None
        best_converter = None
        for target in targets:
            converters = [c for c in available_converters
                          if target in c.to_formats]
            if len(converters) > 0:
                best_target = target
                best_converter = converters[0]
                break

        assert best_target is not None
        assert best_converter is not None

        # Generate the target_filepath.
        target_filepath = ''.join((str(target_basefilepath), best_target))

        # instantiate the Converter subclass
        converter = best_converter(src_filepath, target_filepath, **kwargs)

        return converter

    def convert(self):
        """Convert a file and return its new path.

        Raises
        ------
        ConvertError
            If a general error was encountered in the conversion, such as
            a unsuccessful program execution.
        ArgumentError
            One of the arguments was invalid.

        Returns
        -------
        successful : bool
            True if the conversion was successful, False if it wasn't.
        """
        return False

