"""
Contexts are dictionaries (dicts) that contain the entries of the header for
a disseminate document, the body of the disseminate document ('body' entry) and
other default settings. The context is used directly in rendering documents.

The context has the following responsibilities:

1. *Variable storage*. The context is a dict that contains the values needed
   to properly render a target document.
2. *Data validation*. Specific entries, like the src_filepath, must be a
   specific type, like a :obj:`SourcePath <disseminate.paths.SourcePath>`.
   When initializing and resetting a context, the context will check that
   entries match this type, and it will convert to the valid type if it can.
3. *Inheritance*. A document and its sub-documents will each have their own
   context. It is useful to have the context of sub-documents inherit from
   the parent document's context (parent context) for some values. A context
   keeps a reference to the parent context, and when resetting the context,
   some (or all) of the parent context values are either copied over or
   referenced.
4. *Intelligent resetting*. A context intelligently resets to its initial
   values and the values of the parent_context on reset. These values can
   then be overwritten when the document source is read in.
"""

from .context import BaseContext

__all__ = ('BaseContext',)
