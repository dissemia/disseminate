"""
Objects to manage builds
"""
import logging
import subprocess
import pathlib
from abc import ABCMeta
from string import Formatter
from distutils.spawn import find_executable

from .utils import generate_outfilepath
from .exceptions import runtime_error, BuildError
from ..utils.file import mkdir_p
from ..utils.classes import all_subclasses
from ..paths import TargetPath
from .. import settings


class CustomFormatter(Formatter):
    """A custom formatter class for preparing actions into command-line
    arguments."""

    def get_field(self, field_name, args, kwargs):
        field_value, field_name = super().get_field(field_name, args, kwargs)
        if isinstance(field_value, list) or isinstance(field_value, tuple):
            # Make lists/tuples into space-separated strings
            field_value = " ".join(self.clean_string(s) for s in field_value)
            return field_value, field_name
        return self.clean_string(field_value), field_name

    @staticmethod
    def clean_string(s):
        """Clean strings used for command-line processes"""
        return str(s).strip('-*')


class Builder(metaclass=ABCMeta):
    """A build for one or more dependencies.

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
    outfilepath : Optional[:obj:`pathlib.Path`]
        If specified, the path for the output file.
    use_cache : Optional[bool]
        If True, set the builder outfilepath into the cache_root path from the
        builder environment.
    use_media : Optional[bool]
        If True, set the builder outfilepath subpath in the media_root in the
        build environment context, if specified.

    Attributes
    ----------
    action : str
        The command to execute during the build.
    available : bool
        Whether this builder is available to factory methods
    active_requirements : Union[tuple, bool]
        If False, the builder will be inactive
        If a tuple of strings is specified, these conditions will be tested
        to see if the builder is active:
        - 'priority': test that the priority attribute is an int
        - 'required_execs': tests that the required_execs attribute is specified
        - 'all_execs': tests that the required execs are available
    scan_parameters : bool
        If True (default), scan the parameters for additional dependencies.
    priority : int
        If multiple viable builders are available, use the one with the highest
        priority.
    required_execs : Tuple[str]
        A list of external executables that are needed by the builder.
    infilepath_ext : str
        The format extension for the input file (ex: '.pdf')
    outfilepath_ext : str
        The format extension for the output file (ex: '.svg')
    outfilepath_append : str
        For automatically generated outfilepaths, the following string will
        be appended to the name of the file. ex: '_scale'
    target : Optional[str]
        If specified, use the given target for creating the target file.
        This is used in formatting the TargetPath.
        ex: 'html' target will store built files in the 'html/' subdirectory.
    popen : Union[:obj:`subprocess.Popen`, None, str]
        The process for the externally run program.
        The popen can also be None, if a process hasn't been run, or "done"
        if the process is finished.
    """
    env = None
    action = None
    available = False
    active_requirements = ('priority', 'required_execs', 'all_execs')
    decision = None
    scan_parameters = True

    priority = None
    required_execs = None
    use_cache = True
    use_media = True

    infilepath_ext = None
    outfilepath_ext = None

    # Options that impact how the outfilepath is formatted
    outfilepath_append = None
    target = None

    _active = dict()
    _available_builders = dict()
    _parameters = None
    _outfilepath = None

    popen = None

    def __init__(self, env, target=None, parameters=None, outfilepath=None,
                 use_cache=None, use_media=None, **kwargs):
        self.env = env
        self.target = target.strip('.') if isinstance(target, str) else None
        self.use_cache = use_cache if use_cache is not None else self.use_cache
        self.use_media = use_media if use_media is not None else self.use_media

        # Load the parameters
        parameters = parameters or []
        parameters = (list(parameters) if isinstance(parameters, tuple) or
                      isinstance(parameters, list) else [parameters])
        self.parameters = parameters

        # Scan for additional parameters, if desired
        if self.scan_parameters:
            self.parameters += env.scanner.scan(parameters=self.parameters)

        # Load the outfilepath
        self.outfilepath = (outfilepath if isinstance(outfilepath, TargetPath)
                            else None)

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @classmethod
    def active(cls):
        """True if a builder is active"""
        cls_name = cls.__name__

        if cls_name in Builder._active:
            return Builder._active[cls_name]

        active = True

        # 1. Make sure the priority is properly set for the concrete class
        if (cls.active_requirements and
            'priority' in cls.active_requirements and
           not isinstance(cls.priority, int)):
            logging.warning("Builder '{}' not active because a priority has "
                            "not been set.".format(cls.__name__))
            active = False

        # 2. Make sure the required executable tuple is properly set for the
        #    concrete class
        required_execs = isinstance(cls.required_execs, tuple)
        if (cls.active_requirements and
            'required_execs' in cls.active_requirements and
           not required_execs):
            logging.warning("Builder '{}' not active because the required "
                            "executable tuple was not "
                            "specified.".format(cls.__name__))
            active = False

        # 3. Make sure the required executables can be found
        if (cls.active_requirements and
            'all_execs' in cls.active_requirements and
           cls.required_execs):
            all_execs = {exe: find_executable(exe)
                         for exe in cls.required_execs}
            if not all(v is not None for v in all_execs.values()):
                missing_execs = [exe for exe, available in all_execs.items()
                                 if available is None]
                logging.warning("Builder '{}' not active because the "
                                "required executables could not be "
                                "found: {}".format(cls.__name__, missing_execs))
                active = False

        return Builder._active.setdefault(cls_name, active)

    @property
    def status(self):
        """The status of the builder.

        The builder can have the following states:
        - 'ready': The builder is active and the parameters have been set
        - 'inactive': The builder isn't active--see the active property
        - 'missing (parameters)': All the required parameters have not been
          specified or files for paths in the parameters do not exist
        - 'missing (outfilepath)': The outfilepath could not be or was not
           created
        - 'building': The builder is building
        - 'done': The builder is done building
        """
        active = self.active
        has_parameters = len(self.parameters) > 0
        if not active:
            return "inactive"
        elif (not has_parameters or
              not all(i.exists() for i in self.parameters
                      if hasattr(i, 'exists'))):
            return "missing (parameters)"
        elif not self.build_needed() or self.popen == "done":
            return "done"
        elif self.popen is not None:
            poll = self.popen.poll()
            if poll is None:
                # If popen.poll() returns None, the process isn't done.
                return "building"
            elif not self.outfilepath.exists():
                return "missing (outfilepath)"
            elif poll == 0:
                # exit code of 0. Successful!
                # Reset the popen and the build status
                self.popen = 'done'
                self.build_needed(reset=True)
                return "done"
            else:  # non-zero exit code. Unsuccessful. :(
                runtime_error(popen=self.popen)
        else:
            return "ready"

    def build_needed(self, reset=False):
        """Determine whether a build is needed."""
        if self.decision is None:
            decider = self.env.decider
            self.decision = decider.decision
        inputs = list(self.parameters)
        if self.action:
            inputs.append(self.action)
        return self.decision.build_needed(inputs=inputs,
                                          output=self.outfilepath,
                                          reset=reset)

    @property
    def parameters(self):
        """The list of input filenames and paths needed for the build"""
        return getattr(self, '_parameters', [])

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def get_parameter(self, name, *parameters):
        """Return parameters inserted as 2-ples of name/value.

        Parameters
        ----------
        name
            The name of the 2-ple parameter (the 1st 2-ple item)
        *parameters
            If specified, use these parameters to get the specified parameter.
            Otherwise, the builder's parameters will be used.

        Returns
        -------
        value
            The corresponding 2-ple value (the 2nd 2-ple item)
        """
        parameters = parameters or self.parameters or []
        filtered_parameters = [p[1] for p in parameters
                               if isinstance(p, tuple) and len(p) > 1 and
                               p[0] == name]
        return filtered_parameters[0] if filtered_parameters else None

    @property
    def infilepaths(self):
        """Retrieve the parameters that are filepaths (:obj:`pathlib.Path`)."""
        return [p for p in self.parameters if isinstance(p, pathlib.Path)]

    @property
    def not_infilepaths(self):
        """Retrieve the parameters that are not filepaths (:obj:`pathlib.Path`)
        """
        return [p for p in self.parameters if not isinstance(p, pathlib.Path)]

    @property
    def outfilepath(self):
        """The output filename and path"""
        outfilepath = self._outfilepath

        if outfilepath is None:
            outfilepath = generate_outfilepath(env=self.env,
                                               parameters=self.parameters,
                                               target=self.target,
                                               append=self.outfilepath_append,
                                               ext=self.outfilepath_ext,
                                               use_cache=self.use_cache,
                                               use_media=self.use_media)

        # Make sure the outfilepath directory exists
        if outfilepath and not outfilepath.parent.is_dir():
            mkdir_p(outfilepath.parent)

        return outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value

    def run_cmd_args(self):
        """Format the action, if it's a string.

        Returns
        -------
        run_cmd_args : Tuple[str]
            A tuple of the arguments to run in a process.
        """
        if isinstance(self.action, str):
            fmt = CustomFormatter()
            fmt_action = fmt.format(self.action, builder=self)
            return tuple(fmt_action.split())
        else:
            return tuple()

    def run_cmd(self, *args):
        """If the action is a external command, run it."""
        if self.popen is None and (isinstance(self.action, str) or args):

            # Format the action string, if it's to be used
            args = args if args else self.run_cmd_args()
            logging.debug("'{}' run with: '{}'".format(self.__class__.__name__,
                                                       " ".join(args)))

            popen = subprocess.Popen(args=args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, bufsize=4096,)
            self.popen = popen

    def build(self, complete=False):
        """Run the build.

        .. note::
          - This function will run the sub-builders and this builder once.
          - Each builder is atomic
          - When running a build, not all of the builders might be called in
            the first build--for example, subsequent builders may rely on the
            results of previous builds. For this reason, builders should be used
            in conjunction with an environment to make sure a set of
            builds are completed or the build complete=True should be used.
        """
        if complete:
            # Run while this builder is either ready to build or a build is
            # ongoing.
            while self.status in {'building', 'ready'}:
                self.run_cmd()
        else:
            if self.status in {'building', 'ready'}:
                self.run_cmd()
        return self.status

    @classmethod
    def find_builder_cls(cls, in_ext, out_ext=None, target=None,
                         raise_error=True):
        """Return a builder class

        Parameters
        ----------
        in_ext: str
            The extension for the input file.
        out_ext : str
            The extension for the output file.
        target : Optional[str]
            The document target. ex: '.html' or '.pdf'
        raise_error : Optional[bool]
            If True (default), raise an exception if a builder class couldn't
            be found.
        """
        # Cache the available builders
        if not Builder._available_builders:
            subclses = Builder._available_builders

            for builder in all_subclasses(Builder):
                logging.debug("Builder {:<30}: active={}, available={}"
                              "".format(builder.__name__, builder.active(),
                                        builder.available))

                if not builder.available or not builder.active():
                    continue

                key = (builder.infilepath_ext, builder.outfilepath_ext)

                # Only replace an existing builder if it's higher property
                if (key not in subclses or
                   subclses[key].priority < builder.priority):
                    subclses[key] = builder

        # See if there's a valid builder from the given out_ext
        key = (in_ext, out_ext)
        if target is None and key in Builder._available_builders:
            return Builder._available_builders[key]

        # Otherwise see if there's a tracked target
        target = (target if not isinstance(target, str) or
                  target.startswith('.') else '.' + target)

        msg = ("The document target must be specified and listed in the "
               "settings.tracked_deps.")
        assert target and target in settings.tracked_deps, msg

        if target in settings.tracked_deps:
            # If the in_ext is an allowed format, just use a copy builder
            # defined as the builder with a '.*' infilepath_ext and
            # outfilepath_ext
            if in_ext in settings.tracked_deps[target]:
                copy_builder = Builder._available_builders[('.*', '.*')]
                return copy_builder

            # Otherwise find a converter
            for out_ext in settings.tracked_deps[target]:
                key = (in_ext, out_ext)
                if key in Builder._available_builders:
                    return Builder._available_builders[key]

        # No builder class could be found
        if raise_error:
            msg = ("A builder cannot be found for '{}'. Available formats "
                   "are: {}".format(in_ext, settings.tracked_deps))
            raise BuildError(msg)
        else:
            return None
