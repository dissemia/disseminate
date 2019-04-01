"""
Classes and methods to manage tag attributes
"""
import regex

from ..settings import attribute_target_sep


class AttributeFormatError(Exception):
    pass


class PositionalAttribute(object):
    """A placeholder value for positional arguments."""
    pass


class _MissingAttribute(object):
    """An internal object used when a key is missing"""
    pass


re_attrs = regex.compile(r'((?P<key>[\w\.]+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|[^\s\]]+))'
                         r'|(?P<position>\w+))')


class Attributes(dict):
    """The attributes class is an ordered dict to manage and validate attribute
    entries.

    .. note:: Attributes can either be key/value (ex: 'class=media') or
              positional (ex: 'red'). For positional arguments, the values
              are None. Consequently, retrieving a positional argument's value
              will return None. (ex: attr.get('red') is None)
    """

    def __init__(self, *args, **kwargs):
        for string in filter(lambda x: isinstance(x, str), args):
            self.load(string)

        # Remove strings (and None) from args
        args = tuple(filter(lambda x: not isinstance(x, str) and x is not None,
                            args))

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.__class__.__name__ + super().__repr__()

    def load(self, s):
        """Parses an attribute string into a tuple of attributes.

        Parameters
        ----------
        s: str
            Input string of attributes. Attributes come in two forms:
            positional attributes and keyword attributes (kwargs), and
            attributes strings have the following form:
            "key1=value1 key2=value2 value3"

        Returns
        -------
        attrs: tuple
            A tuple of attributes comprising either 2-ple strings (key, value) or
            strings (positional arguments)
        """
        attrs = []

        for m in re_attrs.finditer(s):
            d = m.groupdict()
            if d.get('key', None) and d.get('value', None):
                attrs.append((d['key'], d['value'].strip('"').strip("'")))
            elif d.get('position', None):
                attrs.append((d['position'].strip("'").strip('"'),
                              PositionalAttribute))

        self.update(tuple(attrs))

    def get(self, key, target=None, default=None, sep=attribute_target_sep):
        """Retrieve an entry by target-specific key, if available and
        specified, or by key.

        Parameters
        ----------
        key : str
            The key of the entry to retrieve
        target : str, optional
            If specified, search for a key for the given target.
            ex: class.html with be returned for the 'class' key and 'html'
            target, if available, otherwise, the entry for 'class' will be
            returned.
        default : object, optional
            If the key is not found, return this value instead.
        sep : str, optional
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        value
            The retrieved value.
            If the entry is a positional attribute, PositionalAttribute will be
            returned.

        Examples
        --------
        >>> attrs = Attributes('class="general" class.html="specific"')
        >>> attrs.get('class')
        'general'
        >>> attrs.get('class.html')
        'specific'
        >>> attrs.get('class', target='html')
        'specific'
        >>> attrs.get('class', target='tex')
        'general'
        >>> attrs.get('missing')
        """
        # Find the value in self
        target = target.strip('.') if isinstance(target, str) else target

        if target is not None and sep.join((key, target)) in self:
            # See if a target-specific key is availble
            return self[sep.join((key, target))]
        elif key in self:
            # Otherwise, see if the key itself is available
            return self[key]
        else:
            # When the key is not available, return the default
            return default

    def get_by_type(self, key, value_type=str, target=None, default=None,
                    sep=attribute_target_sep, raise_error=False):
        """Retrieve an entry by key and return for the given entry_type, if
        it can be converted.

        Parameters
        ----------
        key : str
            The key of the entry to retrieve
        value_type : type, optional
            The type of value returned.
        target : str, optional
            If specified, search for a key for the given target.
            ex: class.html with be returned for the 'class' key and 'html'
            target, if available, otherwise, the entry for 'class' will be
            returned.
        default : object, optional
            If the key is not found, return this value instead.
        sep : str, optional
            The separator character (or string) to use to separate the key
            and target.
        raise_error : bool, optional
            If True and if the key is in this dict, but the type cannot be
            converted, raise and AttributeFormatError.

        Returns
        -------
        formatted_value
            The value in the specified value_type.
        """
        value = self.get(key=key, target=target, default=_MissingAttribute,
                         sep=sep)

        # Return the value directly if it matches the value_type
        if isinstance(value, value_type):
            return value

        # Otherwise it needs to be converted
        exception = None
        if value == _MissingAttribute:
            # The value was not found. Mark the exception as a KeyError,
            # in case 'raise_error' is True. The value returned will be the
            # default value
            exception = KeyError(key)

        elif value_type == bool:
            # Try converting boolean values. Strings are special, since they
            # can be 'true'  or 'false'
            if isinstance(value, str):
                return False if 'false' in value.lower().strip() else True
            else:
                try:
                    return bool(value)
                except ValueError as e:
                    exception = e

        elif value_type == tuple or value_type == list:
            # Try converting tuples and lists. Strings are special, since they
            # need to be parsed into values for the tuple or list.
            if isinstance(value, str):
                try:
                    return value_type(value.split())
                except ValueError as e:
                    exception = e
            else:
                try:
                    return value_type(value)
                except ValueError as e:
                    exception = e

        else:
            # Otherwise, just try converting the value to the desired
            # value_type
            try:
                return value_type(value)
            except ValueError as e:
                exception = e

        # The conversion was not successful. Either raise the captured
        # exception, if available, or return the default value.
        if exception is not None and raise_error:
            raise exception
        else:
            return default

    def append(self, key, value):
        """Set a value by appending to it, if it already exists, or creating
        it if it doesn't.

        Parameters
        ----------
        key : string
            The key for the entry to set or append.
        value : object
            The value to set or append.
        """
        if key not in self:
            # Simply set the value, if it doesn't exist
            self[key] = value
        else:
            current_value = self[key]
            # In this case, try to append it
            if isinstance(current_value, str):
                self[key] = ' '.join((current_value, str(value)))
            elif isinstance(current_value, list):
                current_value.append(value)
            else:
                # Append it as a string
                self[key] = ' '.join((str(current_value), str(value)))

    def filter(self, keys=None, target='', sep=attribute_target_sep):
        """Create an Attributes dict with target-specific entries.

        Parameters
        ----------
        keys : iterable of str or None
            Filter keys. If specified, only entries that match one of these
            keys will be returned.
        target : str or None, optional
            Filter targets. If specified, only entries general entries will
            be returned unless a target-specific entry is present, in which
            case it will be returned.
            For example, if entries for 'class' and 'class.tex' exist and
            target='tex', then the 'class.tex' entry will be returned as
            'class'. If target is None, then the 'class' entry will be returned.
        sep : str, optional
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        attributes : :obj:`disseminate.attributes.Attributes`
            A filtered attributes dict.

        Examples
        --------
        >>> attrs = Attributes('class=one tgt=default tgt.tex=tex')
        >>> attrs.filter()  # python >= 3.6 should have ordered entries
        Attributes{'class': 'one', 'tgt': 'default'}
        >>> attrs.filter(target='tex')
        Attributes{'class': 'one', 'tgt': 'tex'}
        >>> attrs.filter(keys='class')
        Attributes{'class': 'one'}
        >>> attrs.filter(keys='tgt')
        Attributes{'tgt': 'default'}
        """
        # strip leading periods in the target
        target = target[1:] if target.startswith('.') else target

        # Create a dict with keys and values, using target-specific entries
        # if available
        d = dict()

        # Convert the keys argument to a list of filtered_keys
        filtered_keys = (keys,) if isinstance(keys, str) else keys  # wrap strs

        for k in self.keys():
            # See if a target-specific key exists, or a general key
            # ex -- k='class' k_target='class.html'
            #    -- k='class.html' k_target='class.html.html'
            k_target = sep.join((k, target))

            pieces = k.split(sep)
            if len(pieces) > 1 and pieces[1] != target:
                # Skip targets that don't match the target
                continue
            else:
                k_general = pieces[0]

            if (k_target not in self and
               (filtered_keys is None or k_general in filtered_keys)):
                # Only add the entry if:
                #   1. the key is specific, or it's a general key without a
                #      specific target. Regardless, the 'd' dict's key
                #      should not have the target-specific part
                #   2. If filtered_keys is specified, make sure the general
                #      key is in the list of keys to include.
                d[k_general] = self[k]

        return Attributes(d)

    def exclude(self, keys, target='',  sep=attribute_target_sep):
        """Create an Attributes dict with the specified keys excluded.

        Parameters
        ----------
        keys : iterable of str or None
            Exclude keys. If specified, entries that match one of these
            keys will not be returned.
        target : str or None, optional
            If specified, general and specific entries will be excluded
            for the given target.
        sep : str, optional
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        attributes : :obj:`disseminate.attributes.Attributes`
            A filtered attributes dict.

        Examples
        --------
        >>> attrs = Attributes('class=one tgt=default tgt.tex=tex')
        >>> attrs.exclude('test')  # python >= 3.6 should have ordered entries
        Attributes{'class': 'one', 'tgt': 'default', 'tgt.tex': 'tex'}
        >>> attrs.exclude('class')
        Attributes{'tgt': 'default', 'tgt.tex': 'tex'}
        >>> attrs.exclude('tgt', target='tex')
        Attributes{'class': 'one'}
        >>> attrs.exclude('tgt')
        Attributes{'class': 'one'}
        """
        exclude_keys = (keys,) if isinstance(keys, str) else keys  # wrap strs
        exclude_keys = set(exclude_keys)

        # Get a set of all keys in this Attributes dict
        keys = self.keys()

        # Remove all exclude keys
        keys = [k for k in keys if k not in exclude_keys]

        if target:
            # Remove target-specific keys, if a target is specified
            exclude_keys = {sep.join((k, target)) for k in exclude_keys}
            keys = [k for k in keys if k not in exclude_keys]
        else:
            # Otherwise remove all targets
            keys = [k for k in keys
                    if not any(k.startswith(l) for l in exclude_keys)]

        return Attributes({k: self[k] for k in keys})

    @property
    def html(self):
        """Format the attributes for html."""
        d = self.filter(target='html')

        # Create an attribute string in html format
        entries = ["{}='{}'".format(k, v) if v != PositionalAttribute else
                   "{}".format(k)
                   for k, v in d.items()]
        return " ".join(entries)




    @property
    def tex(self):
        """Format the attributes for tex."""
        d = self.filter(target='tex')

        # Create an attribute string in html format
        entries = ["{}={}".format(k, v) if v != PositionalAttribute else
                   "{}".format(k)
                   for k, v in d.items()]
        return " ".join(entries) if entries else ""
