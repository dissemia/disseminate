"""
Utilities for dealing with Python classes.
"""
import weakref
from itertools import chain as i_chain


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
    [<class 'disseminate.utils.classes.B'>, \
<class 'disseminate.utils.classes.C'>]
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
    [<class 'disseminate.utils.classes.B'>, \
<class 'disseminate.utils.classes.A'>]
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
