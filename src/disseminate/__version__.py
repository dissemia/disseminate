def get_version(ver_tuple):
    """Convert a version tuple to a version string that is PEP 440 compliant.

    Parameters
    ----------
    ver_tuple: tuple
        A tuple with five items for the version number.
        - item 1: Major version number
        - item 2: Minor version number
        - item 3: Update number
        - item 4: Release type. Either 'final', 'alpha', 'beta', 'rc
        - item 5: Release number

    Returns
    -------
    str
        The version string.

    Examples
    --------
    >>> get_version((2,1,0, 'final', 3))
    '2.1'
    >>> get_version((2,1,0, 'rc', 3))
    '2.1rc3'
    >>> get_version((2,1,1, 'final', 0))
    '2.1.1'
    >>> get_version((2,1,2, 'alpha', 1))
    '2.1.2a1'
    >>>
    """
    assert len(ver_tuple) == 5
    assert ver_tuple[3] in ('final', 'alpha', 'beta', 'rc')
    ver = '.'.join(map(str, ver_tuple[0:2]))
    if ver_tuple[2] > 0:
        ver += '.{}'.format(ver_tuple[2])
    mapping = {'final': '', 'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
    ver += mapping[ver_tuple[3]]
    if ver_tuple[3] in ('alpha', 'beta', 'rc') and ver_tuple[4] > 0:
        ver += str(ver_tuple[4])
    return ver


# The version tuple.
#
# - Item 0 is the major version, usually reserved for major features and API
#   changes
#
# - Item 1 is the minor revision, usually for standard new features.
#
# - Item 2 is the post release number, usually reserved for bug fixes and
#   updates
#
# - Item 3 is the release type. Either 'alpha', 'beta', 'rc' or 'final'
#
# - Item 4 is the release type number. ex: rc3 is the third release candidate.
#   This number is only non-zero for 'alpha', 'beta' and 'rc' software.
VERSION = (2, 3, 3, 'final', 0)

__version__ = get_version(VERSION)
