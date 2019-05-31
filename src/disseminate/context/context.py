"""
The base class for Context objects that include functions to validate a context.
"""
import logging
from pprint import pprint
from weakref import ref

import regex

from .. import settings
from ..utils.classes import all_attributes_values
from ..utils.string import str_to_dict, str_to_list


re_header_block = regex.compile(r'^[\s\n]*(-{3,})\s*\n'
                                r'(?P<header>.+?)'
                                r'(\n\s*\g<1>)\n?', regex.DOTALL)


class ContextException(Exception):
    pass


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
    parent_context : Optional[dict]
        A parent or template context.
    *args, **kwargs : tuple and dict
        The entries to populate in the context dict.

    Attributes
    ----------
    validation_types : Dict[str, type]
        A listing of entry keys and the types they should be.
        If None is listed as the type, then a type check will not be conducted.
    parent : :obj:`BaseContext <.context.BaseContext>`
        A weakref to a BaseContext of a parent document.
    do_not_inherit : Set[str]
        The context keys that should not be accessed (inherited) from the
        parent context.
    exclude_from_reset : Set[str]
        The context entries that should not be removed when the context is
        reset.

    Entries
    -------
    _initial_values : dict
        A dict containing the initial values. Since this starts with an
        underscore, it is hidden when listing keys with the keys() function.
    _parent_context : :obj:`Type[BaseContext] <.BaseContext>`
        A dict containing the parent context from which values may be inherited.
        Since this starts with an underscore, it is hidden when listing keys
        with the keys() function.
    """

    __slots__ = ('__weakref__',)  # A __dict__ attribute would be redundant

    validation_types = dict()

    do_not_inherit = {'_initial_values', '_parent_context'}
    exclude_from_reset = {'_parent_context', '_initial_values'}

    _do_not_inherit = None

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
        return (self.__class__.__name__ + '{' +
                ', '.join('{}: {}'.format(k, self[k])
                          for k in self.keys(only_self=True)) +
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
            do_not_inherit = self.find_do_not_inherit()

            if (key not in do_not_inherit and parent is not None and
               key in parent):
                val = parent[key]
                return val
        return default

    def keys(self, only_self=False, hidden_prefix='_'):
        """The keys for this context dict.

        Parameters
        ----------
        only_self : Optional[bool]
            If True, only keys for entries in this context dict will be
            returned. Otherwise, keys for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : Optional[str]
            If specified, keys that start with this character or these
            characters will be considered hidden and not returned.

        Returns
        -------
        keys : set
            A set of keys for the context dict.
        """
        keys = {k for k in super().keys() if not isinstance(k, str) or
                not k.startswith(hidden_prefix)}

        if not only_self:
            # If not only self, get the keys from the parent context as well.
            # This method should remove hidden keys as well if the parent
            # context is a BaseContext.
            parent = self.parent_context
            other_keys = parent.keys() if isinstance(parent, dict) else set()

            # Do not include keys that should not be inherited
            do_not_inherit = self.find_do_not_inherit()
            other_keys -= do_not_inherit

            # Add the remaining keys to the key listing
            keys |= other_keys

        # Return keys and remove hidden keys
        return keys

    def values(self, only_self=False, hidden_prefix='_'):
        """The values for this context dict.

        Parameters
        ----------
        only_self : Optional[bool]
            If True, only values for entries in this context dict will be
            returned. Otherwise, values for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : Optional[str]
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
        only_self : Optional[bool]
            If True, only items for entries in this context dict will be
            returned. Otherwise, items for this context dict and all parent
            context dicts will be returned.
        hidden_prefix : Optional[str]
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
        only_self : Optional[bool]
            If True, the number of entries only in this context dict will be
            returned. Otherwise, the number of entries this context dict
            and all parent context dicts will be returned.
        hidden_prefix : Optional[str]
            If specified, keys that start with this character or these
            characters will be considered hidden and not included in the count.

        Returns
        -------
        length : int
            The number of entries in the context dict.
        """
        return len(self.keys(only_self=only_self, hidden_prefix=hidden_prefix))

    @classmethod
    def find_do_not_inherit(cls):
        if cls.__dict__.get('_do_not_inherit') is None:
            do_not_inherit = all_attributes_values(cls=cls,
                                                   attribute='do_not_inherit')
            cls._do_not_inherit = set(do_not_inherit)
        return cls._do_not_inherit

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

    def load(self, string, strip_header=True):
        """Load context entries from a string.

        The load function interprets a string containing a dict in the format
        processed by :func:`str_to_dict <disseminate.utils.string.str_to_dict>`.
        Additionally, this function parses header portions of strings
        delineated by 3 or more '-' characters, and only new entries entries
        that match the types of existing entries are inserted.

        Parameters
        ----------
        string : str
            The string to load into this context.
        strip_header : Optional[bool]
            If True (default), the returned string will have the header
            removed.

        Returns
        -------
        string : str
            The processed string with the header removed (if available) or just
            the string passed as an argument.

        Examples
        --------
        >>> context = BaseContext()
        >>> context.load('test: 1')
        >>> print(context)
        BaseContext{test: 1}
        """
        # Pull out the header string, if available
        m = re_header_block.match(string)
        rest = None
        if m is not None:
            # Determine the start and end position of the header
            start, end = m.span()

            # Collect the rest of the string
            rest = string[end:]

            # Get the header part of the string
            string = m.groupdict()['header']

        # Parse the string
        d = str_to_dict(string)

        # update self
        self.matched_update(d)

        return rest if rest is not None and strip_header else string

    def reset(self):
        """(Selectively) resets the context to its initial state.

        The context is reset by removing items with keys not specified in the
        'exclude_from_clear' class attribute.

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
        keys : Optional[Tuple[str]]
            If specified, only the given keys will be checked if they're in
            the validate_types class attribute. Otherwise all validate_types
            will be checked.
        must_exist : Optional[bool]
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

    def matched_update(self, changes, overwrite=True):
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

        Parameters
        ----------
        changes : Union[str, dict, :obj:`BaseContext <.context.BaseContext>`]
            The changes to include in updating this context dict.
        overwrite : Optional[bool]
            If True, overwrite existing entries, if they already exist.
            If False, do not overwrite existing entries.
        """
        changes = str_to_dict(changes) if isinstance(changes, str) else changes
        self._match_update(original=self, changes=changes, overwrite=overwrite)

    @staticmethod
    def _match_update(original, changes, overwrite, level=1):
        assert isinstance(original, dict) and isinstance(changes, dict)

        # Make sure the context isn't too deeply nested
        if level >= settings.context_max_depth:
            msg = "Context cannot exceed a depth of {}."
            raise ContextException(msg.format(settings.context_max_depth))

        # Get a list of keys that are only in the original (not including keys
        # from the parent_context)
        original_self_keys = (original.keys(only_self=True)
                              if isinstance(original, BaseContext) else
                              original.keys())

        for key, change_value in changes.items():
            # Skip hidden keys
            if key.startswith('_'):
                continue

            # Copy values that are not in the original--whether the key is
            # actually in the original or in the parent_context
            if key not in original.keys():
                original[key] = change_value
                continue

            # If the entry already exists, but not in the local (self) keys
            # and it shouldn't be overwritten, just skip the rest of the
            # processing
            if key in original_self_keys and not overwrite:
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
                original[key] = new_list

            # For list entries, convert strings to a list and append the
            # items to the original's list.
            elif isinstance(original_value, set):
                change_value = (str_to_list(change_value)
                                if isinstance(change_value, str) else
                                list(change_value))
                new_set = original_value.union(change_value)
                original[key] = new_set

            # For dict entries, convert strings to a dict and append the
            # items to the original's dict.
            elif isinstance(original_value, dict):
                change_value = (str_to_dict(change_value)
                                if isinstance(change_value, str) else
                                dict(change_value))
                original_copy = original_value.copy()

                # match update the dict. Since original_copy is a copy,
                # we can overwrite entries
                BaseContext._match_update(original=original_copy,
                                          changes=change_value,
                                          overwrite=True,
                                          level=level+1)
                original[key] = original_copy

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
