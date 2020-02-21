"""
Decider classes to evaluate whether a build is needed.
"""
from ...paths import SourcePath, TargetPath
from ...utils.classes import weakattr


class Decision(object):
    """A decision to build.

    The base decision checks to see if the input files and output file
        exist.
    """

    build_needed = None

    def __init__(self, inputs, output, args):
        assert isinstance(inputs, list) or isinstance(inputs, tuple)

        # Test to make sure all of the SourcePath inputs exist
        infiles = [p for p in inputs if isinstance(p, SourcePath)]
        if not all(p.exists() for p in infiles):
            self.build_needed = True
        elif not isinstance(output, TargetPath) or not output.exists():
            self.build_needed = True
        else:
            self.build_needed = False

    def __enter__(self):
        """Run when the build is making a decision to run the build.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Run when the build is finished, or an error was encountered"""
        self.build_needed = False


class Decider(object):
    """A decider to evaluate whether a build is needed."""

    environment = weakattr()
    decision_cls = Decision

    def __init__(self, env):
        self.environment = env

    @property
    def decision(self):
        """Return the Decision class associated with this decider."""
        return self.decision_cls
