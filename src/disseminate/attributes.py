"""
Functions for parsing and processing attributes.

Attributes are optional parameters added to a tag with square brackets.

    ex: "@section[id=title one]{My first section}"

Attributes comprise keyword attributes (i.e. 'id=title') and positional
attributes (i.e. 'one'). Additionally, attributes may include target-specific
attributes that are only used for a given target. For example,

    "@img[html.width=300]{media/image.jpg}"

The 'html.width' keyword argument will be parsed as 'width=300' for '.html'
targets.

"""
from collections import OrderedDict
import regex


class TagAttributeError(Exception): pass


re_attrs = regex.compile(r'((?P<key>[\w\.]+)'
                         r'\s*=\s*'
                         r'(?P<value>("[^"]*"'
                         r'|\'[^\']*\''
                         r'|[^\s\]]+))'
                         r'|(?P<position>\w+))')


def parse_attributes(s):
    """Parses an attribute string into a tuple of attributes.

    Parameters
    ----------
    s: str
        Input string of attributes. Attributes come in two forms: positional
        attributes and keyword attributes (kwargs), and attributes strings have
        the following form: "key1=value1 key2=value2 value3"

    Returns
    -------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

    Examples
    --------
    >>> parse_attributes("data=one red=two")
    (('data', 'one'), ('red', 'two'))
    >>> parse_attributes(" class='base bttnred' style= media red")
    (('class', 'base bttnred'), ('style', 'media'), 'red')
    >>> parse_attributes("class='base btn' skip")
    (('class', 'base btn'), 'skip')
    """
    attrs = []

    for m in re_attrs.finditer(s):
        d = m.groupdict()
        if d.get('key', None) and d.get('value', None):
            attrs.append((d['key'], d['value'].strip('"').strip("'")))
        elif d.get('position', None):
            attrs.append(d['position'].strip("'").strip('"'))

    return tuple(attrs)


def get_attribute_value(attrs, attribute_name, target=None):
    """Get an attribute's value from a keyword attribute key or positional
    attribute value.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute: 2-ple or str
        An attribute to set. It's either a 2 item tuple (attribute id,
        attribute value) or a positional attribute string.

    Returns
    -------
    attr_value: string or None
        The attribute value, if found, or None if it was not found.

    Examples
    --------
    >>> get_attribute_value((('class', 'base bttnred'), ('style', 'media')),
    ...                     'class')
    'base bttnred'
    >>> get_attribute_value((('class', 'base bttnred'), ('style', 'media')),
    ...                     'classes')
    >>> get_attribute_value((('class', 'base bttnred'), 'red'),
    ...                     'red')
    'red'
    >>> get_attribute_value((('class', 'base bttnred'), 'red'),
    ...                     'blue')
    >>> get_attribute_value((('html.label', 'test1'), ('tex.label', 'test2')),
    ...                     'label', target='.tex')
    'test2'
    """
    # Format the attrs
    if isinstance(attrs, str):
        attrs = parse_attributes(attrs)
    elif attrs is None:
        attrs = tuple()

    processed_attrs = filter_attributes(attrs=attrs,
                                        attribute_names=[attribute_name],
                                        target=target,
                                        raise_error=False)
    if len(processed_attrs) > 0:
        attr = processed_attrs[0]
        if hasattr(attr, '__iter__') and len(attr) == 2:
            return attr[1]
        elif isinstance(attr, str):
            return attr
        else:
            return None
    else:
        return None


