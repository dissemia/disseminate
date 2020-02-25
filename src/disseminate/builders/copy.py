"""
A Builder to copy or link files.
"""
from shutil import copyfile

from .builder import Builder


class Copy(Builder):
    """A builder to copy or build a file."""

    @property
    def status(self):
        return "done" if not self.build_needed() else "ready"

    def build(self, complete=False):
        infilepath = self.infilepaths[0]
        outfilepath = self.outfilepath
        copyfile(infilepath, outfilepath)
        self.build_needed(reset=True)  # reset build flag
        return self.status
