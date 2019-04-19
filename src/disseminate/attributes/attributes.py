"""
Classes and methods to manage tag attributes
"""
import regex

from .. import settings
from ..utils.list import uniq
from ..utils.types import PositionalValue, positionalvalue_type, ispositional


class AttributeFormatError(Exception):
    """An error was encountered in the format of attributes"""
    pass


class _MissingAttribute(object):
    """An internal object used when a key is missing"""
    pass


def gen_attr(attr, sep=settings.attribute_target_sep):
    """The general attribute for the given attribute, whether it's a general
    attribute or a target-specific attribute.

    Examples
    --------
    >>> gen_attr(3)
    3
    >>> gen_attr('143')
    '143'
    >>> gen_attr('3.1416')
    '3.1416'
    >>> gen_attr('2.718.tex')
    '2.718'
    >>> gen_attr('width.tex')
    'width'
    >>> gen_attr('width')
    'width'
    """
    if not isinstance(attr, str):
        return attr
    split = attr.split(sep)

    if len(split) == 1:
        # It already a general attr, return it
        # ex:
        #     attr: '3', return '3'
        return split[0]
    elif len(split) > 2:
        # Only the last piece is a target. Just strip it.
        # ex:
        #     '3.1416.tex', return '3.1416'
        return sep.join(split[0:-1])
    else:
        # See if the last piece matches a target.
        # ex:
        #     '3.1416', return '3.1416'
        return (sep.join(split) if split[-1].isdigit() else
                sep.join(split[0:-1]))


