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
        A list of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

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


def set_attribute(attrs, attribute, method='r'):
    """Set an attribute in an attributes list.

    Parameters
    ----------
    attrs: list
        A list of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute: 2-ple or str
        An attribute to set. It's either a 2 item tuple (attribute name, attribute value) or
        a positional attribute string.
    method: char
        'r': replace (default)
        'a': append

    Returns
    -------
    attrs: list
        A list of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

    Examples
    --------
    >>> set_attribute([('class', 'base bttnred'), ('style', 'media'), 'red'],
    ...                ('class', 'standard'), method='r')
    [('class', 'standard'), ('style', 'media'), 'red']
    >>> set_attribute([('class', 'base bttnred'), ('style', 'media'), 'red'],
    ...                ('class', 'standard'), method='a')
    [('class', 'base bttnred'), ('style', 'media'), 'red', ('class', 'standard')]
    >>> set_attribute([('class', 'base bttnred'), ('style', 'media'), 'red'],
    ...                'red', method='r')
    [('class', 'base bttnred'), ('style', 'media'), 'red']
    >>> set_attribute([('class', 'base bttnred'), ('style', 'media'), 'red'],
    ...                'red', method='a')
    [('class', 'base bttnred'), ('style', 'media'), 'red', 'red']
    """
    if method == 'a':
        new_attrs = list(attrs)
        new_attrs.append(attribute)
        return new_attrs
    else:
        if hasattr(attribute, '__iter__') and len(attribute) == 2:
            name, value = attribute
            new_attrs = []
            attr_found = False

            for attr in attrs:
                if (hasattr(attr, '__iter__')
                   and len(attr) == 2
                   and attr[0] == name):

                    attr_found = True
                    new_attrs.append((name, value))
                else:
                    new_attrs.append(attr)
            if not attr_found:
                new_attrs.append((name, value))
            return new_attrs
        else:
            new_attrs = list(attrs)
            if attribute not in new_attrs:
                new_attrs.append(attribute)
            return new_attrs
