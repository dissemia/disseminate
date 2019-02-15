"""
Utility functions for dictionaries.
"""


def find_entry(dicts, major, intermediate=None, minor=None, spacer='_'):
    """Search dictionaries for entries with string keys constructed from
    combinations of the specified major, intermediate and minor classifications
    and separated by spacer.

    Dictionaries are searched in order of preference.
    String keys are constructed with parts constructed from the major,
    intermediate, and minor classification, from the most specific to the more
    general, by joining the parts with the spacer string.

    Parameters
    ----------
    *dicts : tuple of dicts
        The dictionary with format strings as values
    major : string or tuple of str
        The major classification, starts the key string.
    intermediate : string or tuple of str, optional
        The intermediate classification, specified after the major
        classification.
    minor : str or tuple of str, optional
        The minor classification, specified after the major and intermediate
        classifications.
    spacer : str, optional
        The separator for joining key parts into a key.

    Returns
    -------
    value
        The value from the dict for the best match.

    Raises
    ------
    KeyError
        Raised if a key was not found.

    Examples
    --------
    >>> d = {'starter_middle1_term': 1,
    ...      'starter_middle1': 2,
    ...      'starter_middle2_term': 3,
    ...      'starter_middle2': 4,
    ...      'starter_term': 5,
    ...      'starter': 6}
    >>> find_entry(d, 'starter', ('middle1', 'middle2'), 'term')
    1
    >>> find_entry(d, 'starter', ('middle1', 'middle2'),)
    2
    >>> find_entry(d, 'starter', ('middle2',), 'term')
    3
    >>> find_entry(d, 'starter', ('middle2',), )
    4
    >>> find_entry(d, 'starter', None, 'term')
    5
    >>> find_entry(d, 'starter')
    6
    """
    # Set missing parameters
    intermediate = tuple() if intermediate is None else intermediate
    minor = tuple() if minor is None else minor

    # wrap the parameters in tuples
    major = (major,) if isinstance(major, str) else major
    intermediate = (intermediate,) if isinstance(intermediate, str) else intermediate
    minor = ((minor,) if isinstance(minor, str) else
                   minor)
    dicts = (dicts,) if isinstance(dicts, dict) else dicts

    for dictionary in dicts:
        for starter in major:
            for middle in intermediate:
                for terminator in minor:
                    key = spacer.join((starter, middle, terminator))
                    if key in dictionary:
                        return dictionary[key]

                key = spacer.join((starter, middle))
                if key in dictionary:
                    return dictionary[key]

            for terminator in minor:
                key = spacer.join((starter, terminator))
                if key in dictionary:
                    return dictionary[key]

            if starter in dictionary:
                return dictionary[starter]

    msg = ("Could not find a key constructed from the parts '{major}', "
           "'{intermediate}' and '{minor}'")
    raise KeyError(msg.format(major=major, intermediate=intermediate,
                              minor=minor))
