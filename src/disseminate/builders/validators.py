"""
Functions to validate arguments
"""


def _raise_error(msg, exception, raise_error=True):
    """When an argument is not valid, raise a ValidationError with the
    given message when the raise_error argument is True. Otherwise return
    False.
    """
    if raise_error:
        raise exception(msg)

    return False


def validate_tuple(arg, length=None, type=None, raise_error=True):
    """Validate or try to convert an arg (argument) into a tuple.

    Parameters
    ----------
    arg : Iterable
        The tuple (or other iterable) to validate.
    length : Optional[Int]
        If specified, the tuple is only valid if it has this length.
    type : Optional[Type]
        If specified, this function will try to convert the items to this type,
        and the tuple will only be valid if its items are of this type.
    raise_error : Optional[Bool]
        If True (default), a ValidationError will be raised if arg doesn't
        validate.

    Returns
    -------
    arg : Union[arg, False]
        Returns the validated tuple.
        If the tuple could not be validated, returns False

    Examples
    --------
    >>> validate_tuple('test')
    Traceback (most recent call last):
        ...
    TypeError: The argument 'test' must not be a string
    >>> validate_tuple(1)
    Traceback (most recent call last):
        ...
    TypeError: The argument '1' must be a tuple
    >>> validate_tuple([1, 2, 3], length=4)
    Traceback (most recent call last):
        ...
    ValueError: The argument tuple '(1, 2, 3)' must be of length '4'
    >>> validate_tuple([1, 2, 3], length=3)
    (1, 2, 3)
    >>> validate_tuple([1.0, 2.0, 3.0], length=3, type=int)
    (1, 2, 3)
    >>> validate_tuple([1.0, 'a', 3.0], length=3, type=int)
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 10: 'a'
    """
    if isinstance(arg, str):
        return _raise_error("The argument '{}' must not be a "
                            "string".format(arg),
                            TypeError, raise_error=raise_error)
    if not hasattr(arg, '__iter__'):
        return _raise_error("The argument '{}' must be a tuple".format(arg),
                            TypeError, raise_error=raise_error)
    try:
        arg = tuple(arg)
    except TypeError:
        return _raise_error("The argument '{}' could not be converted to "
                            "a tuple".format(arg), TypeError,
                            raise_error=raise_error)

    if length is not None and len(arg) != length:
        return _raise_error("The argument tuple '{}' must be of length "
                            "'{}'".format(arg, length), ValueError,
                            raise_error=raise_error)

    if type is not None:
        try:
            arg = tuple(type(i) for i in arg)
        except TypeError:
            return _raise_error("The items of tuple '{}' could not be "
                                "converted to type '{}'".format(arg, type),
                                TypeError, raise_error=raise_error)
    return arg
