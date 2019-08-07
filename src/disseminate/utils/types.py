"""
Generic types.
"""


class PositionalValue(object):
    """A placeholder for a positional value in a dict."""
    pass


class IntPositionalValue(PositionalValue):
    """A placeholder for a positional *integer* value in a dict."""
    pass


class FloatPositionalValue(PositionalValue):
    """A placeholder for a positional *float* value in a dict."""
    pass


class StringPositionalValue(PositionalValue):
    """A placeholder for a positional *string* value in a dict."""
    pass


def ispositional(p, positionalvalue_type=PositionalValue):
    """True, if the given parameter is a PositionalValue class or subclass.

    Parameters
    ----------
    p : object
        The parameter to test.
    positionalvalue_type : :class:`PositionalValue <.types.PositionalValue>`
        The PositionalValue class to test whether parameter is a subclass of
        this type.

    Returns
    -------
    bool
        True if parameter 'p' is the class or a subclass of PositonalValue
        (positionalvalue_type).

    Examples
    --------
    >>> ispositional('test')
    False
    >>> ispositional(IntPositionalValue)
    True
    >>> ispositional(PositionalValue)
    True
    """
    return isinstance(p, type) and issubclass(p, positionalvalue_type)


def positionalvalue_type(p):
    """Find the PostionalValue type for the given parameter.

    Parameters
    ----------
    p : object
        The parameter for which the PositionalValue class or subclass will be
        evaluated and returned.

    Returns
    -------
    positionalvalue_type : :class:`PositionalValue <.types.PositionalValue>`
        The PositionalValue class or subclass that matches the given parameter.

    Examples
    --------
    >>> positionalvalue_type(3)
    <class 'disseminate.utils.types.IntPositionalValue'>
    >>> positionalvalue_type('test')
    <class 'disseminate.utils.types.StringPositionalValue'>
    >>> positionalvalue_type('23')
    <class 'disseminate.utils.types.IntPositionalValue'>
    >>> positionalvalue_type('3.23')
    <class 'disseminate.utils.types.FloatPositionalValue'>
    >>> positionalvalue_type('src/media/image.png')
    <class 'disseminate.utils.types.StringPositionalValue'>
    """
    mappings = ((int, IntPositionalValue),
                (float, FloatPositionalValue),
                (str, StringPositionalValue),
                )

    for t, v in mappings:
        try:
            t(p)
            return v
        except ValueError:
            pass

    return PositionalValue
