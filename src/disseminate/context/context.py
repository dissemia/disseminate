"""
The base class for Context objects that include functions to validate a context.
"""
import logging
from copy import deepcopy
from pprint import pprint

from ..utils.classes import all_attributes_values
from ..utils.string import str_to_dict, str_to_list


class BaseContext(dict):
    """A context dict with entries used for rendering target documents.

    Contexts are suppose to be data containers--i.e. there are no sophisticated
    processing or rendering functions. The available functions only manage the
    data and set of the context.

    The BaseContext is basically a heritable dict. It keeps track of dict
    lineage and initial values so that it can be reset to its state when it
    was initialized.

    Entries, Copies and Reset
    -------------------------

    Contexts are optionally populated by:
        1. a default_context (default_context class attribute)
           Values are deep copied, unless specified by the 'shallow_copy'
           attribute set.
        2. a parent_context
           Values are deep copied, unless specified by the 'shallow_copy'
           attribute set.
        3. initial values
           Values are preserved (i.e. shallow copied)

    The latter entries take precedence over the earlier entries.

    By default, objects are (deep) copied from the default_context and
    parent_context so that changes to their values from this context dict will
    not impact the original. However, keys listed in the 'shallow_copy'
    attribute set will be shallow copied.

    Why is this done? The default and parent contexts may contain mutables,
    like lists, which should not be changed from their original values by
    contexts that inherit values from these. These mutables may include dicts,
    or sets, which have no immutable alternative.

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

    #: The following are keys for entries that are shallow copied, instead of
    #: deep copied (default) from the parent_context or initial_values. This
    #: is typically used for objects that are shared between many contexts in
    #: a project.
    shallow_copy = set()

    def __init__(self, parent_context=None, *args, **kwargs):
        super().__init__()

        # Store the parent context
        parent_context = (dict() if parent_context is None else
                          dict(parent_context))
        self['_parent_context'] = parent_context

        # Store the initial values
        initial_values = dict(*args, **kwargs)
        self['_initial_values'] = initial_values

        # Reset the dict with the default_context and parent_context values
        self.reset()

    def update(self, other=None, only_shallow=False, **kwargs):
        """Update this context dict with other.

        This method behaves differently than the standard dict update method as
        it creates deep copies of values, by default, or shallow copies for
        items listed in self.shallow_copy

        Parameters
        ----------
        other : tuple of 2-ples
            The itemized list of entries to add.
        kwargs : dict
            The dictionary with values to add.
        only_shallow : bool, optional
            If True, all items will be shallow copied. Otherwise, shallow and
            deep copies will be created according to self.shallow_copy.
        """
        # Get a list of keys for items that should be shallow copied
        shallow_copy = all_attributes_values(cls=self.__class__,
                                             attribute='shallow_copy')

        # Convert other, if needed
        if other is not None:
            kwargs.update(other)

        shallow_copies = {k: v for k, v in kwargs.items()
                          if k in shallow_copy}

        if not only_shallow:
            deep_copies = {k: deepcopy(v) for k, v in kwargs.items()
                           if k not in shallow_copy}
        else:
            deep_copies = {k: v for k, v in kwargs.items()
                           if k not in shallow_copy}

        for d in (shallow_copies, deep_copies):
            for k, v in d.items():
                self[k] = v

    def reset(self):
        """(Selectively) resets the context to its initial state.

        The context is reset by removing items with keys not specified in the
        'exclude_from_clear' class attribute, then repopulating the dict with
        values from the default context and and parent_context.

        By default, entries are deep copies from the default_context and
        parent_context. (see :meth:`update
        <disseminate.context.context.BaseContext.update>`). Values from the
        initial_values are shallow copies. Interim changes to the
        default_context or parent_context  mutables in the initial values will
        be included in the reset context.

        Examples
        --------
        >>> l1, l2 = [], []
        >>> context = BaseContext(l1=l1)
        >>> context['l2'] = l2
        >>> context['l1'].append(1)
        >>> context['l2'].append(2)
        >>> context.reset()
        >>> context['l1'] == [1]
        True
        >>> 'l2' in context
        False
        """
        # The first step is to remove all entries except those listed in
        # the 'exclude_from_reset' attributes.

        # Get a set of keys to exclude from reset from this class and
        # subclasses, and exclude these from the keys to remove
        parent_attrs = all_attributes_values(cls=self.__class__,
                                             attribute='exclude_from_reset')
        keys_to_remove = self.keys() - self.exclude_from_reset
        keys_to_remove -= set(parent_attrs)

        # Now remove the entries that are remaining
        for k in keys_to_remove:
            del self[k]

        # Copy over the default context. This update method produces deep and
        # shallow copies. See :meth:`BaseContext.update`.
        if self.default_context:
            self.update(self.default_context)

        # Copy from the parent_context. Use all entries in the parent_context,
        # except for those listed in the 'do_not_inherit' attribute sets of
        # this class and subclasses.
        parent_attrs = all_attributes_values(cls=self.__class__,
                                             attribute='do_not_inherit')
        keys_to_inherit = self['_parent_context'].keys() - self.do_not_inherit
        keys_to_inherit -= set(parent_attrs)

        # This update method produces deep and shallow copies. See
        # :meth:`BaseContext.update`.
        self.update({key: self['_parent_context'][key]
                     for key in keys_to_inherit})

        # Copy in the initial value arguments.
        self.update(self['_initial_values'], only_shallow=True)

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

    def recursive_update(self, changes):
        """Update this base context dict with the entries listed in the given
        changes dict.

        The recursive update only updates entries for matching types and appends
        to nested mutables, like lists and dicts.

        1. 'Hidden' entries with keys that start with an underscore ('_') are
           skipped.
        2. New entries in 'changes' are copied over 'as-is' to this dict.
        3. Lists entries in this dict are append to from the changes dict.
           If these are strings in the changes dict, they  are first converted
           to lists. Items are added to the front.
        4. Dict entries in this dict are append to from the changes dict.
           If these are strings in the changes dict, they  are first converted
           to a dict. The update is recursive by applying this function to
           that dict.
        5. Other immutables, like ints and floats, are copied over to this dict
           if the corresponding entry in the changes dict can be converted to
           an int or float. Otherwise, they're skipped.
        6. String entries are copied from changes to this dict if the dict's
           entry is also a string.
        """
        changes = str_to_dict(changes) if isinstance(changes, str) else changes

        self._recursive_update(original=self, changes=changes)

    @staticmethod
    def _recursive_update(original, changes,):
        assert isinstance(original, dict) and isinstance(changes, dict)

        for key, change_value in changes.items():
            # Skip hidden keys
            if key.startswith('_'):
                continue

            # Copy values that are not in the original
            if key not in original:
                original[key] = change_value
                continue

            # Now copy over values based on the type of the original's value
            original_value = original[key]

            # For list entries, convert strings to a list and append the
            # items to the original's list.
            if isinstance(original_value, list):
                change_value = (str_to_list(change_value)
                                if isinstance(change_value, str) else
                                list(change_value))
                new_list = change_value +original_value
                # original_value += change_value
                original_value.clear()
                original_value += new_list

            # For dict entries, convert strings to a dict and append the
            # items to the original's dict.
            elif isinstance(original_value, dict):
                change_value = (str_to_dict(change_value)
                                if isinstance(change_value, str) else
                                dict(change_value))
                BaseContext._recursive_update(original=original_value,
                                              changes=change_value)

            # For immutable types, like ints, covert strings into their
            # proper format and replace the original's value
            elif isinstance(original_value, int):
                try:
                    original[key] = int(change_value)
                except ValueError:
                    pass

            elif isinstance(original_value, float):
                try:
                    original[key] = float(change_value)
                except ValueError:
                    pass

            # Otherwise, if the original value's type and change value type
            # match, like for strings, just replace the original's value
            elif type(original_value) == type(change_value):
                original[key] = change_value

    def print(self):
        """Pretty print this context"""
        pprint(self)
