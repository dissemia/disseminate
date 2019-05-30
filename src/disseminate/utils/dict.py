"""
Utility functions for dictionaries.
"""


def find_entry(dicts, *keys, suffix=None, sep='_'):
    """Search dictionaries for entries with string keys constructed from
    ordred combinations of the specified keys.

    Dictionaries are searched in order of preference.
    String keys are constructed with parts constructed by joining the parts
    with the sep string.

    Parameters
    ----------
    dicts : Union[dict, Tuple[dict], List[dict]]
        One or more dictionaries to find entries in.
    keys : str
        One or more items to construct keys.
    suffix : Optional[str]
        If specified, try appending the given suffix to generate the combined
        key before trying the combined key itself.
    sep : Optional[str]
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
    >>> find_entry(d, 'starter', 'middle1', suffix='term')
    1
    >>> find_entry(d, 'starter', 'middle1')
    2
    >>> find_entry(d, 'starter', 'middle2', suffix='term')
    3
    >>> find_entry(d, 'starter', 'middle2' )
    4
    >>> find_entry(d, 'starter', 'term')
    5
    >>> find_entry(d, 'starter')
    6
    """
    # Wrap dict in a list
    dicts = [dicts] if isinstance(dicts, dict) else dicts

    for d in dicts:
        num_keys = len(keys)
        while num_keys > 0:
            trial = sep.join(keys[0:num_keys])
            trial_suffix = (sep.join((trial, suffix))
                            if suffix is not None else trial)

            for t in (trial_suffix, trial):
                if t in d:
                    return d[t]

            num_keys -= 1

    msg = "Could not find a key constructed from '{keys}'"
    raise KeyError(msg.format(keys=keys))
