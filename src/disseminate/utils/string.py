"""
String manipulation operations.
"""
from slugify import slugify


def find_basestring(strings):
    """Evaluate the common base string amongst a list of strings.

    Parameters
    ----------
    strings : list of str
        A list of strings

    Returns
    -------
    base_string : str
        The common base string.

    Examples
    --------
    >>> find_basestring(['tester', 'test', 'testest'])
    'test'
    >>> find_basestring(['tester', 'test', 'testest', 'smile'])
    ''
    """
    # Get one of the strings
    base = strings[0]

    # Chop off from the end until a base string that is common to all is found
    base_found = all(i.startswith(base) for i in strings)

    while not base_found and base:
        base = base[:-1]
        base_found = all(i.startswith(base) for i in strings)

    return base


def str_to_list(string, delimiter=','):
    """Convert a string (or list) into a split list of strings.

    Parameters
    ----------
    string : str
        The string to split into a list.
    delimiter : str, optional
        The optional delimiter used to split pieces of a string.

    Returns
    -------
    split_list
        A list of strings split by delimiter and spaces.

    Examples
    --------
    >>> str_to_list("my friend, the robot")
    ['my friend', 'the robot']
    >>> str_to_list(['my friend', ' the robot'])
    ['my friend', 'the robot']
    """
    # Convert the string to a list
    if isinstance(string, str):
        lst = [string]
    elif hasattr(string, '__iter__'):
        lst = list(string)

    # Breakup the pieces by delimiter
    returned_list = []
    for item in lst:
        returned_list += [s.strip() for s in item.split(delimiter)]
    return returned_list


class Metastring(str):
    """A string class that holds metadata.

    Examples
    --------
    >>> s = Metastring('test', line_offset=3)
    >>> print(s)
    test
    >>> print(hasattr(s, 'line_offset'))
    True
    >>> print(s.line_offset)
    3
    """
    def __new__(cls, content, **kwargs):
        new_str = super(Metastring, cls).__new__(cls, content)
        new_str.__dict__.update(kwargs)
        return new_str

