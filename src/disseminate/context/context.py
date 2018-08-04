"""
Context objects.
"""
import logging
from copy import deepcopy
from pprint import pprint

from ..utils.classes import all_parent_attributes


class BaseContext(dict):
    """A context object with variables used for rendering target documents.

    Contexts are suppose to be data containers--i.e. there are no sophisticated
    processing or rendering functions. The available functions only manage the
    data and set of the context.

    The BaseContext is basically a heritable dict. It keeps track of dict
    lineage and initial values so that it can be reset to its state when it
    was initialized.

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
    do_not_inherit = {'_parent_context', '_initial_values'}

    #: The following are context entries that should not be removed when the
    #: context is reset.
    exclude_from_reset = {'_parent_context', '_initial_values'}

    def __init__(self, parent_context=None, *args, **kwargs):
        # Store the parent context
        parent_context = (dict() if parent_context is None else
                          dict(parent_context))
        self['_parent_context'] = parent_context

        # Store the initial values
        initial_values = dict(*args, **kwargs)
        self['_initial_values'] = initial_values

        # Reset the dict with the default_context and parent_context values
        self.reset()

    def reset(self):
        """(Selectively) resets the context.

        The context is reset by removing items with keys not specified in the
        'exclude_from_clear' class attribute, then repopulating the dict with
        values from the default context and and parent_context.
        """
        # Get a set of keys to remove from the current class and all parent
        # classes
        parent_attrs = all_parent_attributes(cls=self.__class__,
                                             attribute='exclude_from_reset')
        keys_to_remove = self.keys() - self.exclude_from_reset

        for attr in parent_attrs:
            keys_to_remove -= attr

        # Now remove the entries that are remaining
        for k in keys_to_remove:
            del self[k]

        # Copy over the default context. This is a deep copy since mutables
        # in the settings should not be changed.
        if self.default_context:
            self.update(**deepcopy(self.default_context))

        # Copy from the parent_context. We want to conduct a shallow copy
        # since this context will use the same objects as the parent_context.
        # (exclude entries listed in the do_not_inherit attribute for this
        # class and all parent classes).
        parent_attrs = all_parent_attributes(cls=self.__class__,
                                             attribute='do_not_inherit')
        keys_to_inherit = self['_parent_context'].keys() - self.do_not_inherit

        for attr in parent_attrs:
            keys_to_inherit -= attr

        self.update({key: self['_parent_context'][key]
                     for key in keys_to_inherit})

        # Copy in the initial value arguments
        initial_values = self['_initial_values']
        self.update(**initial_values)

    def is_valid(self, *keys, must_exist=True):
        """Validate the entries in the context dict.

        This function checks that the keys denoted by the validate_types
        class attribute match the corresponding types for its values.

        Parameters
        ----------
        keys : tuple of str, optional
            If specified, only the given keys will be checked if they're in
            the validate_types class attribute. Otherwise all validate_types
            will be checked.
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

        # Determine which keys to use. Use all validation keys, if not keys
        # were given
        keys = self.validation_types.keys() if len(keys) == 0 else keys

        for key in keys:
            if key not in self:
                msg = "The key '{}' could not be found in the context."
                logging.debug(msg.format(key))

                if must_exist:
                    return False
                continue

            value_type = self.validation_types.get(key, None)

            if value_type is not None:
                valid_entry = isinstance(self[key], value_type)
                if value_type is not None and not valid_entry:
                    msg = ("The key '{}' has a value '{}' that is not valid; a "
                           "value type of '{}' is expected.")
                    logging.debug(msg.format(key, self[key], value_type))

                    return False

        return True

    def print(self):
        """Pretty print this context"""
        pprint(self)
