"""
Objects to manage builds
"""
import logging
import subprocess
from abc import ABCMeta
from distutils.spawn import find_executable

from .utils import cache_filepath
from .exceptions import runtime_error
from ..utils.file import mkdir_p
from ..paths import SourcePath, TargetPath


class Builder(metaclass=ABCMeta):
    """A build for one or more dependencies.

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
        The filepaths for input files in the build
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.

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
    infilepath_ext : str
        The format extension for the input file (ex: '.pdf')
    outfilepath_ext : str
        The format extension for the output file (ex: '.svg')
    outfilepath_append : str
        For automatically generated outfilepaths, the following string will
        be appended to the name of the file. ex: '_scale'
    priority : int
        If multiple viable builders are available, use the one with the highest
        priority.
    required_execs : Tuple[str]
        A list of external executables that are needed by the builder.
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

    infilepath_ext = None
    outfilepath_ext = None

    outfilepath_append = None

    priority = None
    required_execs = None

    _active = None
    _infilepaths = None
    _outfilepath = None

    popen = None

    def __init__(self, env, infilepaths=None, outfilepath=None, **kwargs):
        self.env = env

        # Load the infilepaths, which must be SourcePaths
        infilepaths = infilepaths or []
        infilepaths = (list(infilepaths) if isinstance(infilepaths, tuple) or
                       isinstance(infilepaths, list) else [infilepaths])
        infilepaths = [i for i in infilepaths if isinstance(i, SourcePath)]
        self.infilepaths = infilepaths

        # Load the outfilepath
        self.outfilepath = (outfilepath if isinstance(outfilepath, TargetPath)
                            else None)

    @property
    def active(self):
        """True if a builder is available"""
        cls = self.__class__

        if cls._active is not None:
            return cls._active

        active = True
        if not isinstance(cls.active_requirements, tuple):
            return False

        # 1. Make sure the priority is properly set for the concrete class
        priority = isinstance(cls.priority, int)
        if 'priority' in self.active_requirements and not priority:
            logging.warning("Builder '{}' not available because a priority has "
                            "not been set.".format(cls.__name__))
            active = False
        required_execs = isinstance(cls.required_execs, tuple)

        # 2. Make sure the required executable tuple is properly set for the
        #    concrete class
        if 'required_execs' in self.active_requirements and not required_execs:
            logging.warning("Builder '{}' not available because the required "
                            "executable tuple was not "
                            "specified.".format(cls.__name__))
            active = False

        # 3. Make sure the required executables can be found
        if 'all_execs' in self.active_requirements:
            all_execs = {exe: find_executable(exe)
                         for exe in cls.required_execs}
            if not all(v is not None for v in all_execs.values()):
                missing_execs = [exe for exe, available in all_execs.items()
                                 if available is None]
                logging.warning("Builder '{}' not available because the "
                                "required executables could not be "
                                "found: {}".format(cls.__name__, missing_execs))
                active = False

        cls._active = active
        return cls._active

    @property
    def status(self):
        """The status of the builder.

        The builder can have the following states:
        - 'ready': The builder is active and the infilepaths have been set
        - 'inactive': The builder isn't active--see the active property
        - 'missing': The infilepaths have not been specified, the infilepaths
          do not exist or the outfilepath could not be created.
        - 'building': The builder is building
        - 'done': The builder is done building
        """
        active = self.active
        has_infilepaths = len(self.infilepaths) > 0
        if not active:
            return "inactive"
        elif (not has_infilepaths or
              not all(i.exists() for i in self.infilepaths)):
            return "missing"
        elif not self.build_needed() or self.popen == "done":
            return "done"
        elif self.popen is not None:
            poll = self.popen.poll()
            if poll is None:
                # If popen.poll() returns None, the process isn't done.
                return "building"
            elif not self.outfilepath.exists():
                return "missing"
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
        inputs = list(self.infilepaths)
        if self.action:
            inputs.append(self.action)

        return self.decision.build_needed(inputs=inputs,
                                          output=self.outfilepath,
                                          reset=reset)

    @property
    def infilepaths(self):
        """The list of input filenames and paths needed for the build"""
        return self._infilepaths

    @infilepaths.setter
    def infilepaths(self, value):
        self._infilepaths = value

    @property
    def outfilepath(self):
        """The output filename and path"""
        outfilepath = self._outfilepath

        if outfilepath is None:
            infilepaths = self.infilepaths
            if infilepaths:
                outfilepath = cache_filepath(path=self.infilepaths[0],
                                             append=self.outfilepath_append,
                                             env=self.env,
                                             ext=self.outfilepath_ext)

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
            infilepaths_str = " ".join([str(i) for i in self.infilepaths])
            fmt_action = self.action.format(infilepaths=infilepaths_str,
                                            outfilepath=self.outfilepath)
            return fmt_action.split()
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
