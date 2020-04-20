"""
Builder to save temporary files
"""
import logging

from .builder import Builder, BuildError
from .utils import generate_mock_infilepath, generate_outfilepath
from ..utils.classes import weakattr
from ..utils.file import mkdir_p


class SaveTempFile(Builder):
    """A Builder to save a string to a temporary file

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
        The input for the saved temp file. This function expects a string.
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.
    save_ext : str
        The extension for the saved temp file.
    """

    available = True
    action = 'save'
    priority = 1000
    active_requirements = ('priority',)
    scan_infilepaths = False  # This is done after all infilepaths are loaded

    context = weakattr()

    infilepath_ext = '.save'  # dummy extension for find_builder_cls

    save_ext = None

    def __init__(self, env, context, save_ext=None, **kwargs):
        super().__init__(env=env, **kwargs)
        # Checks
        assert save_ext or self.outfilepath, ("Either a save_ext or an "
                                              "outfilepath must be specified")

        self.save_ext = save_ext or self.outfilepath.suffix
        self.context = context

    @property
    def outfilepath(self):
        outfilepath = self._outfilepath

        if outfilepath is None:
            infilepaths = self.infilepaths

            if infilepaths:
                # Create an temporary infilepath from the hash of the input
                sourcepath = generate_mock_infilepath(env=self.env,
                                                      context=self.context,
                                                      infilepaths=infilepaths,
                                                      ext='.save')

                outfilepath = generate_outfilepath(env=self.env,
                                                   infilepaths=sourcepath,
                                                   append=self.outfilepath_ext,
                                                   ext=self.save_ext,
                                                   target=self.target,
                                                   use_cache=self.use_cache,
                                                   use_media=self.use_media)

        # Make sure the outfilepath directory exists
        if outfilepath and not outfilepath.parent.is_dir():
            mkdir_p(outfilepath.parent)

        return outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value

    def build(self, complete=False):
        # Check that the string to write is in the infilepaths
        strings = [f for f in self.infilepaths if isinstance(f, str)]
        if len(strings) == 0:
            msg = ("The '{}' builder expects a single string as the infilepath "
                   "to save the temporary file.")
            raise BuildError(msg.format(self.__class__.__name__))
        string = strings[0]

        outfilepath = self.outfilepath
        logging.debug("Saving temporary file to '{}'".format(outfilepath))
        outfilepath.write_text(string)

        self.build_needed(reset=True)  # reset build flag
        return self.status
