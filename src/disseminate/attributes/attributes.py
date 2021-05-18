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


def strip_attr(attr, sep=settings.attribute_target_sep):
    """Strip a target-specific terminator from the given attr.

    Parameters
    ----------
    attr : Union[str, :class:`PositionalValue <.PositionalValue>`]
            The key of the attribute to retrieve or the PositionalValue to
            retrieve.
    sep : Optional[str]
        The separator character (or string) to use to separate the key
        and target.

    Returns
    -------
    stripped_attr : str
        The attribute with the target-specific terminator stripped.

    Examples
    --------
    >>> strip_attr(3)
    3
    >>> strip_attr('143')
    '143'
    >>> strip_attr('width.tex')
    'width'
    >>> strip_attr('width')
    'width'
    >>> strip_attr('my_file.pdf#link-anchor')
    'my_file.pdf#link-anchor'
    >>> strip_attr('my_file.pdf#link-anchor.tex')
    'my_file.pdf#link-anchor'
    """
    if isinstance(attr, str):
        # If a target-specific terminator is not included, nothing needs to
        # be done
        if sep not in attr:
            return attr

        # Check all available targets
        targets = {target.strip('.')
                   for target in settings.tracked_deps.keys()}
        for target in targets:
            term = sep + target
            if attr.endswith(term):
                return attr[:-len(term)]

    return attr


def is_target_specific(attr, sep=settings.attribute_target_sep):
    """Tests whether the given attribute is a target-specific attribute.

    Parameters
    ----------
    attr : Union[str, :class:`PositionalValue <.PositionalValue>`]
            The key of the attribute to retrieve or the PositionalValue to
            retrieve.
    sep : Optional[str]
        The separator character (or string) to use to separate the key
        and target.

    Returns
    -------
    is_target_specific : bool
        True if the attr is a target-specific attribute

    Examples
    --------
    >>> is_target_specific(3)
    False
    >>> is_target_specific('pos')
    False
    >>> is_target_specific('pos.tex')
    True
    >>> is_target_specific('/usr/docs/text.tex')  # not quoted
    True
    >>> is_target_specific('"/usr/docs/text.tex"')  # quoted
    False
    """
    return attr != strip_attr(attr, sep=sep)


re_attrs = regex.compile(r'((?P<key>[\w\.]+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|[^\s\]]+))'
                         r'|(?P<position>"[^"]*"'
                         r'|\'[^\']*\''
                         r'|[^\s,\[\]]+|))')


