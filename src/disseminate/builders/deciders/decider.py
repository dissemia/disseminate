"""
Decider classes to evaluate whether a build is needed.
"""
from .exceptions import MissingInputFiles
from ...paths import SourcePath, TargetPath
from ...utils.classes import weakattr


class Decision(object):
    """A decision to build.

    The base decision checks to see if the input files and output file
        exist.

    Parameters
    ----------
    parent_decider : :obj:`.builders.decider.Decider`
        The parent decider instance that created this decision.
    """

    parent_decider = weakattr()

    def __init__(self, parent_decider):
        self.parent_decider = parent_decider

    def build_needed(self, inputs, output, reset=False):
        """Determine whether a build is needed.

        Parameters
        ----------
        inputs : List[str, :obj:`.paths.SourcePath`, tuple]
            The input infilepaths, strings and arguments to use in the build.
        output : :obj:`.paths.TargetPath`
            The outfilepath for the built file
        reset : Optional[bool]
            If True, reset cached values in determining whether the build is
            needed.

        Raises
        ------
        MissingInputFiles
            Raise if one or more of the input files are missing.
        """
        assert isinstance(inputs, list) or isinstance(inputs, tuple)

        # Test to make sure all of the SourcePath inputs exist
        infiles = [p for p in inputs if isinstance(p, SourcePath)]
        if not all(p.exists() for p in infiles):
            missing_files = [str(p) for p in infiles if not p.exists()]
            msg = ("This following input files are missing and are needed for "
                   "a build: {}".format(", ".join(missing_files)))
            raise MissingInputFiles(msg)
        elif (not isinstance(output, TargetPath) or
              not output.exists()):
            return True
        else:
            return False


class Decider(object):
    """A decider to evaluate whether a build is needed."""

    environment = weakattr()
    decision_cls = Decision

    def __init__(self, env):
        self.environment = env

    @property
    def decision(self):
        """Return the Decision class associated with this decider."""
        return self.decision_cls(parent_decider=self)
