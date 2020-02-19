"""
Objects to manage builds
"""
import logging
import subprocess
from abc import ABCMeta
from distutils.spawn import find_executable

from .utils import cache_filepath
from .exceptions import runtime_error
from ..paths import SourcePath, TargetPath


class Builder(metaclass=ABCMeta):
    """A build for one or more dependencies.


    .. note::
      - Each builder is atomic
      - When running a build, not all of the builders might be called in the
        first build--for example, subsequent builders may rely on the results
        of previous builds. For this reason, builders should be used
        in conjunction with an environment to make sure a set of
        builds are completed.

    Parameters
    ----------
    infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
        The filepaths for input files in the build
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.
    env: :obj:`.builders.Environment`
        The build environment

    Attributes
    ----------
    action : str
        The command to execute during the build.
    target : Union[:obj:`pathlib.Path`, str]
        The target file to create
    dependencies : Union[str, List[str], :obj:`.Dependencies`]

    """
    action = None
    target = None
    env = None

    subbuilders = None
    previous_subbuilder = None
    next_subbuilder = None

    infilepath_ext = None
    outfilepath_ext = None

    outfilepath_append = None

    priority = None
    required_execs = None
    optional_execs = None

    _active = None
    _infilepaths = None
    _outfilepath = None

    popen = None

    def __init__(self, env, *args, **kwargs):
        self.env = env

        # Load the subbuilders
        self.subbuilders = [arg for arg in args if isinstance(arg, Builder)]
        self.subbuilders += list(kwargs.pop('subbuilders', []))

        # Load the infilepaths, which must be SourcePaths
        self.infilepaths = [arg for arg in args if isinstance(arg, SourcePath)]
        infilepaths = kwargs.pop('infilepaths', [])
        infilepaths = (list(infilepaths) if isinstance(infilepaths, tuple) or
                       isinstance(infilepaths, list) else [infilepaths])
        infilepaths = [arg for arg in infilepaths
                       if isinstance(arg, SourcePath)]
        self.infilepaths += infilepaths

        # Load the outfilepath
        outfilepath = kwargs.pop('outfilepath', None)
        self.outfilepath = (outfilepath if isinstance(outfilepath, TargetPath)
                            else None)

        self.target = kwargs.get('target', None)

    @property
    def active(self):
        """True if a builder is available"""
        cls = self.__class__

        if cls._active is not None:
            return cls._active

        active = True

        # 1. Make sure the priority is properly set for the concrete class
        priority = isinstance(cls.priority, int)
        if not priority:
            logging.warning("Builder '{}' not available because a priority has "
                            "not been set.".format(cls.__name__))
            active = False
        required_execs = isinstance(cls.required_execs, tuple)

        # 2. Make sure the required executable tuple is properly set for the
        #    concrete class
        if not required_execs:
            logging.warning("Builder '{}' not available because the required "
                            "executable tuple was not "
                            "specified.".format(cls.__name__))
            active = False

        # 3. Make sure the required executables can be found
        all_execs = {exe: find_executable(exe) for exe in cls.required_execs}
        if not all(v is not None for v in all_execs.values()):
            missing_execs = [exe for exe, available in all_execs.items()
                             if available is None]
            logging.warning("Builder '{}' not available because the required "
                            "executables could not be "
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
        - 'missing': The infilepaths have not been specified
        - 'building': The builder is building
        - 'done': The builder is done building
        """
        active = self.active
        has_infilepaths = len(self.infilepaths) > 0
        if not active:
            return "inactive"
        elif not has_infilepaths:
            return "missing"
        elif self.popen is not None:
            poll = self.popen.poll()
            if poll is None:
                # If popen.poll() returns None, the process isn't done.
                return "building"
            elif poll == 0:  # exit code of 0. Successful!
                return "done"
            else:  # non-zero exit code. Unsuccessful. :(
                runtime_error(popen=self.popen)

        else:
            return "ready"

    @property
    def infilepaths(self):
        return self._infilepaths

    @infilepaths.setter
    def infilepaths(self, value):
        self._infilepaths = value

    @property
    def outfilepath(self):
        outfilepath = self._outfilepath
        if outfilepath is not None:
            return outfilepath
        infilepaths = self.infilepaths
        if infilepaths:
            outfilepath = cache_filepath(path=self.infilepaths[0],
                                         append=self.outfilepath_append,
                                         env=self.env,
                                         ext=self.outfilepath_ext)
            return outfilepath
        return None

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value

    def run_cmd_args(self):
        """Format the action, if it's a string."""
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
                                                       args))

            popen = subprocess.Popen(args=args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, bufsize=4096,)
            self.popen = popen

    def build(self, complete=False):
        """Run the build.

        .. note:: This function will run the sub-builders and this builder
                  once.
        """
        def run_build(self):
            status = 'done'
            for builder in self.subbuilders:
                if builder.status == 'building':
                    status = 'building'
                elif builder.status == 'ready':
                    builder.build()
                    status = 'building'
                    break
                elif builder.status == 'done':
                    status = "done"
            return status

        # Build fixed dependencies first, then this builder's build
        if complete:
            status = None
            while status != "done":
                status = run_build(self)
        else:
            status = run_build(self)

        # Run this builder if the subbuilders are done
        if status == "done":
            if complete:
                while self.status != "done":
                    self.run_cmd()
            else:
                self.run_cmd()
        return self.status