def remove_attribute(attrs, attribute_name):
    """Remove the given attribute for the attribute tuple.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional attributes)
    attribute: 2-ple or str
        An attribute to set. It's either a 2 item tuple (attribute id,
        attribute value) or a positional attribute string.

    Returns
    -------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

    Examples
    --------
    >>> remove_attribute((('class', 'base bttnred'), 'red'),
    ...                  attribute_name= 'red')
    (('class', 'base bttnred'),)
    >>> remove_attribute((('class', 'base bttnred'), 'red'),
    ...                  attribute_name= 'class')
    ('red',)
    """
    # Format the attrs
    if isinstance(attrs, str):
        attrs = parse_attributes(attrs)
    elif attrs is None:
        attrs = tuple()

    # Find the attribute that matches
    filtered_attributes = []
    for attr in attrs:
        # Deal with a 2-ple attribute
        if (hasattr(attr, '__iter__') and
                len(attr) == 2 and
                attr[0] == attribute_name):
            continue
        elif isinstance(attr, str) and attr == attribute_name:
            continue
        filtered_attributes.append(attr)

    return tuple(filtered_attributes)


def set_attribute(attrs, attribute, method='r'):
    """Set an attribute in an attributes tuple.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (keyword
        attributes) or strings (positional attributes)
    attribute: 2-ple or str
        An attribute to set. It's either a 2 item tuple (attribute id,
        attribute value) or a positional attribute string.
    method: char
        'r': replace (short)
        'a': append

    Returns
    -------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

    Examples
    --------
    >>> set_attribute((('class', 'base bttnred'), ('style', 'media'), 'red'),
    ...                ('class', 'standard'), method='r')
    (('class', 'standard'), ('style', 'media'), 'red')
    >>> set_attribute((('class', 'base bttnred'), ('style', 'media'), 'red'),
    ...                ('class', 'std'), method='a')
    (('class', 'base bttnred'), ('style', 'media'), 'red', ('class', 'std'))
    """
    attrs = tuple() if attrs is None else attrs

    if method == 'a':
        new_attrs = list(attrs)
        new_attrs.append(attribute)
        return tuple(new_attrs)
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
            return tuple(new_attrs)
        else:
            new_attrs = list(attrs)
            if attribute not in new_attrs:
                new_attrs.append(attribute)
            return tuple(new_attrs)


def filter_attributes(attrs, attribute_names=None, target=None,
                      raise_error=False):
    """Filter a tuple of attributes (attrs) to only include those that match
    names (or positional attributes) in the given list.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute_names: list of str or None, optional
        A list of attribute names and positional arguments to include in the
        returned result. Matches are case-sensitive.
        If None, no attribute names are filtered.
    target: str, optional
        By default (i.e. when target is None), target-specific attributes are
        removed. Target-specific attributes start with the target id and a
        period. For example, 'tex.width' is the 'width' attribute for '.tex'
        targets. If a target is specified, the filtered attributes will only
        include target-specific attributes that match the target, and the
        target-specific part will be stripped.
    raise_error: bool, optional
        If an attribute has been included that is not recognized, raise an
        TagAttributeError.

    Returns
    -------
    attrs: tuple
        A filtered tuple of attributes comprising either 2-ple strings
        (key, value) or strings (positional arguments)

    Raises
    ------
    TagAttributeError
        If raise_error and an attribute is given that is not in the list of
        attribute_names.

    Examples
    --------
    filter_attributes((('class', 'base'), ('style', 'media'), 'red'))
    >>> filter_attributes((('class', 'base'), ('style', 'media'), 'red'),
    ...                   attribute_names=['class', 'red'])
    (('class', 'base'), 'red')
    >>> filter_attributes((('tex.class', 'base'), ('html.class', 'media')),
    ...                   attribute_names=['class', 'red'], target='.tex')
    (('class', 'base'),)
    >>> filter_attributes((('tex.class', 'base'), ('html.class', 'media')),
    ...                   target='.tex')
    (('class', 'base'),)
    >>> filter_attributes((('tex.class', 'base'), ('src', 'image.png')),
    ...                   target='.tex')
    (('class', 'base'), ('src', 'image.png'))
    >>> filter_attributes(('tex.orange', 'red'),
    ...                   target='.tex')
    ('orange', 'red')
    >>> filter_attributes(('tex.orange', 'red'), target=None)
    ('red',)
    """

    new_attrs = []
    # Filter attributes based on target
    target = target.strip('.') if target is not None else ''

    for attr in attrs:
        # See if the attribute matches a target and whether it matches
        # the specified target
        if hasattr(attr, '__iter__') and len(attr) == 2:
            # Deal with an attr that is a 2-ple
            if attr[0].startswith(target + '.'):
                # matches target. ex: 'tex.width'
                new_attrs.append((attr[0].replace(target + '.', ''),
                                  attr[1]))
            elif '.' in attr[0]:
                # attr for another target. ex: 'html.width'
                continue
            else:
                new_attrs.append(attr)
        else:
            # Deal with an attr that is a string
            if attr.startswith(target + '.'):
                # matches target. ex: 'tex.width'
                new_attrs.append(attr.replace(target + '.', ''))
            elif '.' in attr:
                # attr for another target. ex: 'html.width'
                continue
            else:
                new_attrs.append(attr)
    attrs = new_attrs

    if attribute_names is not None:
        new_attrs = []
        # Filter attributes based on attribute names
        for attr in attrs:
            if (hasattr(attr, '__iter__')
               and len(attr) == 2
               and attr[0] in attribute_names):

                new_attrs.append(attr)
            elif attr in attribute_names:
                new_attrs.append(attr)
            elif raise_error:
                msg = "The attribute '{}' is not a valid attribute."
                raise TagAttributeError(msg.format(attr))
        attrs = new_attrs

    return tuple(attrs)


