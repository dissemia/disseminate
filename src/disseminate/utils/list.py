"""
Utilities for lists.
"""
import hashlib


def uniq(l, key=None):
    """Find the unique items in the given list while preserving the order of
    the list and optionnally using a key mapping function.

    Parameters
    ----------
    l : list
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
    seen = set()
    # Get the mappings of the list items, base on the key
    if key is None:
        uniques = [item for item in l if item not in seen
                   and not seen.add(item)]
    else:
        uniques = [item for item in l if key(item) not in seen
                   and not seen.add(key(item))]
    return uniques


def dupes(l, key=None):
    """Find duplicates in a list using, optionally, a key mapping function.

    Parameters
    ----------
    l : list
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
    dupes = []
    for item in l:
        mapping = item if key is None else key(item)
        counts[mapping] = counts.setdefault(mapping, 0) + 1

    if key is None:
        return [item for item in l if counts[item] > 1]
    else:
        return [item for item in l if counts[key(item)] > 1]


def unwrap(l):
    """Unwrap lists with only a single item.

    Parameters
    ----------
    l : list
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
    new_l = l[0] if isinstance(l, list) and len(l) == 1 else l
    if isinstance(new_l, list) and len(new_l) == 1:
        new_l = unwrap(new_l)
    return new_l


def chunks(l, N):
    """Return a generator in chunks of N.

    Parameters
    ----------
    l : Union[List, Tuple]
        The iterable to break into chunks.
    N : int
        The size of chunks.

    Returns
    -------
    Generator
        A generator with sublists of items from 'l' broken into chunks of 'N'.
    """
    for i in range(0, len(l), N):
        yield l[i:i + N]


def md5hash(l):
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
                else str(i) for i in l).encode()
    return hashlib.md5(s).hexdigest()
