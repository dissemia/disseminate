"""
The base class for Context objects that include functions to validate a context.
"""
import logging
from pprint import pprint
from weakref import ref

from ..utils.classes import all_attributes_values
from ..utils.string import str_to_dict, str_to_list


class BaseContext(dict):
    """A context dict with entries used for rendering target documents.

    Contexts are suppose to be data container dicts--i.e. there are no
    sophisticated processing or rendering functions. The available functions
    only manage the data and set of the context.

    The BaseContext is basically a heritable dict. It keeps track of dict
    lineage and initial values so that it can be reset to its initialized state.

    Contexts, by default, access the entries from a parent_context. New entries
    that match parent_context entry will shadow that value. However, accessing
    parent_context entries of mutables and changing those will change the
    parent_context's mutable values.

    >>> parent = BaseContext(a=1, b=[])
    >>> child = BaseContext(parent_context=parent)
    >>> child['a']
    1
    >>> child['a'] = 2
    >>> child['a']
    2
    >>> parent['a']
    1
    >>> child['b'].append(1)
    >>> parent['b']
    [1]
    >>> child['b'] = []
    >>> child['b'].append(2)
    >>> parent['b']
    [1]

    Parameters
    ----------
    parent_context : dict, optional
        A parent or template context to (deep)copy values from.
    *args, **kwargs : tuple and dict
        The entries to populate in the context dict.

    Attributes
    ----------
    validation_types : dict
        A listing of entry keys and the types they should be.
    parent : :obj:'BaseContext <disseminate.context.BaseContext>'
        A weakref to a BaseContext of a parent document.
    do_not_inherit : set
        The context entries that should not be accessed (inherited)
        from the parent context.
    exclude_from_reset : set
        The context entries that should not be removed when the
        context is reset.

    Entries
    -------
    _initial_values : dict
        A dict containing the initial values. Since this starts with an
        underscore, it is hidden when listing keys with the keys() function.
    _parent_context : dict
        A dict containing the parent context from which values may be inherited.
        Since this starts with an underscore, it is hidden when listing keys
        with the keys() function.
    """

    __slots__ = ('__weakref__',)  # A __dict__ attribute would be redundant

    validation_types = dict()

    do_not_inherit = {'_initial_values', '_parent_context'}
    exclude_from_reset = {'_parent_context', '_initial_values'}

    def __init__(self, *args, **kwargs):
        super().__init__()

        kwargs.update(*args)

        # Remove protected keys
        for k in {'_parent_context', '_initial_values'}:
            if k in kwargs:
                del kwargs[k]

        # Store the parent context
        if 'parent_context' in kwargs:
            parent = kwargs.get('parent_context', None)
            del kwargs['parent_context']

            self.parent_context = parent

        # Store the initial values
        initial_values = dict(*args, **kwargs)
        self['_initial_values'] = initial_values

        # Reset the dict with the default_context and parent_context values
        self.reset()

    def __getitem__(self, key):
        val = self.get(key)
        if val is None:
            raise KeyError
        else:
            return val

    def __contains__(self, key):
        return key in self.keys()

    def __len__(self):
        return self.len()

    def __iter__(self):
        return iter(self.keys())

    def __repr__(self):
        return ('{' +
                ', '.join('{}: {}'.format(k, self[k]) for k in self.keys()) +
                '}')

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        # Copy over the entries for this context dict
        for key in self.keys(only_self=True):
            result[key] = self[key]

        # Copy over the parent_context and initial_values
        for key in ['_initial_values', '_parent_context']:
            try:
                result[key] = self[key]
            except KeyError:
                continue
        return result

    def get(self, key, default=None):
        try:
            val = super().__getitem__(key)
            return val
        except KeyError as e:
            parent = self.parent_context

            # Get all do_not_inherit values for this class and child classes
            do_not_inherit = all_attributes_values(cls=self.__class__,
                                                   attribute='do_not_inherit')

            if (key not in do_not_inherit and parent is not None and
               key in parent):
                val = parent[key]
                return val
        return default

    def keys(self, only_self=False, hidden_prefix='_'):
        """The keys for this context dict.

        Parameters
        ----------
        only_self : bool, optional
            If True, only keys for entries in this context dict will be
            returned. Otherwise, keys for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : str, optional
            If specified, keys that start with this character or these
            characters will be considered hidden and not returned.

        Returns
        -------
        keys : set
            A set of keys for the context dict.
        """
        # Get the keys for this context dict without hidden keys--i.e. those
        # that start with an underscore '_'.
        if isinstance(hidden_prefix, str):
            keys = {k for k in super().keys()
                    if not k.startswith(hidden_prefix)}
        else:
            keys = super().keys()

        if not only_self:
            # Try to get the keys from the parent context
            parent = self.parent_context

            # Get all do_not_inherit values for this class and child classes
            do_not_inherit = all_attributes_values(cls=self.__class__,
                                                   attribute='do_not_inherit')

            # dereference the parent, if needed, and add its keys (excluding those
            # that shouldn't be inherited
            if parent is not None:
                keys |= (parent.all_keys() - do_not_inherit
                         if hasattr(parent, 'all_keys') else
                         parent.keys() - do_not_inherit)

        return keys

    def values(self, only_self=False, hidden_prefix='_'):
        """The values for this context dict.

        Parameters
        ----------
        only_self : bool, optional
            If True, only values for entries in this context dict will be
            returned. Otherwise, values for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : str, optional
            If specified, keys that start with this character or these
            characters will be considered hidden and not returned.

        Returns
        -------
        values : generator
            A generator of values for the context dict.
        """
        # Get the keys for this context dict and for its parent
        keys = self.keys(only_self=only_self, hidden_prefix=hidden_prefix)
        return (self[k] for k in keys)

    def items(self, only_self=False, hidden_prefix='_'):
        """The items for this context dict.

        Parameters
        ----------
        only_self : bool, optional
            If True, only items for entries in this context dict will be
            returned. Otherwise, items for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : str, optional
            If specified, keys that start with this character or these
            characters will be considered hidden and not returned.

        Returns
        -------
        items : generator
            A generator of items for the context dict.
        """
        keys = self.keys(only_self=only_self, hidden_prefix=hidden_prefix)
        return ((k, self[k]) for k in keys)

    def len(self, only_self=False, hidden_prefix='_'):
        """The length (number of entries) in this context dict.

        Parameters
        ----------
        only_self : bool, optional
            If True, the number of entries only in this context dict will be
            returned. Otherwise, the number of entries this context dict
            and all parent context dicts will be returned.
        hidden_prefix : str, optional
            If specified, keys that start with this character or these
            characters will be considered hidden and not included in the count.

        Returns
        -------
        length : int
            The number of entries in the context dict.
        """
        return len(self.keys(only_self=only_self, hidden_prefix=hidden_prefix))

    @property
    def parent_context(self):
        """The parent context."""
        # Try to get the keys from the parent context
        parent = super().get('_parent_context', None)

        # dereference the parent, if needed
        if parent is not None:
            parent = parent() if isinstance(parent, ref) else parent

        return parent

    @parent_context.setter
    def parent_context(self, parent):
        # Set the parent_context in self's dict. Create a weakref, if able
        # to do so, because this context does not own the parent_context
        self['_parent_context'] = (ref(parent)
                                   if hasattr(parent, '__weakref__') else
                                   parent)

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
        attrs = all_attributes_values(cls=self.__class__,
                                      attribute='exclude_from_reset')
        keys_to_remove = self.keys(only_self=True) - self.exclude_from_reset
        keys_to_remove -= set(attrs)

        # Now remove the entries that are remaining
        for k in keys_to_remove:
            del self[k]

        # Copy in the initial value arguments.
        self.update(self['_initial_values'])

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

    def matched_update(self, changes):
        """Update with the values in the changes dict that are either missing
        in this base context dict or to match the types of existing entries in
        this base context dict.

        The matched update only updates entries for matching types and appends
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

        self._match_update(original=self, changes=changes)

    @staticmethod
    def _match_update(original, changes, ):
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
                new_list = change_value + original_value
                # original_value += change_value
                original_value.clear()
                original_value += new_list

            # For dict entries, convert strings to a dict and append the
            # items to the original's dict.
            elif isinstance(original_value, dict):
                change_value = (str_to_dict(change_value)
                                if isinstance(change_value, str) else
                                dict(change_value))
                BaseContext._match_update(original=original_value,
                                          changes=change_value)

            # For immutable types, like ints, covert strings into their
            # proper format and replace the original's value
            elif isinstance(original_value, bool):
                change_value_lower = change_value.lower().strip()
                if change_value_lower == 'false':
                    original[key] = False
                elif change_value_lower == 'true':
                    original[key] = True

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
