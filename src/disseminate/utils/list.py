"""
Utilities for lists.
"""
import hashlib
from itertools import filterfalse


def uniq(lst, key=None):
    """Find the unique items in the given list while preserving the order of
    the list and optionally using a key mapping function.

    Parameters
    ----------
    lst : list
        The list to check for duplicates.
    key : Optional[Callable]
        A mapping function that takes a list item and returns an alternate
        value to compare for unique entries.

    Examples
    --------
    >>> uniq([1, 2, 2, 3, 3, 3, 4, 5, 6, 6, 7])
    [1, 2, 3, 4, 5, 6, 7]
    >>> uniq([(1, 'a'), (2, 'a'), (3, 'b'), (4, 'c')], key=lambda i:i[1])
    [(1, 'a'), (3, 'b'), (4, 'c')]
    >>> uniq([(1, 'a'), (2, 'a'), (3, 'b'), (4, 'c')], key=lambda i:i[0])
    [(1, 'a'), (2, 'a'), (3, 'b'), (4, 'c')]
    """
    return list(unique_everseen(lst, key=key))


def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen.
    """
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def dupes(lst, key=None):
    """Find duplicates in a list using, optionally, a key mapping function.

    Parameters
    ----------
    lst : list
        The list to check for duplicates.
    key : Optional[Callable]
        A mapping function that takes a list item and returns an alternate
        value to compare for duplicates.

    Examples
    --------
    >>> dupes([1, 2, 2, 3, 3, 3, 4, 5, 6, 6, 7])
    [2, 2, 3, 3, 3, 6, 6]
    >>> dupes([(1, 'a'), (2, 'a'), (3, 'b'), (4, 'c')], key=lambda i:i[1])
    [(1, 'a'), (2, 'a')]
    >>> dupes([(1, 'a'), (2, 'a'), (3, 'b'), (4, 'c')], key=lambda i:i[0])
    []
    """
    counts = dict()
    for item in lst:
        mapping = item if key is None else key(item)
        counts[mapping] = counts.setdefault(mapping, 0) + 1

    if key is None:
        return [item for item in lst if counts[item] > 1]
    else:
        return [item for item in lst if counts[key(item)] > 1]


def unwrap(lst):
    """Unwrap lists with only a single item.

    Parameters
    ----------
    lst : list
        The list to unwrap

    Returns
    -------
    unwrapped_list : list
        The unwrapped list

    Examples
    --------
    >>> unwrap([1, 2, 3])
    [1, 2, 3]
    >>> unwrap([1])
    1
    >>> unwrap([[1]])
    1
    >>> unwrap([[[3]]])
    3
    """
    new_l = lst[0] if isinstance(lst, list) and len(lst) == 1 else lst
    if isinstance(new_l, list) and len(new_l) == 1:
        new_l = unwrap(new_l)
    return new_l


def flatten(lst):
    """Flatten a list of lists.

    Examples
    --------
    >>> list(flatten([1, 2, 3]))
    [1, 2, 3]
    >>> list(flatten([[1, 2, 3], [4, 5, 6]]))
    [1, 2, 3, 4, 5, 6]
    >>> list(flatten([[1,2], [3, [4, 5], 6]]))
    [1, 2, 3, 4, 5, 6]
    """
    for element in lst:
        if isinstance(element, list):
            yield from flatten(element)
        else:
            yield element


def chunks(lst, N):
    """Return a generator in chunks of N.

    Parameters
    ----------
    lst : Union[List, Tuple]
        The iterable to break into chunks.
    N : int
        The size of chunks.

    Returns
    -------
    Generator
        A generator with sublists of items from 'l' broken into chunks of 'N'.
    """
    for i in range(0, len(lst), N):
        yield lst[i:i + N]


def md5hash(lst):
    """Generates a hash of a list or tuple.

    Examples
    --------
    >>> md5hash(('a', 'b', 1))
    '68b6a776378decbb4a79cda89087c4ce'
    >>> md5hash(('a', 'b', '1'))
    '68b6a776378decbb4a79cda89087c4ce'
    >>> md5hash(['a', [1, 'b'], 'c'])
    '1c81219649292a2ef9240fc997353078'
    >>> md5hash(['a', ['1', 'b'], 'c'])
    '1c81219649292a2ef9240fc997353078'
    """
    s = ''.join(md5hash(i) if isinstance(i, list) or isinstance(i, tuple)
                else str(i) for i in lst).encode()
    return hashlib.md5(s).hexdigest()


def transpose(lst):
    """Transpose a list of lists

    Examples
    --------
    >>> transpose([[1, 2, 3], [4, 5, 6]])
    [[1, 4], [2, 5], [3, 6]]
    >>> transpose([[1, 2, 3], [4, 5]])  # Discard mismatched list entries
    [[1, 4], [2, 5]]
    >>> transpose([[1, 2], [4, 5, 6]])  # Discard mismatched list entries
    [[1, 4], [2, 5]]
    """
    return list(map(list, zip(*lst)))
