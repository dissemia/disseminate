"""
A compiled document class for documents that need to be compiled to their
final version.
"""
from tempfile import mkdtemp
from shutil import rmtree
import os.path

from ..convert import convert
from ..utils import mkdir_p
from .document import Document, DocumentError
from .. import settings


class CompiledDocumentError(DocumentError):
    """An error in generating a compiled document"""

    exit_code = None
    shell_out = None


class CompiledDocument(object):
    """A compiled document is a document that requires additional
    compilation steps to generate the final target."""

    document = None
    compiled_targets = None
    uncompiled_targets = None

    _temp_dir = None

    def __init__(self, targets, *args, **kwargs):
        self.targets = targets

        # Setup the compilation
        # First separate the compiled and uncompiled targets
        self.compiled_targets = {k: v for k,v in targets.items()
                                 if k in settings.compiled_exts}
        self.uncompiled_targets = {k: v for k,v in targets.items()
                                   if k not in settings.compiled_exts}

        # For the compiled targets, setup a temporary directory
        self._temp_dir = mkdtemp()

        # Modify the uncompiled targets to list the intermediary files to
        # compile, if they're not available. These are the files that will be
        # converted to the final target (ex: .tex)
        for target, target_filepath in self.compiled_targets.items():
            # Determine the intermediary target. ex: '.tex'
            intermediary_target = settings.compiled_exts[target]

            # In this case, the intermediary file is already being created,
            # so a temporary one doesn't have to make
            if intermediary_target in self.uncompiled_targets:
                continue

            # Otherwise the intermediary target should be added to the
            # uncompiled_targets with a temporary target_filepath

            # Get the filename for the target. ex: 'index.pdf'
            filename = os.path.split(target_filepath)[1]

            # Convert the filename to an intermediate target filename
            # ex: 'index.tex'
            target_filename = (os.path.splitext(filename)[0] +
                               intermediary_target)

            # Create an intemediary path in a temporary directory
            target_filepath = os.path.join(self._temp_dir, target_filename)

            # Add the intermediary target_filepath to the list of
            # uncompiled_targets to generate
            self.uncompiled_targets[intermediary_target] = target_filepath

        # create the document as usual with the uncompiled targets
        kwargs['targets'] = self.uncompiled_targets
        self.document = Document(*args, **kwargs)

    def __del__(self):
        """Clean up any temp directories no longer in use."""
        if self._temp_dir is not None:
            rmtree(self._temp_dir, ignore_errors=True)

    def get_ast(self, *args, **kwargs):
        return self.document.get_ast(*args, **kwargs)

    def render(self, *args, **kwargs):
        """Render the documents and compile the required documents."""
        # Render the documents, as usual
        self.document.render(*args, **kwargs)

        # Find the targets that should be turned into compile targets
        for target, target_filepath in self.compiled_targets.items():
            # Check to see if the target directory needs to be created
            if settings.create_dirs:
                mkdir_p(target_filepath)

            # Determine the intermediary target. ex: '.tex'
            intermediary_target = settings.compiled_exts[target]

            # Get the location of the intermediate target file and proceed if
            # it's valid
            if (intermediary_target in self.document.targets and
               os.path.isfile(self.document.targets[intermediary_target])):
                # Get the src_file path, which is the target_filepath of the
                # intermediary file
                src_filepath = self.document.targets[intermediary_target]

                # Get the target_basefilepath, which is the target_filepath
                # without the extension
                target_basefilepath = os.path.splitext(target_filepath)[0]

                # Determine the compiled_intermediary_targ
                return convert(src_filepath=src_filepath,
                               target_basefilepath=target_basefilepath,
                               targets=[target,])