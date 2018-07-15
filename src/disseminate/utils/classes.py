"""
Utilities for dealing with Python classes.
"""


def all_subclasses(cls):
    """Retrieve all subclasses, sub-subclasses and so on for a class

    Parameters
    ----------
    cls : class object
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
    cls : class object
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


def all_parent_attributes(cls, attribute):
    """Retrieve a list of a class attribute for all parent classes of a given
    class.

    Parameters
    ----------
    cls : class object
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
    >>> class C(B):
    ...     value = 'c'
    >>> all_parent_attributes(C, 'value')
    ['b', 'a']
    """
    bases = all_parent_classes(cls)
    return [getattr(b, attribute) for b in bases if hasattr(b, attribute)]
