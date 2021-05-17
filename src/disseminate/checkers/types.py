"""Bases classes for checkers of software dependencies."""


class SoftwareDependency(object):
    """An external software program or package dependency.

    Parameters
    ----------
    name : str
        The name of the external program or package.

    Attributes
    ----------
    path : str
        The path for the external program or package.
    available : Optional[bool]
        True, if dependency is available, False otherwise.
        May also be None if the availability is not determined yet
    """

    __slots__ = ('name', 'path', 'available')

    def __init__(self, name, **kwargs):
        """Initialize dependency with name and attributes."""
        kwargs['name'] = name
        if 'available' not in kwargs:
            kwargs['available'] = None

        for k, v in kwargs.items():
            if k in self.__slots__:
                setattr(self, k, v)

    def __repr__(self):
        return "{}({})".format(self.name,
                               self.available
                               if isinstance(self.available, bool) else
                               'unknown')


class SoftwareDependencyList(object):
    """A listing of software dependencies

    Parameters
    ----------
    category : str
        The category name for the software dependency list.
    *dependencies : Tuple[Union[str, :obj:`SoftwareDependencyList`]
        The listing of dependency names or sub dependency lists.
    """

    __slots__ = ('category', 'dependencies')

    def __init__(self, category, *dependencies):
        """Initialize with category and sub-dependencies."""
        self.category = category
        # if (len(dependencies) == 1 and
        #    isinstance(dependencies[0], SoftwareDependencyList)):
        #     self.dependencies = dependencies[0]
        # else:
        self.dependencies = [SoftwareDependency(i) if isinstance(i, str)
                             else i for i in dependencies]

    def __getitem__(self, key):
        if isinstance(key, str):
            for item in self.dependencies:
                if (getattr(item, 'name', None) == key or
                   getattr(item, 'category', None) == key):
                    return item
            raise KeyError(key)
        else:
            return self.dependencies[key]

    def __len__(self):
        return len(self.dependencies)

    def __contains__(self, key):
        if isinstance(key, str):
            for item in self.dependencies:
                if (getattr(item, 'name', None) == key or
                   getattr(item, 'category', None) == key):
                    return True
        return False

    def __repr__(self):
        cls_name = self.__class__.__name__
        items_str = ', '.join([i.__repr__() for i in self.dependencies])
        return cls_name + '[' + items_str + ']'

    def flatten(self, items=None, level=1):
        """Return a flattened list of software dependency objects.

        The flattened list includes SoftwareDependency and
        SoftwareDependencyList objects.

        Returns
        -------
        flattened_list : List[Tuple[int, Union[:obj:`.SoftwareDependency`, \
            :obj:`.SoftwareDependencyList`]]]
            A flattened list of tuples with the level (int) and software
            dependencies or software dependency lists.
        """
        # Recursion check
        if level > 16:
            return None
        flattened_list = []

        # Use this list's dependencies list, if not items are specified
        items = self if items is None else items
        items = items.dependencies if hasattr(items, 'dependencies') else items

        # Wrap in a list
        items = [items] if not isinstance(items, list) else items

        for item in items:
            # Only return SoftwareDependency or SoftwareDependencyList objects
            if isinstance(item, SoftwareDependency):
                flattened_list.append((level, item))
            elif isinstance(item, SoftwareDependencyList):
                flattened_list.append((level, item))
                flattened_list += self.flatten(items=item, level=level + 1)

        return flattened_list

    def keys(self):
        """Name or category of sub-dependencies."""
        return [i.category if hasattr(i, 'category')
                else i.name
                for i in self.dependencies]

    @property
    def available(self):
        return False


class Any(SoftwareDependencyList):
    """A list for external programs and packages in why any of them may
    be present."""

    @property
    def available(self):
        return any(i.available is True for i in self.dependencies)


class All(SoftwareDependencyList):
    """A list for external programs and packages in why all of them
    should be present."""

    @property
    def available(self):
        return all(i.available is True for i in self.dependencies)


class Optional(SoftwareDependencyList):
    """A list for external programs and packages in why none of them are
    required to be present."""

    @property
    def available(self):
        return True
