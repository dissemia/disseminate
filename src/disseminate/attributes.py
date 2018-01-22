import regex

re_attrs = regex.compile(r'((?P<key>\w+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|\w+))'
                         r'|(?P<position>\w+))')


def parse_attributes(s):
    """Parses an attribute string into an OrderedDict of attributes.

    Parameters
    ----------
    s: str
        Input string of attributes of the form: "key1 = value1 key2 = value2"

    Returns
    -------
    attrs: list
        A list of either 2-ple strings (key, value) or strings (positional
        arguments)

    Examples
    --------
    >>> parse_attributes("data=one red=two")
    [('data', 'one'), ('red', 'two')]
    >>> parse_attributes(" class='base bttnred' style= media red")
    [('class', 'base bttnred'), ('style', 'media'), 'red']
    >>> parse_attributes("class='base btn' skip")
    [('class', 'base btn'), 'skip']
    """
    attrs = []

    for m in re_attrs.finditer(s):
        d = m.groupdict()
        if d.get('key', None) and d.get('value', None):
            attrs.append((d['key'], d['value'].strip('"').strip("'")))
        elif d.get('position', None):
            attrs.append(d['position'].strip("'").strip('"'))

    return attrs