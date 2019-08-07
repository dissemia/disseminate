"""
Utilities for checkers.
"""
import re
import operator


def name_and_version(string):
    """Parse the name and version from a package name string with an optional
    specifier.

    Parameters
    ----------
    string : str
        The string with a name and version to parase.

    Returns
    -------
    name, operator, version : Union[None, \
        Tuple[str, Union[operator, None], Union[None, Tuple[int]]]
        The name, operator and version for a package.
        None, if the string couldn't be parsed.

    Examples
    --------
    >>> name_and_version('test')
    ('test', None, None)
    >>> name_and_version('test-ab_one')
    ('test-ab_one', None, None)
    >>> name_and_version('test-ab_one>=0.3.1')
    ('test-ab_one', <built-in function ge>, (0, 3, 1))
    >>> name_and_version('new-package>1.2')
    ('new-package', <built-in function gt>, (1, 2))
    >>> name_and_version('jinja2>=2.10')
    ('jinja2', <built-in function ge>, (2, 10))
    """

    m = re.search(r'([\w\.\-\_]+)'  # match package name
                  r'\s*(==|>=|<=|>|<|!=)?\s*'  # operator
                  r'([\d\.]+)?',  # version number
                  string)

    if m is None:
        # The string couldn't be parse. Return None
        return None

    name = m.group(1)
    op = m.group(2)
    version = m.group(3)

    # Convert the operator
    if op is not None:
        op_mapping = {'==': operator.eq,
                      '>': operator.gt,
                      '<': operator.lt,
                      '>=': operator.ge,
                      '<=': operator.le,
                      '!=': operator.ne}
        op = op_mapping[op]

    # Convert the version to a tuple of integers
    if version is not None:
        version = tuple(map(int, version.split('.')))

    return name, op, version