re_attrs = regex.compile(r'((?P<key>[\w\.]+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|[^\s\]]+))'
                         r'|(?P<position>[\w\.\(\)]+))')


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
            A tuple of attributes comprising either 2-ple strings
            (key, value) or strings (positional arguments)
        """
        attrs = []

        for m in re_attrs.finditer(s):
            d = m.groupdict()
            if d.get('key', None) and d.get('value', None):
                # Put the key-value pair in the attributes dict
                attrs.append((d['key'], d['value'].strip('"').strip("'")))

            elif d.get('position', None):
                value = d['position'].strip("'").strip('"')

                # Strip target-specific suffixes to get the accurate
                # PostionalValue subclass. (ex: '3.1416.tex' turns into
                # '3.1416' to create a FloatPositionalValue instead of just a
                # PositionalValue)
                gen_value = gen_attr(value, settings.attribute_target_sep)

                # Add the positional attribute to the dict by putting the
                # positional value as a key and the PostionalValue class or
                # subclass as the value
                attrs.append((value, positionalvalue_type(gen_value)))

        self.update(tuple(attrs))

    def get_positional(self, attr, target=None, default=None,
                       sep=settings.attribute_target_sep):
        """Retrieve an positional argument/value.

        Parameters
        ----------
        attr : PositionalValue (type)
            The PositionalValue of the attribute to retrieve.
        target : str, optional
            If specified, search for a positional argument for the given target.
            ex: '1' will be returned for the '1.tex' positional argument and
            'tex' target, if available. Otherwise, a general positional argument
            is returned
        default : object, optional
            If the positional argument is not found, return this value instead.
        sep : str, optional
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        value
            The retrieved positional argument.

        Examples
        --------
        >>> attrs = Attributes('class="general" class.html="specific" 1 2.tex')
        >>> attrs.get_positional('class')
        >>> attrs.get_positional(PositionalValue)
        '1'
        >>> attrs.get_positional(PositionalValue, target='tex')
        '2'
        """
        # Remove the trailing period for the target, if it's present
        target = target.strip('.') if isinstance(target, str) else target

        # For see if it's an attribute for a positional argument
        if ispositional(attr):
            # Find all positional values that are of the same type as attr
            positional_keys = [k for k, v in self.items()
                               if ispositional(v, attr)]

            # Return a target-specific positional argument, if requested and
            # available.
            target_positional_keys = ([k for k in positional_keys
                                       if k.endswith(sep + target)]
                                      if target is not None else [])

            if target_positional_keys:
                # A target positional key was found. Return the first one.
                return target_positional_keys[0].split(sep + target)[0]
            elif len(positional_keys) == 1:
                # A target positional key was not sought or found. Return the
                # only positional key, if only one was found.
                return positional_keys[0]
            elif len(positional_keys) > 1:
                # More than 1 positional key was found. Return the generic one,
                # if available. This is a bit tricky since the key might contain
                # a separator ('.'). In this case, return the key with the
                # fewest number of seperators. ex: '3.1416' before '2.718.tex'

                sorted_keys = sorted([k for k in positional_keys
                                      if isinstance(k, str)],
                                     key=lambda x: x.count(sep))

                if len(sorted_keys) > 1:
                    return sorted_keys[0]

        # Attribute/key not found
        return default

    def get_value(self, attr, target=None, default=None,
                  sep=settings.attribute_target_sep):
        """Retrieve an attribute entry.

        Parameters
        ----------
        attr : str
            The key of the attribute to retrieve.
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
            If the entry is a positional attribute, PositionalValue will be
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
        # Remove the trailing period for the target, if it's present
        target = target.strip('.') if isinstance(target, str) else target

        if target is not None and sep.join((attr, target)) in self:
            # See if a target-specific key is availble
            return self[sep.join((attr, target))]
        elif attr in self:
            # Otherwise, see if the key itself is available
            return self[attr]
        else:
            # When the key is not available, return the default
            return default

    def get(self, attr, target=None, default=None,
            sep=settings.attribute_target_sep):
        """Retrieve an entry by target-specific key, if available and
        specified, or by key.

        Parameters
        ----------
        attr : str or PositionalValue (type)
            The key of the attribute to retrieve or the PositionalValue to
            retrieve.
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
            If the entry is a positional attribute, PositionalValue will be
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
        # Remove the trailing period for the target, if it's present
        target = target.strip('.') if isinstance(target, str) else target

        # Try retrieving a positional attribute
        value = self.get_positional(attr=attr, target=target,
                                    default=_MissingAttribute, sep=sep)
        if value != _MissingAttribute:
            #  A positional value was found, return it.
            return value

        # A positional argument was not found. Now try to access the key/value
        # pair
        value = self.get_value(attr=attr, target=target,
                               default=_MissingAttribute, sep=sep)
        if value != _MissingAttribute:
            #  A positional value was found, return it.
            return value

        return default

    def get_by_type(self, attr, value_type=str, target=None, default=None,
                    sep=settings.attribute_target_sep, raise_error=False):
        """Retrieve an entry by key and return for the given entry_type, if
        it can be converted.

        Parameters
        ----------
        attr : str or PositionalValue
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
        value = self.get(attr=attr, target=target, default=_MissingAttribute,
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
            exception = KeyError(attr)

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

    def append(self, attr, value=_MissingAttribute):
        """Set a value by appending to it, if it already exists, or creating
        it if it doesn't.

        Parameters
        ----------
        attr : string
            The attr (key) for the entry to set or append.
        value : object, optional
            The value to set or append. If not specified, the attribute will
            be added as a positional argument
        """
        if value == _MissingAttribute:
            # Simply add positional attributes
            self[attr] = PositionalValue
        elif attr not in self:
            # Simply set the value, if it doesn't exist
            self[attr] = value
        else:
            current_value = self[attr]
            # In this case, try to append it
            if isinstance(current_value, str):
                self[attr] = ' '.join((current_value, str(value)))
            elif isinstance(current_value, list):
                current_value.append(value)
            else:
                # Append it as a string
                self[attr] = ' '.join((str(current_value), str(value)))

    def filter(self, attrs=None, target='', sep=settings.attribute_target_sep,
               sort_by_attrs=False):
        """Create an Attributes dict with target-specific entries.

        Parameters
        ----------
        attrs : None, or iterable of str and PositionalValues
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
        sort_by_attrs: bool, optional
            If True, the returned attributes dict will have keys sorted in the
            same order as the attrs passed. Otherwise, the returned attributes
            dict will be sorted with keys in the same order as this attributes
            dict (default).

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
        >>> attrs.filter(attrs='class')
        Attributes{'class': 'one'}
        >>> attrs.filter(attrs='tgt')
        Attributes{'tgt': 'default'}
        """
        # Strip the leading period from the target, if present
        target = target[1:] if target.startswith('.') else target

        # Setup the returned attributes dict
        d = Attributes()

        # Setup the attrs without target-specific values
        attrs = ([attrs] if isinstance(attrs, str) or
                 isinstance(attrs, PositionalValue)
                 else attrs)  # wrap strings
        attrs = (list(self.keys())
                 if attrs is None else attrs)  # populate empty attrs
        attrs = uniq([gen_attr(k, sep) for k in attrs])  # general attrs

        if not sort_by_attrs:
            # Sort the attrs so that they follow the same order as keys in
            # this dict. This ensures the results of filter are deterministic
            # and not random, if the attrs are an unordered iterable, like a set
            order = {k: num for num, k in enumerate(self.keys())}
            attrs = sorted(attrs, key=lambda x: order.get(x, len(order)))

        for attr in attrs:
            # Try the positional value
            if ispositional(attr):
                value = self.get_positional(attr=attr, target=target,
                                            default=_MissingAttribute, sep=sep)
            else:
                value = _MissingAttribute

            if value != _MissingAttribute:
                # value is the key. ex: '3', attr is the PostionalValue class
                # or subclass. ex: 'IntPositionalValue'
                d[value] = attr
                continue

            # Try a key/value entry
            if not ispositional(attr):
                value = self.get_value(attr=attr, target=target,
                                       default=_MissingAttribute, sep=sep)
            else:
                value = _MissingAttribute

            if value == _MissingAttribute:
                # A value couldn't be found
                continue
            elif ispositional(value):
                # A positional attribute was accessed by key-value because the
                # value is the PositionalValue class (or a subclass)
                # Since the attr may have the target trimmed (ex: '3.1416.tex'
                # to '3.1416'), we may need to convert the PositionalValue
                # type.
                # ex: convert PositionalValue to FloatPositionalValue
                d[attr] = positionalvalue_type(attr)
            else:
                # value was found, copy it over
                d[attr] = value

        return d

    def exclude(self, attrs=None, target=None,
                sep=settings.attribute_target_sep):
        """Create an Attributes dict with the specified attrs excluded.

        Parameters
        ----------
        attrs : iterable of str or None
            Exclude attrs. If specified, entries that match one of these
            attrs will not be returned.
        target : str or None, optional
            If specified, target-specific entries will be excluded for the
            given target.
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
        >>> attrs.exclude(target='tex')
        Attributes{'class': 'one', 'tgt': 'default'}
        >>> attrs.exclude('tgt')
        Attributes{'class': 'one'}
        """
        d = Attributes()

        exclude_keys = () if attrs is None else attrs
        exclude_keys = ((exclude_keys,)
                        if isinstance(exclude_keys, str) else
                        exclude_keys)  # wrap strs
        exclude_keys = set(exclude_keys)

        for k, v in self.items():
            # See if it's a positional value
            if ispositional(v) and v in exclude_keys:
                continue

            # See if it's a key-value
            elif target and isinstance(k, str) and k.endswith(sep + target):
                # If a target to exclude is specified and the key ends with
                # the target, skip it. ex: width.tex
                continue

            elif target is None and gen_attr(k, sep) in exclude_keys:
                # If the target is not specified, remove the target-specific
                # attribute if the general attribute should be exclude
                continue

            elif k in exclude_keys:
                # If the key matches a key listed in the exclude_keys, skip it.
                continue

            # Not excluded, copy it over
            d[k] = v

        return d

    @property
    def html(self):
        """Format the attributes for html."""
        d = self.filter(target='html')

        # Create an attribute string in html format
        entries = ["{}='{}'".format(k, v) if not ispositional(v) else
                   "{}".format(k)
                   for k, v in d.items()]
        return " ".join(entries)

    @property
    def tex_arguments(self):
        """Format arguments for tex.

        Examples
        --------
        >>> Attributes('width=302 3').tex_arguments
        '{302}{3}'
        """
        d = self.filter(target='tex')

        # Create an attribute in tex format
        entries = ["{{{}}}".format(v)
                   if not ispositional(v) else
                   "{{{}}}".format(k)
                   for k, v in d.items()]
        return "".join(entries) if entries else ""

    @property
    def tex_optionals(self):
        """Format optional arguments for tex.

        Examples
        --------
        >>> Attributes('width=302 3').tex_optionals
        '[width=302, 3]'
        """
        d = self.filter(target='tex')

        # Create an attribute in tex format
        entries = ["{}={}".format(k, v)
                   if not ispositional(v) else
                   "{}".format(k)
                   for k, v in d.items()]

        # Format the optional arguments. Treat '*' outside of parentheses
        return "[" + ", ".join(entries) + "]" if entries else ""