def kwargs_attributes(attrs, attribute_names=None, target=None,
                      raise_error=False):
    """Produce a dict of attributes {key: value} suitable to be used
    as kwargs.

    .. note:: This function ignores arguments.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute_names: list of str, str or None, optional
        - A list of attribute names and positional arguments to include in the
          returned result. Matches are case-sensitive.
        - None - Do not filter attribute names
    target: str, optional
        If specified, filter the target-specific attributes. (See
        filter_attributes)
    raise_error: bool, optional
        If an attribute has been included that is not recognized, raise an
        TagAttributeError.

    Returns
    -------
    kwargs: dict
        A dict with {key: value} pairs for the attributes.

    Examples
    --------
    >>> kwargs_attributes((('class', 'base'), ('style', 'media'), 'red'))
    OrderedDict([('class', 'base'), ('style', 'media')])
    >>> kwargs_attributes((('html.class', 'html'), ('tex.class', 'tex')),
    ...                   target='.html')
    OrderedDict([('class', 'html')])
    """
    processed_attrs = filter_attributes(attrs=attrs,
                                        attribute_names=attribute_names,
                                        target=target,
                                        raise_error=raise_error)

    kwargs = OrderedDict()
    for attr in processed_attrs:
        if hasattr(attr, '__iter__') and len(attr) == 2:
            kwargs[attr[0]] = attr[1]

    return kwargs


def positional_attributes(attrs, target=None, raise_error=False):
    """Produce a tuple of the positional attributes/arguments

    Parameters
    ----------
    attrs : tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    target : string or None
        Filter the positional attributes for target-specific attributes.
    raise_error: bool, optional
        If an attribute has been included that is not recognized, raise an
        TagAttributeError.

    Returns
    -------
    attrs : tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)

    Examples
    --------
    >>> positional_attributes((('class', 'base'), ('style', 'media'), 'red'))
    ('red',)
    >>> positional_attributes(('html.orange', 'tex.red'))
    ()
    >>> positional_attributes(('html.orange', 'tex.red'), target='.html')
    ('orange',)
    """
    processed_attrs = filter_attributes(attrs=attrs,
                                        target=target,
                                        raise_error=raise_error)
    return tuple([a for a in processed_attrs if not isinstance(a, tuple)
                  or not hasattr(a, '__iter__')])


