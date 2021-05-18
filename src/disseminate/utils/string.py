"""
String manipulation operations.
"""
import hashlib
from itertools import groupby

import regex
from slugify import slugify  # noqa: F401

from .. import settings


def hashtxt(text, truncate=10):
    """Creates a hash from the given text."""
    text = text if isinstance(text, bytes) else text.encode()
    return (hashlib.md5(text).hexdigest() if truncate is None else
            hashlib.md5(text).hexdigest()[:truncate])


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


def nicejoin(*items, sep=', ', term=' and '):
    """Join a sequence of strings with a separator and an alternative terminal
    separator.

    Parameters
    ----------
    *items : Tuple[str]
        A sequence of strings to join.
    sep : Optional[str]
        The separator to use for all items, other than the last item.
    term : Optional[str]
        The last separator to use in joining items.

    Returns
    -------
    joined_string : str
        The joined string.

    Examples
    --------
    >>> nicejoin('Bill', 'Ted', 'Frances')
    'Bill, Ted and Frances'
    >>> nicejoin('Bill', 'Ted', 'Frances', term=' or ')
    'Bill, Ted or Frances'
    >>> nicejoin('Bill', 'Ted', 'Frances')
    'Bill, Ted and Frances'
    >>> nicejoin('Bill', 'Ted')
    'Bill and Ted'
    >>> nicejoin('Bill')
    'Bill'
    """
    if len(items) > 1:
        return sep.join(items[:-1]) + term + items[-1]
    elif len(items) == 1:
        return items[0]
    else:
        return ''


def space_indent(s, number=4):
    r"""Indent a text block by the specified number of spaces.

    Parameters
    ----------
    s : str
        The string the indent
    number : Optional[int]
        The number of spaces to indent by.

    Returns
    -------
    indented_string : str
        The indented string.

    Examples
    --------
    >>> space_indent('my test')
    '    my test'
    >>> t=space_indent("my block\n of text\nwith indents.")
    >>> print(t)
        my block
         of text
        with indents.
    """
    return '\n'.join(" " * number + t for t in s.splitlines())


_re_newline_space = regex.compile(r'\s*\n\s*')


def stub(s):
    """Takes a string, like a docstring, and returns only the first
    line.

    Parameters
    ----------
    s : str
        The string to generate a stub for.

    Returns
    -------
    stub : str
        The string with its first line stripped.

    Examples
    --------
    >>> stub(stub.__doc__)
    'Takes a string, like a docstring, and returns only the first line.'
    """
    first = s.split('\n\n')[0]
    return _re_newline_space.sub(' ', first,)


_re_multilines = regex.compile(r'(?:\n{2,})')


def strip_multi_newlines(s):
    r"""Strip multiple consecutive newlines in a string.

    Parameters
    ----------
    s : str
        String to strip multiple consecutive newlines from.

    Returns
    -------
    stripped_string : str
        The same string with multiple consecutive newlines replaced to single
        newlines.

    Examples
    --------
    >>> strip_multi_newlines("This is my\nfirst string.")
    'This is my\nfirst string.'
    >>> strip_multi_newlines("This is my\n\nsecond string.")
    'This is my\nsecond string.'
    """
    return _re_multilines.sub("\n", s)


def strip_end_quotes(s):
    """Strip matched quotes from the ends a string.

    Parameters
    ----------
    s : str
        String to strip matched quotes.

    Returns
    -------
    stripped_string : str
        The same string with matched quotes striped.

    Examples
    --------
    >>> strip_end_quotes('This is my "test" string.')
    'This is my "test" string.'
    >>> strip_end_quotes('"This is my test string"')
    'This is my test string'
    >>> strip_end_quotes('"This is my test string "')
    'This is my test string '
    """
    if '\n' in s:
        # Newlines, process each individually
        return '\n'.join(map(strip_end_quotes, s.splitlines()))

    for char in "\'\"":
        if s.count(char) % 2 == 0:  # even number of quotes
            pieces = s.split(char)
            if pieces[0].strip() == '' and pieces[-1].strip() == '':
                return ''.join((pieces[0], char.join(pieces[1:-1]),
                                pieces[-1]))

    return s


_re_find_capitals = regex.compile(r'[A-Z][^A-Z]*')


def convert_camelcase(string, sep='_'):
    """Convert a camel-case string to a string to a lower-case string with
    a seperator character.

    Parameters
    ----------
    string : str
        The camel-case string to convert
    sep : Optional[str]
        The separator character.

    Returns
    -------
    processed_string : str
        The converted string

    Examples
    --------
    >>> convert_camelcase('ProcessContext')
    'process_context'
    >>> convert_camelcase('processcontext')
    'processcontext'
    >>> convert_camelcase('ProcessContext', '.')
    'process.context'
    """
    pieces = _re_find_capitals.findall(string)
    if pieces:
        return sep.join(i.lower() for i in pieces)
    else:
        return string


