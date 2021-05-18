"""
The base class for Context objects that include functions to validate a
context.
"""
import logging
from pprint import pprint
from weakref import ref

from .utils import load_from_string
from ..tags import Tag
from ..utils.classes import all_attributes_values
from ..utils.string import str_to_dict, str_to_list
from .. import settings


class ContextException(Exception):
    """An exception raised when processing a BaseContext"""
    pass


class BaseContext(dict):
    """A context dict with entries used for rendering target documents.

    Contexts are suppose to be data container dicts--i.e. there are no
    sophisticated processing or rendering functions. The available functions
    only manage the data and set of the context.

    The BaseContext is basically a heritable dict. It keeps track of dict
    lineage and initial values so that it can be reset to its initialized
    state.

    .. note:: I've tried different implementations, including a ChainMap-like
              inheritance. The problem with these is that key lookup and
              __contains__ lookup are relatively slow, compared to a standard
              dict. For this reason, I've decided to implement the BaseContext
              as a simple dict with values copied from a parent_context. The
              downside of this approach is that it's more memory intensive, but
              this is mitigated to a great extended from creating shallow
              copies or weak references of parent_context entries.

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
    replace : Set[str]
        The *muttable* context entries that should be replaced, rather than
        appended, from the parent context.
    _initial_values : dict
        A dict containing the initial values. Since this starts with an
        underscore, it is hidden when listing keys with the keys() function.
    _parent_context : :obj:`Type[BaseContext] <.BaseContext>`
        A dict containing the parent context from which values may be
        inherited. Since this starts with an underscore, it is hidden when
        listing keys with the keys() function.

    Examples
    --------
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
    >>> child['b']
    [1]
    >>> parent['b']
    []
    """

    # A __dict__ attribute would be redundant
    __slots__ = ('__weakref__', '_parent_context', 'initial_values')

    validation_types = dict()

    do_not_inherit = set()
    exclude_from_reset = set()
    replace = set()

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
        self.initial_values = initial_values

        # Reset the dict with the default_context and parent_context values
        self.reset()

    def __repr__(self):
        return (self.__class__.__name__ + '{' +
                ', '.join('{}: {}'.format(k, self[k])
                          for k in self.keys()) +
                '}')

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        # Copy over the entries for this context dict
        result.update(self)

        # Copy over the parent_context and initial_values
        result.parent_context = self.parent_context
        result.initial_values = self.initial_values

        return result

    @classmethod
    def find_do_not_inherit(cls):
        """Retrieve a union set for the do_not_inherit attribute of this class
        and all parent classes.

        Returns
        -------
        do_not_inherit : Set[str]
            A set of all attributes that should not be inherited by child class
            instances.
        """
        if cls.__dict__.get('_do_not_inherit') is None:
            do_not_inherit = all_attributes_values(cls=cls,
                                                   attribute='do_not_inherit')
            cls._do_not_inherit = set(do_not_inherit)
        return cls._do_not_inherit

    @property
    def parent_context(self):
        """The parent context."""
        # Try to get the keys from the parent context
        parent = getattr(self, '_parent_context', None)

        # dereference the parent, if needed
        if parent is not None:
            parent = parent() if isinstance(parent, ref) else parent

        return parent

    @parent_context.setter
    def parent_context(self, parent):
        # Set the parent_context in self's dict. Create a weakref, if able
        # to do so, because this context does not own the parent_context
        self._parent_context = (ref(parent)
                                if hasattr(parent, '__weakref__') else
                                parent)

    def load(self, string, strip_header=True, overwrite=True):
        """Load context entries from a string.

        The load function interprets a string containing a dict in the format
        processed by :func:`str_to_dict
        <disseminate.utils.string.str_to_dict>`. Additionally, this function
        parses header portions of strings delineated by 3 or more '-'
        characters, and only new entries entries that match the types of
        existing entries are inserted.

        Parameters
        ----------
        string : str
            The string to load into this context.
        strip_header : Optional[bool]
            If True (default), the returned string will have the header
            removed.
        overwrite : Optional[bool]
            If True, allow existing entries in self to be overwritten by
            changes.

        Returns
        -------
        string : str
            The processed string with the header removed (if available) or just
            the string passed as an argument.

        Examples
        --------
        >>> context = BaseContext()
        >>> rest = context.load('test: 1')
        >>> print(context)
        BaseContext{test: 1}
        """
        # Process the header block into a dict
        rest, d = load_from_string(string)

        # update self with the dict entries
        self.match_update(changes=d, overwrite=overwrite)

        return rest if rest is not None and strip_header else string

    def reset(self):
        """(Selectively) resets the context to its initial state.

        The context is reset by removing items with keys not specified in the
        'exclude_from_clear' class attribute.

        .. note:: Entries in the parent_context are copied to this context.
                  If the parent_context entry is a mutable, like a list or
                  dict, then a copy of that mutable is created if a 'copy'
                  method exists for that mutable. However, mutables within
                  those mutables will still point to the original.

        Examples
        --------
        >>> l1, l2 = ['a'], ['b']
        >>> context = BaseContext(l1=l1)
        >>> context['l2'] = l2
        >>> context['l1'].append(1)
        >>> context['l2'].append(2)
        >>> context.reset()
        >>> context['l1'] == ['a']  # reset to original l1
        True
        >>> 'l2' in context
        False
        """
        # 1. The first step is to remove all entries except those listed in
        #    the 'exclude_from_reset' attributes.

        # Get a set of keys to exclude from reset from this class and
        # subclasses, and exclude these from the keys to remove
        exclude = all_attributes_values(cls=self.__class__,
                                        attribute='exclude_from_reset')
        keys_to_remove = self.keys() - exclude

        # Now remove the entries that are remaining
        for k in keys_to_remove:
            del self[k]

        # Copy in the parent value arguments, except those that shouldn't
        # be inherited
        parent_context = self.parent_context
        if parent_context is not None:
            do_not_inherit = self.find_do_not_inherit()
            keys_to_inherit = parent_context.keys() - do_not_inherit
            self.match_update(parent_context, keys=keys_to_inherit)

        # Copy in the initial value arguments. The initial values should
        # not be modified, so copies of mutabes are created
        self.match_update(changes=self.initial_values)

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
                    msg = ("The key '{}' has a value '{}' that is not valid; "
                           "a value type of '{}' is expected.")
                    logging.debug(msg.format(key, self[key], value_type))

                    return False

        return True

    def match_update(self, changes, keys=None, overwrite=True, level=1):
        """Update this context dict with changes by matching entry types.

        Matched update behaves like a dict's update method with these key
        differences:

        1. If changes is a string, it is first converted to a dict.
        2. Existing entries from changes are converted to the same type as the
           value in this dict. See examples below.
        3. Mutable values are deep copied from the changes dict.

        Parameters
        ----------
        changes : Union[str, dict, :obj:`.BaseContext`]
            The changes to update into this context dict.
        keys : Optional[Iterable[str]]
            If specified, only update the given keys
        overwrite : Optional[bool]
            If True, allow existing entries in self to be overwritten by
            changes.
        level : Optional[int]
            The level of recursion for this function.

        Notes
        -----
        The matched update only updates entries for matching types and appends
        to nested mutables, like lists and dicts.

        1. New entries from 'changes' are copied

           a. If the change's value has a 'copy' method, a copy is created
              with that method
           b. Otherwise, the value is copied directly

        2. Existing entries are converted to the type of the value in this
           context dict.

           a. Lists, sets and dicts: A copy of the changes value is converted
              to the respective type and appended to this context dict's list,
              set or dict.
           b. Immutables are converted and added directly.

        Examples
        --------
        >>> orig = BaseContext(test = [])
        >>> orig.match_update(changes={'test': 'test'})
        >>> orig['test']
        ['test']
        >>> orig.match_update(changes={'test': 'more changes'})
        >>> orig['test']
        ['more changes', 'test']
        """
        # When first invoking this function, 'changes' may simply be a string
        # in YAML format. If so, convert it to a dict to pull values from
        if level == 1 and isinstance(changes, str):
            changes = str_to_dict(changes)

        # Make sure the context isn't too deeply nested
        if level >= settings.context_max_depth:
            msg = "Context cannot exceed a depth of {}."
            raise ContextException(msg.format(settings.context_max_depth))

        # Select the keys for entries to copy over
        keys = changes.keys() if keys is None else keys

        # Copy the entries in the changes dict one-by-one
        for key in keys:
            if key not in changes:
                # Skip if the key is not found in changes
                continue

            change_value = changes[key]

            # 1. *Missing entries*. Copy values that are not in the
            #    original--whether the key is actually in the original or in
            #    the parent_context
            if key not in self.keys():
                try:
                    # Try making a copy. Some objects, like tags, take a
                    # new_context parameter to set the new context in the
                    # created object
                    self[key] = change_value.copy(new_context=self)

                except TypeError:
                    # Other objects, like dicts, have a copy method to create
                    # a shallow copy, but these do not accept keyword arguments
                    self[key] = change_value.copy()
                except AttributeError:
                    # Otherwise reference the value directly, like immutables
                    self[key] = change_value
                continue

            # At this point, the key already exists in self. If overwrite is
            # not enabled, then don't do anything else (i.e. don't overwrite)
            if not overwrite:
                continue

            # Now copy over changed values based on the type of the original
            # value's type
            original_value = self[key]

            # Clear the original_value if this value should be replaced
            if key in getattr(self, 'replace', set()):
                try:
                    original_value.clear()
                except AttributeError:
                    msg = ("The context entry '{}' is of type '{}', and it "
                           "cannot be cleared for replacement.")
                    logging.warning(msg.format(original_value,
                                               type(original_value)))

            # 2. *lists*. Create a copy from changes
            if isinstance(original_value, list):
                change_value = (str_to_list(change_value)
                                if isinstance(change_value, str) else
                                list(change_value))
                original_value[0:0] = change_value  # prepend to top

            # 3. *sets*. Create a copy from changes
            elif isinstance(original_value, set):
                change_value = (str_to_list(change_value)
                                if isinstance(change_value, str) else
                                list(change_value))
                original_value |= set(change_value)

            # 4. *dicts*. Create a copy from changes
            elif isinstance(original_value, dict):
                change_value = (str_to_dict(change_value)
                                if isinstance(change_value, str) else
                                dict(change_value))
                BaseContext.match_update(self=original_value,
                                         changes=change_value,
                                         level=level + 1)

            # 5. *tags*. Create a copy
            elif isinstance(original_value, Tag):
                if isinstance(change_value, str):
                    # If the change_value is a string, then convert it to
                    # a tag of the same type
                    tag_cls = original_value.__class__
                    tag = tag_cls(name=key, content=change_value,
                                  attributes='', context=self)
                elif isinstance(change_value, Tag):
                    tag = change_value.copy(new_context=self)
                else:
                    # Do nothing if the change value is neither a tag or a
                    # string, as this cannot be converted
                    continue
                self[key] = tag

            # For immutable types, like ints, covert strings into their
            # proper format and replace the original's value
            elif isinstance(original_value, bool):
                change_value_lower = change_value.lower().strip()
                if change_value_lower == 'false':
                    self[key] = False
                elif change_value_lower == 'true':
                    self[key] = True

            elif isinstance(original_value, int):
                try:
                    self[key] = int(change_value)
                except ValueError:
                    pass

            elif isinstance(original_value, float):
                try:
                    self[key] = float(change_value)
                except ValueError:
                    pass

            # Otherwise, if the original value's type and change value type
            # match, like for strings, just replace the original's value
            elif type(original_value) == type(change_value):
                self[key] = change_value

    def filter(self, keys):
        """Create a new context with the entries copied for the given keys.

        Parameters
        ----------
        keys : Iterable[str]
            The keys for entries to include in the returned filtered
            BaseContext

        Returns
        -------
        copy : :obj:`.context.BaseContext`
            The filtered copy of the BaseContext.
        """
        # Create an empty copy
        cls = self.__class__
        copy = cls.__new__(cls)

        # Update the copy with the values specified by keys
        copy.match_update(changes=self, keys=keys)
        return copy

    def print(self):
        """Pretty print this context"""
        pprint(self)
