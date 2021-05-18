"""
Checkers for python packages.
"""
from .checker import Checker
from .utils import name_and_version
from .types import SoftwareDependency, SoftwareDependencyList
from ..software_dependencies import python_deps


class PythonChecker(Checker):
    """Checker for python dependencies.

    Attributes
    ----------
    freeze : Optional[Tuple[str]]
        If pip is available, this is populated with a tuple of strings for
        installed packages.
    """

    freeze = None

    def __init__(self, python_deps=python_deps):
        super().__init__('python', *python_deps.dependencies)

        # Setup pip freeze, if available
        try:
            # This is the correct location for pip > 10.0
            from pip._internal.operations import freeze
        except ImportError:
            try:
                from pip.operations import freeze
            except ImportError:
                freeze = None

        # Retrieve the the freeze list of strings, if available
        self.freeze = (tuple(i.lower() for i in freeze.freeze())
                       if freeze is not None else None)

    def check_packages_pip(self, packages=None):
        """Check the availability of specific python packages in pip.

        Parameters
        ----------
        listing : Union[List[str], Tuple[str]]
            Packages names with optional version specifier.
        """
        # if pip freeze isn't available, return None
        if self.freeze is None:
            return None

        # Get the packages
        if packages is not None:
            pass
        elif 'packages' in self:
            packages = self['packages']
        else:
            return None

        if isinstance(packages, SoftwareDependency):
            # Convert the listings to tuples of name, operator, version.
            # ex: 'python>=3.1' becomes 'python',
            #     <built-in function ge>, (3, 1)
            rv = name_and_version(packages.name)

            if rv is None:
                # If the name a version could not be parsed, return None and
                # do nothing more
                return None

            # Parse the package name, comparison operator (op) and the version
            # tuple
            name, op, ver = rv
            name = name.lower()

            # See if the package name is available in the freeze tuple
            matching_packages = [i for i in self.freeze if i.startswith(name)]

            # If there are no matching packages, return None and do nothing
            # more
            if len(matching_packages) == 0:
                return None

            # In this case, there is an installed package. See if the version
            # matches
            installed_package = matching_packages[0]
            rv = name_and_version(installed_package)

            if rv is None:
                # The installed package could not be parsed. Return None and
                # do nothing more
                return None

            installed_name, installed_op, installed_ver = rv

            # check the version
            if op is None and ver is None:
                # In this case, we don't care about the version--just that it's
                # installed. It is, so mark it as installed
                packages.available = True
            elif installed_ver is not None and op(installed_ver, ver):
                # Otherwise check the version number
                packages.available = True

        elif isinstance(packages, SoftwareDependencyList):
            # If the packages is a SoftwareDependencyList, process each package
            # individually
            for package in packages.dependencies:
                self.check_packages_pip(package)