def format_html_attributes(attrs, attribute_names=None, raise_error=False):
    """Format attributes into an options string for html.

    .. note:: If there are target-specific attributes (i.e. they start with
              the target's id with a period, like 'html.width') then
              only the 'html.' attributes are added.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute_names: list of str, optional
        A list of attribute names and positional arguments to include in the
        returned result. Matches are case-sensitive.
    raise_error: bool, optional
        If an attribute has been included that is not recognized, raise an
        TagAttributeError.

    Returns
    -------
    kwargs: dict
        A dict with {key: value} pairs for the attributes.

    Examples
    --------
    >>> format_html_attributes((('class', 'base'), ('style', 'media'), 'red'))
    "class='base' style='media' red"
    >>> format_html_attributes(())
    ''
    >>> format_html_attributes((('tex.width', '100'), ('html.width', '200')))
    "width='200'"
    >>> format_html_attributes((('tex.width', '200'), ))
    ''
    """
    # Convert the given attrs, if needed
    if attrs is None or attrs == '':
        attrs = tuple()
    elif isinstance(attrs, str):
        attrs = parse_attributes(attrs)
    else:
        pass

    if hasattr(attribute_names, '__iter__'):
        processed_attrs = filter_attributes(attrs=attrs,
                                            attribute_names=attribute_names,
                                            target='.html',
                                            raise_error=raise_error)
    else:
        processed_attrs = filter_attributes(attrs=attrs,
                                            target='.html',
                                            raise_error=raise_error)

    if processed_attrs:
        attr_elements = []
        for attr in processed_attrs:
                if isinstance(attr, tuple):
                    attr_elements.append(attr[0] + "='" + attr[1] + "'")
                elif isinstance(attr, str):
                    attr_elements.append(attr)
        return " ".join(attr_elements)
    else:
        return ""


def format_tex_attributes(attrs, attribute_names=None,
                          left_bracket='[', right_bracket=']',
                          raise_error=False):
    """Format attributes into an options string for tex.

    .. note:: If there are target-specific attributes (i.e. they start with
              the target's id with a period, like 'html.width') then
              only the 'tex.' attributes are added.

    Parameters
    ----------
    attrs: tuple
        A tuple of attributes comprising either 2-ple strings (key, value) or
        strings (positional arguments)
    attribute_names: list of str, optional
        A list of attribute names and positional arguments to include in the
        returned result. Matches are case-sensitive.
    left_bracket : str
        The left bracket string to use when enclosing the tex attributes
    right_bracket : str
        The right bracket string to use when enclosing the tex attributes
    raise_error: bool, optional
        If an attribute has been included that is not recognized, raise an
        TagAttributeError.

    Returns
    -------
    formatted_str
        A formatted string for tex.

    Examples
    --------
    >>> format_tex_attributes((('class', 'base'), ('style', 'media'), 'red'))
    '[class=base, style=media, red]'
    >>> format_tex_attributes(())
    ''
    >>> format_tex_attributes((('tex.width', '100'), ('html.width', '200')))
    '[width=100]'
    >>> format_tex_attributes((('html.width', '200'), ))
    ''
    """
    # Convert the given attrs, if needed
    if attrs is None or attrs == '':
        attrs = tuple()
    elif isinstance(attrs, str):
        attrs = parse_attributes(attrs)
    else:
        pass

    if hasattr(attribute_names, '__iter__'):
        processed_attrs = filter_attributes(attrs=attrs,
                                            attribute_names=attribute_names,
                                            target='.tex',
                                            raise_error=raise_error)
    else:
        processed_attrs = filter_attributes(attrs=attrs,
                                            target='.tex',
                                            raise_error=raise_error)

    if processed_attrs:
        attr_elements = []
        for attr in processed_attrs:
                if isinstance(attr, tuple):
                    attr_elements.append('='.join(attr))
                elif isinstance(attr, str):
                    attr_elements.append(attr)
        return left_bracket + ", ".join(attr_elements) + right_bracket
    else:
        return ''
