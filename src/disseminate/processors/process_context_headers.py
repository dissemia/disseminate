"""
Processors for working up the headers of strings in a context.
"""
from .process_context import ProcessContext
from .exceptions import ProcessContextException
from ..context.context import re_header_block
from .. import settings


class ProcessContextHeaders(ProcessContext):
    """Process header strings for entries in a context by loading them into
    the context.
    """

    # This processor should be loaded before the tags are processed
    # (ProcessContextTags) so that the tags can use the updated values from
    # headers in the context.
    order = 100
    short_desc = "Process header blocks in all string entries of the context"

    def __call__(self, context):

        # See which context entries have a header
        for k, v in context.items():
            if isinstance(v, str) and re_header_block.match(v):
                # The context entry has a header. Process the header entry and
                # strip the header from the string.
                context[k] = context.load(v, strip_header=True)


class ProcessContextAdditionalHeaderFiles(ProcessContext):
    """Process additional header files in the paths listed in the context.

    This processor will load additional context values from the template, for
    example.
    """

    # This processor should be loaded after the initial headers are loaded from
    # the context (ProcessContextHeaders), but before the tags are processed
    # (ProcessContextTags)
    order = 400

    short_desc = ("Process additional header files in the paths listed in the "
                  "context")

    def __call__(self, context):

        # Get the paths from the context
        paths = context.get('paths', [])
        header_filename = context.get('additional_header_filename',
                                      'context.txt')

        # Find the context.txt files
        for path in paths:
            header_path = path / header_filename

            # See if it's a valid path
            if header_path.is_file():
                # Check the file size
                if header_path.stat().st_size > settings.context_max_size:
                    msg = ("Context file '{}' is larger than the maximum "
                           "allowed file size {}.")
                    msg = msg.format(header_path, settings.context_max_size)
                    raise ProcessContextException(msg)

                # Load the file and read it into the context
                txt = header_path.read_text()

                # Load the values (without overwriting existing values) in the
                # context
                context.matched_update(txt, overwrite=False)
