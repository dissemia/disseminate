"""
Utilities for dealing with Python classes.
"""
import weakref
from itertools import chain as i_chain
import time


def all_subclasses(cls):
    """Retrieve all subclasses, sub-subclasses and so on for a class

    Parameters
    ----------
    cls : Type
        The class object to inspect for subclasses.

    Returns
    -------
    subclasses : list
        The list of all subclasses.

    Examples
    --------
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(B): pass
    >>> all_subclasses(A)
    [<class 'disseminate.utils.classes.B'>, <class 'disseminate.utils.classes.C'>]
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


def all_parent_classes(cls):
    """Retrieve a list of all of parent classes for a given class.

    Parameters
    ----------
    cls : Type
        The class object to inspect for parent classes.

    Returns
    -------
    parent_classes : list
        The list of all parent classes (not including the object class).

    Examples
    --------
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(B): pass
    >>> all_parent_classes(C)
    [<class 'disseminate.utils.classes.B'>, <class 'disseminate.utils.classes.A'>]
    """
    return list(cls.__bases__) + [g for s in list(cls.__bases__)
                                  for g in all_parent_classes(s)
                                  if g != object]


def all_attributes_values(cls, attribute):
    """Retrieve a list of all values for a given class's attribute
    for the given class and all its parent classes.

    Parameters
    ----------
    cls : Type
        The class object to inspect for parent classes.
    attribute : str
        The attribute whose value should be retrieved from each class.

    Returns
    -------
    parent_attributes : list
        The list of all parent classe attributes.

    Examples
    --------
    >>> class A(object):
    ...     value = 'a'
    >>> class B(A):
    ...     value = 'b'
    ...     value2 = (1, 2)
    >>> class C(B):
    ...     value = 'c'
    ...     value2 = (2, 3)
    >>> sorted(all_attributes_values(C, 'value'))
    ['a', 'b', 'c']
    >>> sorted(all_attributes_values(C, 'value2'))
    [1, 2, 3]
    """
    bases = [cls] + all_parent_classes(cls)
    return set(i_chain(*[getattr(b, attribute) for b in bases
                         if hasattr(b, attribute)]))


def all_dicts(cls):
    """Produce a dict with entries from a given class's __dict__ and the
    __dict__ of all its parent classes.

    Precedence is given to the subclasses over parent classes if the attributes
    were overwritten by subclasses.

    Examples
    --------
    >>> class A(object):
    ...     a1 = 1
    ...     a2 = 2
    >>> class B(A):
    ...     a2 = 3
    ...     b1 = 4
    >>> d = all_dicts(B)
    >>> d['a1']
    1
    >>> d['a2']
    3
    >>> d['b1']
    4
    """
    bases = all_parent_classes(cls)[::-1] + [cls]
    d = dict()
    for base in bases:
        if hasattr(base, '__dict__'):
            d.update(base.__dict__)
    return d


class weakattr(object):
    """A descriptor to store a weakref to an object attribute"""

    def __get__(self, obj, objtype=None):
        weakref_dict = obj.__dict__.setdefault('__weakrefattrs__', dict())
        attrname = self.attrname(obj)
        value = weakref_dict.get(attrname, None)
        return value() if callable(value) else None

    def __set__(self, obj, value):
        if value is None:  # do nothing is a value of None is assigned
            return
        weakref_dict = obj.__dict__.setdefault('__weakrefattrs__', dict())
        attrname = self.attrname(obj)
        weakref_dict[attrname] = weakref.ref(value)

    def __delete__(self, obj):
        weakref_dict = obj.__dict__.setdefault('__weakrefattrs__', dict())
        attrname = self.attrname(obj)
        del weakref_dict[attrname]

    def attrname(self, obj):
        if not hasattr(self, '_attrname'):
            cls = obj.__class__
            for name, value in all_dicts(cls).items():
                if value == self:
                    self._attrname = name
        if hasattr(self, '_attrname'):
            return self._attrname
        else:
            raise AttributeError("weakrefattr could not be found in "
                                 "object '{}'".format(obj))


def trackmtimes(includeattrs=None, excludeattrs=None):
    """A class wrapper to save the modification times (mtimes) for changes
    of specific attributes.

    Parameters
    ----------
    includeattrs : Optional[Tuple[str]]
        If specified, only attributes listed in the includeattrs tuple will
        update the mtime attribute for the class when their values are changed.
    excludeeattrs : Optional[Tuple[str]]
        If specified, attributes listed in the excludeattrs tuple will _not_
        update the mtime attribute for the class when their values are changed.

    Examples
    --------
    >>> @trackmtimes(includeattrs=('a'))
    ... class Test(object):
    ...     pass
    >>> test = Test()
    >>> test.a = 1  # Initially setting the attribute doesn't set mtime
    >>> hasattr(test, 'mtime')
    False
    >>> test.a = 2
    >>> hasattr(test, 'mtime') and isinstance(test.mtime, float)
    True
    """
    def wrapper(cls):
        assert includeattrs is not None or excludeattrs is not None, (
            "trackmtimes: either includeattrs or excludeattrs should be "
            "specified.")

        # See if this class has already been wrapped by this wrapper
        already_wrapped = (hasattr(cls, '_trackmtimes_includes_') or
                           hasattr(cls, '_trackmtimes_excludes_'))

        # Create sets for the tracked attributes in the class, if needed.
        # If _trackmtimes_includes_/_trackmtimes_excludes_ exists from a
        # parent class, create copies so that the parent class's set isn't
        # changed
        cls._trackmtimes_includes_ = (set() if not
                                      hasattr(cls, '_trackmtimes_includes_')
                                      else cls._trackmtimes_includes_.copy())
        cls._trackmtimes_excludes_ = (set() if not
                                      hasattr(cls, '_trackmtimes_excludes_')
                                      else cls._trackmtimes_excludes_.copy())

        # Add the includeattrs and excludeattrs to these sets
        if includeattrs is not None:
            cls._trackmtimes_includes_ |= set(includeattrs)
        if excludeattrs is not None:
            cls._trackmtimes_excludes_ |= set(excludeattrs)

        # If the function is already wrapped, it doesn't need to be wrapped
        # again
        if already_wrapped:
            return cls

        # In this case, the class hasn't been wrapped. Wrap its __setattr__
        # method.

        # Keep the current __setattr__
        current_setattr = cls.__setattr__

        def __setattr__(self, name, value):
            """A set attribute function to update the label's mtime for the
            modification of some fields."""

            if value is None:
                return

            # Get the current value to see if it's changed
            current_value = getattr(self, name, None)

            # Set the new value
            current_setattr(self, name, value)

            # Determine if the attribute should be an attribute with a tracked
            # mtime
            if name == 'mtime':
                # The mtime attribute is special, and it should not be tracked
                # (i.e. updated when it's updated)
                trackedattr = False
            elif (self._trackmtimes_excludes_ and
                  name not in self._trackmtimes_excludes_):
                # In this case, at least one exclude was specified, so the
                # wrapper is in exclusion mode. If the attribute's name is
                # not in the excludes set, then it should be tracked.
                trackedattr = True
            elif name in self._trackmtimes_includes_:
                # In this case, we're in the inclusion mode. Only track the
                # dependency if the attribute's name is in the includes set.
                trackedattr = True
            else:
                # Otherwise, it's not a tracked attribute.
                trackedattr = False

            # Set the mtime if the value is changed or it has already been set
            if (trackedattr and current_value != value and
               current_value is not None):
                current_setattr(self, 'mtime', time.time())

        cls.__setattr__ = __setattr__

        return cls

    return wrapper