def find_basestring(strings):
    """Evaluate the common base string amongst a list of strings.

    Parameters
    ----------
    strings : List[str]
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


def str_to_dict(string, strip_quotes=True):
    r"""Parse a string into a dict.

    Parameters
    ----------
    string : str
        The string with dict-like entries separated by colons.
    strip_quotes : Optional[bool]
        If True, matched quotes ('") are stripped at the ends of value strings.

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
    >>> d == {'first': 'one', 'second': '  multiline\n  entry', 'third': '3'}
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
            # If there'string not a match, just add the line to the current
            # entry
            current_entry_list.append(line)

    # Convert the entries in the dict from a list of strings to strings
    if strip_quotes:
        d = {k: strip_end_quotes("\n".join(v).strip('\n'))
             for k, v in d.items()}
    else:
        d = {k: "\n".join(v).strip('\n') for k, v in d.items()}

    return d


def group_strings(lst):
    """Group adjacent strings in a list and remove empty strings.

    Parameters
    ----------
    lst : Union[list, str or :obj:`Tag <.Tag>`]
        An AST comprising a strings, tags or lists of both.

    Returns
    -------
    processed_list
        The list with the strings grouped and cleaned up

    Examples
    --------
    >>> group_strings(lst=['a', 'b', '', 3, '', 4, 5, 'f'])
    ['ab', 3, 4, 5, 'f']
    >>> group_strings(lst=['a', 'b', 'c', 3, 'd', 'e', 4, 5, 'f'])
    ['abc', 3, 'de', 4, 5, 'f']
    """
    if hasattr(lst, 'content'):
        lst.content = group_strings(lst.content)
    elif isinstance(lst, list):
        # Remove empty strings
        new_list = list(filter(bool, lst))
        lst.clear()
        lst += new_list

        # Join consecutive string elements
        new_list = []
        for cond, group in groupby(lst, key=lambda x: isinstance(x, str)):
            if cond:
                new_list.append(''.join(group))
            else:
                new_list += list(group)
        lst.clear()
        lst += new_list

        # Iterate over the items
        for i, item in enumerate(lst):
            if not isinstance(item, str):
                lst[i] = group_strings(item)

    return lst


_re_macro = regex.compile(r"(?P<macro>" +
                          settings.tag_prefix +  # tag prefix. e.g. '@'
                          r"[\w\.]+)"
                          r"({\s*})?"  # match empty curly brackets
                          )


def replace_macros(s, *dicts):
    """Replace the macros and return a processed string.

    Macros are simple string replacements from context entries whose keys
    start with the tag_prefix character (e.g. '@test'). The
    process_context_asts will ignore macro context entries that have keys
    which start with this prefix. This is to preserve macros as strings.

    Parameters
    ----------
    s : str
        The input string to replace macros within.
    *dicts : Tuple[dict]
        One or more dicts containing variables defined for a specific document.
        Values will be replaced with the first dict found with that value.

    Returns
    -------
    processed_string : str
        A string with the macros replaced.

    Raises
    ------
    MacroNotFound
        Raises a MacroNotFound exception if a macro was included, but it could
        not be found.
    """
    # Replace the values
    def _substitute(m):
        # Get the string for the match
        # ex: macro = '@friend.name'
        d = m.groupdict()
        macro = d['macro']

        # Split at periods
        # ex: pieces = ['@friend', 'name']
        pieces = macro.split('.')

        # See if the first piece corresponds to an entry in kwargs
        obj = None
        while pieces:
            piece = pieces.pop(0)

            if obj is None and any(piece in d for d in dicts):
                for d in dicts:
                    if piece in d:
                        obj = d[piece]
                        break
            elif hasattr(obj, piece):
                obj = getattr(obj, piece)
            else:
                # Match not found. Re-add piece to the pieces list
                pieces.insert(0, piece)
                break

        # Convert obj and the remaining pieces to a string
        if obj is None:
            # no match found. Return the match
            return m.group()
        else:
            # match(es) found, replace with the string
            return str(obj) + ''.join('.' + piece for piece in pieces)

    # Return a string with the dicts substituted. Keep substituting until
    # all dicts are replaced or the string is no longer changing
    s, num_subs = _re_macro.subn(_substitute, s)
    last_num_subs = 0
    while num_subs > 0 and num_subs > last_num_subs:
        last_num_subs = num_subs
        s, num_subs = _re_macro.subn(_substitute, s)

    return s
