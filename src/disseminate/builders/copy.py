"""
A Builder to copy or link files.
"""
import logging
import pathlib
from shutil import copyfile

from .builder import Builder


class Copy(Builder):
    """A builder to copy or build a file."""

    action = 'copy'
    available = True
    active_requirements = ('priority',)
    priority = 1000
    infilepath_ext = '.*'
    outfilepath_ext = '.*'

    def __init__(self, env, infilepaths=None, outfilepath=None, **kwargs):
        # reset outfilepath_ext so that '.*' isn't used in automatically
        # generating the outfilepath (generate_outfilepath)
        self.outfilepath_ext = None

        super().__init__(env=env, infilepaths=infilepaths,
                         outfilepath=outfilepath, **kwargs)

        # Make sure the infilepaths are pathlib.Path objects
        self.infilepaths = [i if isinstance(i, pathlib.Path)
                            else pathlib.Path(i) for i in self.infilepaths]

    @property
    def status(self):
        if (not self.build_needed() or
           self.infilepaths and self.infilepaths[0] == self.outfilepath):
            # Done if the build is not needed or the src and dest are the
            # same file
            return "done"
        elif not all(i.exists() for i in self.infilepaths
                     if hasattr(i, 'exists')):
            # Missing if one or more of the infilepaths are missing
            return "missing (infilepaths)"
        else:
            return "ready"

    def build(self, complete=False):
        if self.status == 'ready':
            infilepath = self.infilepaths[0]
            outfilepath = self.outfilepath

            # Copy the file in the 2 files have different paths. If they have
            # the same path, then a shutil.SameFileError exception is raised.
            if infilepath != outfilepath:
                logging.debug("Copying '{}' -> '{}'".format(infilepath,
                                                            outfilepath))
                copyfile(infilepath, outfilepath)

            self.build_needed(reset=True)  # reset build flag
        return self.status
