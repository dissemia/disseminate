"""
The Checker base class for checking dependencies.
"""
import shutil

from .types import All, SoftwareDependency, SoftwareDependencyList
from ..utils.classes import all_subclasses
from .exceptions import MissingHandler


class Checker(All):
    """Check for installed dependencies.

    .. note::
        The check implements checker handlers for different categories of
        dependencies (``check_`` methods).

        For example, a dependencies listing with a category 'executables' will
        run the :meth:`check_executables` method and a listing with a category
        of 'packages' will run the :meth:`check_packages` method.
    """

    @classmethod
    def checker_subclasses(cls):
        """All subclasses checkers."""
        return all_subclasses(cls)

    @classmethod
    def find_executable(cls, executable):
        return shutil.which(executable)

    def check(self):
        # Find SoftwareDependencyList categories.
        categories = [i.category for i in self.dependencies
                      if isinstance(i, SoftwareDependencyList)]
        for category in categories:
            handler_name = 'check_' + category
            meth = getattr(self, handler_name, None)
            if meth is not None:
                meth()
            else:
                msg = "The checker '{}' is missing the handler '{}'."
                cls_name = self.__class__.__name__

                raise MissingHandler(msg.format(cls_name, handler_name))

        return self.available

    def check_executables(self, executables=None):
        """Check the availability of executables.

        Parameters
        ----------
        executables : Union[List[str], Tuple[str]]
            The list of executables to check for availability.
        """
        # Retrieve the listing of executables
        if executables is not None:
            pass
        elif 'executables' in self:
            executables = self['executables']
        else:
            return None

        # Iterate over the executables and see if they can be found.
        for e in executables:
            if isinstance(e, SoftwareDependency):
                # Skip if already processed, as 'which' (below) might be
                # expensive to process
                if e.available is not None:
                    continue

                # If it's a software dependency, see if it's available
                path = shutil.which(e.name)
                e.available = path is not None  # executable found
                e.path = path
            elif isinstance(e, SoftwareDependencyList):
                # If it's a software dependency list, check each of those items
                self.check_executables(e.dependencies)

    def check_packages(self, packages=None):
        """Check the availability of packages.

        Parameters
        ----------
        packages : Union[List[str], Tuple[str]]
            The list of packages to check for availability.
        """
        # Get a listing of 'check_packages' methods
        check_packages_meth_names = [meth for meth in dir(self)
                                     if meth.startswith('check_packages_')]

        # Execute the methods
        for meth_name in check_packages_meth_names:
            meth = getattr(self, meth_name)
            meth(packages)
