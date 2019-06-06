"""
Processors for working up the headers of strings in a context.
"""
from .process_context import ProcessContext
from .exceptions import ProcessContextException
from ...context.utils import find_header_entries, load_from_string
from ... import settings


class ProcessContextHeaders(ProcessContext):
    """Process header strings for entries in a context by loading them into
    the context.
    """

    #: This processor should be loaded before the tags are processed
    #: (ProcessContextTags) so that the tags can use the updated values from
    #: headers in the context.
    order = 100

    def __call__(self, context):

        # See which context entries have a header
        keys = find_header_entries(context)

        # Load the context into a dict
        header_context = dict()
        for key in keys:
            rest, d = load_from_string(context[key])

            # Replace the entry with the context removed
            context[key] = rest

            # Update the header context
            header_context.update(d)

        # See if there are additional header files from the template
        

        # Load the context
        context.matched_update(header_context)


# class ProcessContextAdditionalHeaderFiles(ProcessContext):
#     """Process additional header files in the paths listed in the context.
#
#     This processor will load additional context values from the template, for
#     example.
#     """
#
#     #: This processor should be loaded after the initial headers are loaded
#     #: from the context (ProcessContextHeaders) and the template
#     #: (ProcessContextTemplate), but before the tags are processed
#     #: (ProcessContextTags)
#     order = 400
#
#     def __call__(self, context):
#
#         # Get the paths from the context
#         paths = context.get('paths', [])
#         header_filename = context.get('additional_header_filename',
#                                       'context.txt')
#
#         # Find the context.txt files
#         for path in paths:
#             header_path = path / header_filename
#
#             # See if it's a valid path
#             if header_path.is_file():
#                 # Check the file size
#                 if header_path.stat().st_size > settings.context_max_size:
#                     msg = ("Context file '{}' is larger than the maximum "
#                            "allowed file size {}.")
#                     msg = msg.format(header_path, settings.context_max_size)
#                     raise ProcessContextException(msg)
#
#                 # Load the file and read it into the context
#                 txt = header_path.read_text()
#
#                 # Load the values (without overwriting existing values) in the
#                 # context
#                 context.matched_update(txt, overwrite=False)
