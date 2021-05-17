"""Checkers for .tex targets."""

import subprocess

from .checker import Checker
from .types import SoftwareDependency, SoftwareDependencyList
from ..software_dependencies import pdf_deps
from ..utils.list import chunks


class PdfChecker(Checker):
    """Checker for pdf renderings from latex."""

    def __init__(self, pdf_deps=pdf_deps):
        """Initialize checker for pdf rendering dependencies."""
        super().__init__('pdf', *pdf_deps.dependencies)

    def check_classes(self, classes=None):
        """Check the availability of classes.

        Parameters
        ----------
        classes : Union[List[str], Tuple[str]]
            The list of packages to check for availability.
        """
        # Get a listing of 'check_classes' methods
        check_classes_meth_names = [meth for meth in dir(self)
                                    if meth.startswith('check_classes_')]

        # Execute the methods
        for meth_name in check_classes_meth_names:
            meth = getattr(self, meth_name)
            meth(classes)

    def check_kpsewhich(self, listing, ext):
        """Check the availability of latex packages using kpsewhich.

        Parameters
        ----------
        listing : Union[List[str], Tuple[str]]
            Base filenames for latex classes or packages to check.
            ex: 'article'
        ext : str
            The extension to search. ex: '.sty' or '.cls'
        """
        # Make sure that 'kpsewhich' is installed.
        if self.find_executable('kpsewhich') is None:
            return None

        # Evalulate the presence of packages by opening at most 5
        # processes at
        # a time
        for chunk in chunks(listing, 5):
            processes = []

            # Start the processes for kpsewhich
            for item in chunk:
                if isinstance(item, SoftwareDependency):
                    # construct the kpsewhich command
                    args = ('kpsewhich', item.name + ext)

                    # Run the subprocess
                    p = subprocess.Popen(args, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         bufsize=4096, )
                    processes.append((item, p))

                elif isinstance(item, SoftwareDependencyList):
                    self.check_kpsewhich(item.dependencies, ext=ext)

            # Wait for the processes to have terminated
            for item, process in processes:
                # Check that it was succesfully executed
                out, err = process.communicate()
                returncode = process.returncode

                # Assign the package dependency's availability
                item.available = (returncode == 0)  # succesfully found

    def check_packages_kpsewhich(self, packages=None):
        """Check available latex packages (.sty) using kpsewhich.

        Parameters
        ----------
        packages : Union[List[str], Tuple[str]]
                The list of packages to check for availability.
        """
        if packages is not None:
            pass
        elif 'packages' in self:
            packages = self['packages']
        else:
            return None
        self.check_kpsewhich(packages, '.sty')

    def check_fonts(self, fonts=None):
        """Check available of latex fonts (.tfm) using kpsewhich.

        Parameters
        ----------
        fonts : Union[List[str], Tuple[str]]
                The list of fonts to check for availability.
        """
        if fonts is not None:
            pass
        elif 'fonts' in self:
            fonts = self['fonts']
        else:
            return None
        self.check_kpsewhich(fonts, '.tfm')

    def check_classes_kpsewhich(self, classes=None):
        """Check available latex classes (.cls) using kpsewhich.

        Parameters
        ----------
        classes : Union[List[str], Tuple[str]]
            The list of classes to check for availability.
        """
        if classes is not None:
            pass
        elif 'classes' in self:
            classes = self['classes']
        else:
            return None
        self.check_kpsewhich(classes, '.cls')
