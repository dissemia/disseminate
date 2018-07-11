"""
Context objects.
"""
from copy import deepcopy


class BaseContext(dict):
    """A context object with variables used for rendering target documents.

    Contexts are suppose to be data containers--i.e. there are no sophisticated
    processing or rendering functions. The available functions only manage the
    data and set of the context.

    Contexts are optionally populated by:
        1. a default context (default_context class attribute).
           Mutable objects from the default context are copies to new objects.
        2. a parent_context
           Mutable objects from the parent context are inserted without
           being copied into new objects.
        3. the values specified.

    The latter entries take precedence over the earlier entries.

    Parameters
    ----------
    parent_context : dict, optional
        A parent or template context to (deep)copy values from.
    *args, **kwargs : tuple and dict
        The entries to populate in the context dict.
    """

    __slots__ = ()  # A __dict__ attribute would be redundant

    #: A listing of entry keys and the types they should be
    validation_types = dict()

    default_context = None

    #: The following are context entries that should not be copied (inherited)
    #: from the parent context.
    do_not_inherit = set()

    #: The following are context entries that should not be removed when the
    #: context is cleared.
    exclude_from_clear = set()

    def __init__(self, *args, **kwargs):
        # Get optional parameters
        if 'parent_context' in kwargs and kwargs['parent_context'] is not None:
            parent_context = kwargs['parent_context']
        else:
            parent_context = dict()

        # Store the parent context
        self.parent_context = parent_context

        # Reset the dict with the default_context and parent_context values
        self.reset()

        # Copy in the specified arguments. These should override those in the
        # parent_context
        self.update(*args, **kwargs)

    @property
    def parent_context(self):
        return self['_parent_context']

    @parent_context.setter
    def parent_context(self, value):
        self['_parent_context'] = value

    def reset(self):
        """(Selectively) resets the context.

        The context is reset by removing items with keys not specified in the
        'exclude_from_clear' class attribute, then repopulating the dict with
        values from the default context and and parent_context.
        """
        keys_to_remove = (self.keys() -
                          self.exclude_from_clear - {'_parent_context'})

        for k in keys_to_remove:
            del self[k]

        # Copy over the default context. This is a deep copy since mutables
        # in the settings should not be changed.
        if self.default_context:
            self.update(**deepcopy(self.default_context))

        # Copy from the parent_context. We want to conduct a shalow copy
        # since this context will use the same objects as the parent_context.
        # (exclude entries listed in the do_not_inherit attribute.
        self.update({k: v for k, v in self.parent_context.items()
                     if k not in self.do_not_inherit})

    def is_valid(self, must_exist=True):
        """Validate the entries in the context dict.

        This function checks that the keys denoted by the validate_types
        class attribute match the corresponding types for its values.

        Parameters
        ----------
        must_exist : bool, optional
            If True (default), then the entry must also exist in addition to
            having the correct type.
            If False, then entries can be missing in this dict that are listed
            in the validate_types class attribute.

        Returns
        -------
        validated : bool
            True if the context is valid.
            False if the context is not valid
        """
        for key, value_type in self.validation_types.items():
            if key not in self:
                if must_exist:
                    return False
                continue

            valid_entry = isinstance(self[key], value_type)
            if value_type is not None and not valid_entry:
                return False

        return True
