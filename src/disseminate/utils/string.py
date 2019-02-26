"""
String manipulation operations.
"""
import hashlib
import string

import regex
from slugify import slugify


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


def str_to_list(string):
    """Parse a string into a list.

    Parameters
    ----------
    string : str
        The string with list entries separated by semicolons, newlines or
        commas.

    Returns
    -------
    parsed_list : list
        The parsed list with the string split into string pieces.

    Examples
    --------
    >>> str_to_list('one, two, three')
    ['one', 'two', 'three']
    >>> str_to_list('one, 1; two, 2; three, 3')
    ['one, 1', 'two, 2', 'three, 3']
    >>> str_to_list('''
    ... one, 1
    ... two, 2
    ... three, 3''')
    ['one, 1', 'two, 2', 'three, 3']
    >>> str_to_list("friends")
    ['friends']
    """
    pieces_semicolon = string.split(';')

    if len(pieces_semicolon) > 1:
        return [piece.strip() for piece in pieces_semicolon]

    pieces_newline = [piece.strip() for piece in string.split('\n')]
    pieces_newline = list(filter(bool, pieces_newline))  # remove empty items

    if len(pieces_newline) > 1:
        return pieces_newline

    pieces_comma = string.split(',')

    if len(pieces_comma) > 1:
        return [piece.strip() for piece in pieces_comma]

    return [string]


_re_entry = regex.compile(r'^(?P<space_level>\s*)'
                         r'(?P<key>.+?)'
                         r'(?<!\\)\:'  # match ':' but not '\:'
                         r'\s*'
                         r'(?P<value>.*)')


def str_to_dict(string):
    """Parse a string into a dict.

    Parameters
    ----------
    string : str
        The string with dict-like entries separated by colons.

    Returns
    -------
    parsed_dict : dict
        The parsed dict with keys and values as strings.

    Examples
    --------
    >>> string = '''
    ... first: one
    ... second:
    ...   multiline
    ...   entry
    ... third: 3
    ... '''
    >>> d = str_to_dict(string)
    >>> d == {'first': 'one', 'second': '  multiline\\n  entry', 'third': '3'}
    True
    """
    d = dict()

    # Split the string into lines and see which lines have an entry of the
    # form "key: value"
    lines = string.splitlines()

    # Go from line to line and identify which lines are key/value pairs

    # Keep a list of all lines that pertain to a given entry
    current_entry_list = []
    # Keep track of how many spaces were used to define the entry. This is used
    # to place sub-blocks of an entry within the entry.
    current_spaces = None

    for line in lines:
        m = _re_entry.match(line)

        # Workup the line. Strip leading spaces from the line.
        if current_spaces is not None:
            line = line[current_spaces:]

        # Replace escaped colons ('\:') with colons (':')
        line = line.replace("\\:", ":")

        if m is not None:
            # If there'string a match, then we may have a new entry.
            # However, only create a new entry if the space_level is the same
            # as the last entry.
            group_dict = m.groupdict()
            space_level = len(group_dict['space_level'])
            key = group_dict['key'].strip()
            value = group_dict['value']

            if current_spaces is not None and space_level > current_spaces:
                # Not a new entry. Just add the line to the last entry.
                current_entry_list.append(line)
            else:
                # A new entry. Create a new current_entry_list.
                current_spaces = space_level
                current_entry_list = d.setdefault(key, [])
                current_entry_list.append(value)
        else:
            # If there'string not a match, just add the line to the current entry
            current_entry_list.append(line)

    # Convert the entries in the dict from a list of strings to strings
    d = {k: "\n".join(v).strip('\n') for k, v in d.items()}

    return d


class NewlineCounter(object):
    """Count the newlines in strings.

    Parameters
    ----------
    initial : int, optional
        The line number to start the count.

    Examples
    --------
    >>> line = NewlineCounter()
    >>> line("my test\\nline\\nstring")
    3
    >>> line.number
    3
    >>> line("another")
    3
    >>> line("another\\ntwo lines")
    4
    """

    number = None

    def __init__(self, initial=1):
        self.number = initial

    def __call__(self, string):
        """Add the newlines of the given string to the count."""
        self.number += string.count('\n')
        return self.number


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


class StringTemplate(string.Template):
    """A template string used to preprocess strings in disseminate format.

    This class allows for a simple substitution of '$' variables and disallows
    more complicated Python operations.

    Examples
    --------
    >>> StringTemplate("test $friend").substitute(friend='Bill')
    'test Bill'
    """
    delimiter = '$'
    idpattern = r'[a-z][_a-z0-9\.]*'

    def substitute(*args, **kwargs):
        self, *args = args  # allow the "self" keyword be passed
        raise_expcetion = kwargs.pop('raise_exception', True)

        def convert(match):
            # Get the string for the match
            # ex: match_str = '$friend.name'
            match_str = match.group()

            # Split at periods
            # ex: pieces = ['$friend', 'name']
            pieces = match_str.split('.')

            # Reconstruct the pieces into a list of results
            results = pieces[0:1] + ['.' + piece for piece in pieces[1:]]

            # See if the first piece corresponds to an entry in kwargs
            result = results.pop(0)  # ex: piece = '$friend'
            obj = kwargs.get(result[1:], None)
            last_obj = obj

            # Raise an exception, if the key was not found and the key is valid
            if (raise_expcetion and
                obj is None and  # if key not found (i.e. obj is None) and
                result[1:] and   # the key is not empty and
               result[0:2] != self.delimiter*2):  # the delimiter isn't escaped
                raise KeyError(result[1:])

            while results and not isinstance(obj, str) and obj is not None:
                result = results.pop(0)
                obj = getattr(obj, result[1:], None)
                last_obj = obj if obj is not None else last_obj

            if last_obj is not None and obj is None:
                results.insert(0, result)
                results.insert(0, str(last_obj))
            elif last_obj is not None:
                results.insert(0, str(last_obj))
            else:
                results.insert(0, result)

            return ''.join(results)

        return self.pattern.sub(convert, self.template)

    def safe_substitute(*args, **kwargs):
        self, *args = args  # allow the "self" keyword be passed
        kwargs['raise_exception'] = False
        return self.substitute(*args, **kwargs)
