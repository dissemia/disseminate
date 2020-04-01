"""
A Builder to copy or link files.
"""
import logging
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

    @property
    def status(self):
        return ("done" if not self.build_needed()
                or (self.infilepaths and  # done if src and dest are the same
                    self.infilepaths[0] == self.outfilepath)
                else "ready")

    def build(self, complete=False):
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