class Attributes(dict):
    """The attributes class is an ordered dict to manage and validate attribute
    entries.

    .. note:: Attributes can either be key/value (ex: 'class=media') or
              positional (ex: 'red'). For positional arguments, the values
              are :class:`PositionalValue <.utils.types.PositionalValue>` class
              objects.
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

    def copy(self):
        return Attributes(**self)

    def totuple(self):
        """Return a tuple for an attributes dict

        Examples
        --------
        >>> attrs = Attributes("key1=val1 val2")
        >>> attrs.totuple()
        (('key1', 'val1'), 'val2')
        """
        return tuple(k if ispositional(v) else (k, v)
                     for k, v in self.items())

    def load(self, s, sep=settings.attribute_target_sep):
        """Parses an attribute string into key/values for the Attributes dict.

        Parameters
        ----------
        s: str
            Input string of attributes. Attributes come in two forms:
            positional attributes and keyword attributes (kwargs), and
            attributes strings have the following form:
            "key1=value1 key2=value2 value3"
        sep : Optional[str]
            The separator character (or string) to use to separate the key
            and target.

        Examples
        --------
        >>> attrs = Attributes()
        >>> attrs.load("key1=val1 val2")
        >>> attrs
        Attributes{'key1': 'val1', 'val2': <class '...StringPositionalValue'>}
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
                gen_value = strip_attr(value, sep=sep)

                # Add the positional attribute to the dict by putting the
                # positional value as a key and the PostionalValue class or
                # subclass as the value
                attrs.append((value, positionalvalue_type(gen_value)))

        self.update(tuple(attrs))

    def find_item(self, attr, target=None, default=None,
                  sep=settings.attribute_target_sep):
        """Find the key in the attributes dict with or without the target
        specified.

        This function will not modify the keys/values in this attributes dict.

        Parameters
        ----------
        attr : Union[str, :class:`PositionalValue <.PositionalValue>`]
            The key of the attribute to retrieve or the PositionalValue to
            retrieve.
        target : Optional[str]
            If specified, search for a key for the given target.
            ex: class.html with be returned for the 'class' key and 'html'
            target, if available, otherwise, the entry for 'class' will be
            returned.
        default : Optional[Any]
            If the key is not found, return this value instead.
        sep : Optional[str]
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        key, value : Any
            The retrieved item.

        Examples
        --------
        >>> attrs = Attributes('class="general" class.html="specific" pos')
        >>> attrs.find_item('class')
        ('class', 'general')
        >>> attrs.find_item('class.html')
        ('class.html', 'specific')
        >>> attrs.find_item('class', target='html')
        ('class.html', 'specific')
        >>> attrs.find_item('class', target='tex')
        ('class', 'general')
        >>> attrs.find_item('pos')
        ('pos', <class ...StringPositionalValue'>)
        >>> attrs.find_item('missing')
        """
        target = target.strip('.') if isinstance(target, str) else target

        # See if the target specific key is in the attributes
        # ex: 'class.html' for target='.html' or 'file.txt.tex'
        target_key = (sep.join((str(attr), target)) if target is not None
                      else None)
        if target_key and target_key in self:
            return target_key, self[target_key]

        # See if the attr is a key in the dict itself. ex: 'class'
        if attr in self:
            return attr, self[attr]

        # See if it's a positional value
        if ispositional(attr):
            # Find all matching positional values
            # ex: StringPositionalValue
            items = [(k, v) for k, v in self.items() if ispositional(v, attr)]

            if target:
                # Filter by target, if specific
                target_items = [(k, v) for k, v in items if k.endswith(target)]
            else:
                # Otherwise remove entries that have target-specific
                target_items = [(k, v) for k, v in items
                                if not is_target_specific(k, sep=sep)]

            # Return the first item found
            if target_items:
                return target_items[0]
            elif items:
                return items[0]

        # Give up
        return default

    def get(self, attr, target=None, default=None,
            sep=settings.attribute_target_sep):
        """Retrieve an entry by target-specific key, if available and
        specified, or by key.

        As opposed to the find_item method, this function will strip the
        target-specific terminators of returned values

        Parameters
        ----------
        attr : Union[str, :class:`PositionalValue <.PositionalValue>`]
            The key of the attribute to retrieve or the PositionalValue to
            retrieve.
        target : Optional[str]
            If specified, search for a key for the given target.
            ex: class.html with be returned for the 'class' key and 'html'
            target, if available, otherwise, the entry for 'class' will be
            returned.
        default : Optional[Any]
            If the key is not found, return this value instead.
        sep : Optional[str]
            The separator character (or string) to use to separate the key
            and target.

        Returns
        -------
        value : Any
            The retrieved value.
            If the entry is a positional attribute, PositionalValue will be
            returned.

        Examples
        --------
        >>> attrs = Attributes('class="general" class.html="specific" pos')
        >>> attrs.get('class')
        'general'
        >>> attrs.get('class.html')
        'specific'
        >>> attrs.get('class', target='html')
        'specific'
        >>> attrs.get('class', target='tex')
        'general'
        >>> attrs.get('pos')
        <class ...StringPositionalValue'>
        >>> attrs.get('missing')
        """
        rv = self.find_item(attr=attr, target=target, default=default,
                            sep=sep)
        if isinstance(rv, tuple) and len(rv) == 2:
            key, value = rv
            rv = key if ispositional(attr) else value

            return strip_attr(rv, sep=sep) if isinstance(rv, str) else rv
        else:
            return rv

    def append(self, attr, value=_MissingAttribute):
        """Set a value by appending to it, if it already exists, or creating
        it if it doesn't.

        Parameters
        ----------
        attr : str
            The attr (key) for the entry to set or append.
        value : Optional[Any]
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

    def strip(self, sep=settings.attribute_target_sep):
        """Replace the entries in this attributes dict without the
        target-specific terminators."""
        # Make a copy and reset this dict
        cp = self.copy()
        self.clear()

        # Get all the keys to copy over
        keys = list(cp.keys())

        # Find target-specific terminators from keys.
        stripped_keys = set()
        for key in keys:
            stripped_key = strip_attr(key, sep=sep)
            if stripped_key != key:
                stripped_keys.add(stripped_key)

        # Remove keys that have target-specific entries
        keys = [k for k in keys if k not in stripped_keys]

        for key in keys:
            stripped_key = strip_attr(key, sep=sep)

            if key == stripped_key:
                # use the key, if it hasn't been changed
                self[key] = cp[key]
            else:
                self[stripped_key] = cp[key]

    def filter(self, attrs=None, target=None,
               sep=settings.attribute_target_sep, sort_by_attrs=False,
               strip=True):
        """Create an Attributes dict with target-specific entries.

        Parameters
        ----------
        attrs : Optional[Union[str, List[Union[str, :class:`PositionalValue \
            <.PositionalValue>`]]]]
            Filter keys. If specified, only entries that match one of these
            keys will be returned.
        target : Optional[str]
            Filter targets. If specified, only entries general entries will
            be returned unless a target-specific entry is present, in which
            case it will be returned.
            For example, if entries for 'class' and 'class.tex' exist and
            target='tex', then the 'class.tex' entry will be returned as
            'class'. If target is None, then the 'class' entry will be
            returned.
        sep : Optional[str]
            The separator character (or string) to use to separate the key
            and target.
        sort_by_attrs : Optional[bool]
            If True, the returned attributes dict will have keys sorted in the
            same order as the attrs passed. Otherwise, the returned attributes
            dict will be sorted with keys in the same order as this attributes
            dict (default).
        strip : Optional[bool]
            If True, strip all target-specific terminators from the returned
            attris dict.

        Returns
        -------
        attributes : :obj:`Attributes <.attributes.Attributes>`
            A filtered attributes dict.

        Examples
        --------
        >>> attrs = Attributes('class=one tgt=default tgt.tex=tex')
        >>> attrs.filter()  # python >= 3.6 should have ordered entries
        Attributes{'class': 'one', 'tgt': 'default'}
        >>> attrs.filter(target='tex', strip=False)
        Attributes{'class': 'one', 'tgt.tex': 'tex'}
        >>> attrs.filter(target='tex', strip=True)
        Attributes{'class': 'one', 'tgt': 'tex'}
        >>> attrs.filter(attrs='class')
        Attributes{'class': 'one'}
        >>> attrs.filter(attrs='tgt')
        Attributes{'tgt': 'default'}
        """
        target = target.strip('.') if isinstance(target, str) else target

        # Setup the returned attributes dict
        d = Attributes()

        # Setup the attrs without target-specific values
        attrs = ([attrs] if isinstance(attrs, str) or
                 isinstance(attrs, PositionalValue)
                 else attrs)  # wrap strings
        attrs = (list(self.keys())
                 if attrs is None else attrs)  # populate empty attrs
        attrs = uniq(attrs)  # general attrs

        if not sort_by_attrs:
            # Sort the attrs so that they follow the same order as keys in
            # this dict. This ensures the results of filter are deterministic
            # and not random, if the attrs are an unordered iterable, like a
            # set
            order = {k: num for num, k in enumerate(self.keys())}
            attrs = sorted(attrs, key=lambda x: order.get(x, len(order)))

        # Find keys to remove
        if target is not None:
            # Find target-specific terminators from keys.
            remove_attrs = set()
            for attr in attrs:
                stripped_attr = strip_attr(attr, sep=sep)

                if attr == stripped_attr:
                    # If the attr does not have a target-specific terminator,
                    # do not remove it.
                    continue
                # The following are entries when attr != stripped_attr, i.e.
                # key had a target-specific terminator
                if attr.endswith(sep + target):
                    # The attr is a target-specific attr that matches the
                    # target. Remove the non-target-specific general entry
                    remove_attrs.add(stripped_attr)
                else:
                    # The attr is a target-specific attr, but it matches a
                    # different target. Remove that.
                    remove_attrs.add(attr)
        else:
            # Remove target-specific keys
            remove_attrs = {attr for attr in attrs
                            if is_target_specific(attr, sep=sep)}

        # Remove those entries
        attrs = [attr for attr in attrs if attr not in remove_attrs]

        for attr in attrs:
            rv = self.find_item(attr=attr, target=target, sep=sep)
            if rv is not None:
                k, v = rv
                d[k] = v

        # Strip target-specific terminators, if strip is enabled
        if strip:
            d.strip()
        return d

    @property
    def html(self):
        """Format the attributes for html.

        Notes
        -----
        - This function won't strip target tags ('.html'), and a filter
          for the '.html' target should be applied before using this property

        """
        # Disable filtering here because the command that uses this property
        # already filters the attributes dict
        # d = self.filter(target='html')  # previously
        d = self

        # Create an attribute string in html format
        entries = ["{}='{}'".format(k, v) if not ispositional(v) else
                   "{}".format(k)
                   for k, v in d.items()]
        return " ".join(entries)

    @property
    def tex_arguments(self):
        """Format arguments for tex.

        Notes
        -----
        - This function won't strip target tags ('.tex'), and a filter
          for the '.tex' target should be applied before using this property

        Examples
        --------
        >>> Attributes('width=302 3').tex_arguments
        '{302}{3}'
        """
        # Disable filtering here because the format command that uses this
        # property already filters the attributes dict
        # d = self.filter(target='tex')  # previously
        d = self

        # Create an attribute in tex format
        entries = ["{{{}}}".format(v)
                   if not ispositional(v) else
                   "{{{}}}".format(k)
                   for k, v in d.items()]
        return "".join(entries) if entries else ""

    @property
    def tex_optionals(self):
        """Format optional arguments for tex.

        Notes
        -----
        - This function won't strip target tags ('.tex'), and a filter
          for the '.tex' target should be applied before using this property

        Examples
        --------
        >>> Attributes('width=302 3').tex_optionals
        '[width=302, 3]'
        """
        # Disable filtering here because the command that uses this property
        # already filters the attributes dict
        # d = self.filter(target='tex')  # previously
        d = self

        # Create an attribute in tex format
        entries = ["{}={}".format(k, v)
                   if not ispositional(v) else
                   "{}".format(k)
                   for k, v in d.items()]

        # Format the optional arguments. Treat '*' outside of parentheses
        return "[" + ", ".join(entries) + "]" if entries else ""
