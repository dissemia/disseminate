"""
Objects to manage builds
"""
import logging
import subprocess
from abc import ABCMeta
from distutils.spawn import find_executable

from .utils import cache_filepath
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
    _status = None
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
        if self._status is None:
            active = self.active
            has_infilepaths = len(self.infilepaths) > 0
            if not active:
                self._status = "inactive"
            elif not has_infilepaths:
                self._status = "missing"
            elif self.popen is not None:
                if self.popen.poll() is not None:
                    self._status = "building"
                else:
                    self._status = "done"
            else:
                self._status = "ready"
        return self._status

    @status.setter
    def status(self, value):
        assert value in {'ready', 'inactive', 'missing', 'building', 'done'}
        self._status = value

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

    def build(self, complete=False):
        """Run the build.

        .. note:: This function will run the sub-builders and this builder
                  once.
        """
        def run_build(self):
            status = 'done'
            for builder in self.subbuilders:
                if builder.status == 'building':
                    carry_over.append(builder)
                    status = 'building'
                elif builder.status == 'ready':
                    builder.build()
                    carry_over.append(builder)
                    status = 'building'
                    break
                elif builder.status == 'done':
                    status = "done"
            return status

        # Build fixed dependencies first
        carry_over = []
        if complete:
            status = None
            while status != "done":
                status = run_build(self)
        else:
            status = run_build(self)

        # Transfer over the builders that aren't finished
        self.subbuilders.clear()
        self.subbuilders += carry_over

        # Run this builder if the subbuilders are done
        if status == "done":
            self.run_cmd()
        return self.status

    def run_cmd(self, *args):
        """If the action is a external command, run it."""
        if isinstance(self.action, str) or args:
            args = args or self.action.split()
            popen = subprocess.Popen(args=args, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, bufsize=4096,)
            self.popen = popen
