"""
String manipulation operations.
"""
from slugify import slugify
import hashlib


def hashtxt(text, truncate=10):
    """Creates a hash from the given text."""
    return (hashlib.md5(text.encode()).hexdigest() if truncate is None else
            hashlib.md5(text.encode()).hexdigest()[:truncate])


def titlelize(string, truncate=True, capitalize=False):
    """Given a string, generate a condensed title.

    >>> titlelize("My example caption. It has 2 sentences")
    'My example caption'
    >>> titlelize("My example caption. It has 2 sentences", capitalize=True)
    'My Example Caption'
    """
    # Strip extra newlines and join to a single string
    lines = list(filter(bool, string.split('\n')))
    string = ' '.join(lines)

    # Break at end of sentence periods
    pieces = string.split('. ')

    # Truncate, if needed
    if truncate:
        string = pieces[0]
    else:
        string = ". ".join(pieces)

    # capitalize words, if specified, and return the joined string.
    # This function also strips extra spaces between words
    pieces = string.split(' ')
    pieces = list(filter(bool, pieces))
    if capitalize:
        if len(pieces) > 2:
            pieces = ([pieces[0].title()] +
                      [piece.title() if piece not in ('in', 'to', 'a')
                       else piece for piece in pieces[1:]])
    string = " ".join(pieces)

    return string.strip('.')


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
    >>> str_to_list("src/file1.tex\\nsrc/file2.tex\\nsrc/file 3.tex")
    ['src/file1.tex', 'src/file2.tex', 'src/file 3.tex']
    """
    # Convert the string to a list
    if isinstance(string, str):
        lst = string.splitlines()
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

