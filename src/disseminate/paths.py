"""
Classes for different kinds of paths.
"""
# TODO: Implement equivalence tests.

import pathlib
import os
import re


re_dbl_slash = re.compile(r'(?<!\:)//')  # match '//' but not '://'


# We need to derive the WindowsPath and PosixPath so that we can add
# entries into its __dict__.
class WindowsPath(pathlib.WindowsPath):
    pass


class PosixPath(pathlib.PosixPath):
    pass


class SourcePath(object):
    """A path for a file in the source directory that keeps track of the
    project_root and subpath.
    """
    project_root = None
    subpath = None
    __mixclass__ = None

    def __new__(cls, project_root=None, subpath=None):
        subpath = pathlib.Path(subpath or '')
        assert not subpath.is_absolute(), ("The subpath argument cannot be an "
                                           "absolute path")

        # Create the mixclass, if needed, this is the class with either
        # PosixPath or WindowsPath mixed in with SourcePath
        if cls.__mixclass__ is None:
            flavor_cls = WindowsPath if os.name == 'nt' else PosixPath

            class MixClass(flavor_cls, SourcePath):
                pass
            MixClass.__name__ = cls.__name__
            cls.__mixclass__ = MixClass

        obj = pathlib.Path.__new__(cls.__mixclass__,
                                   project_root or '',
                                   subpath or '')
        obj.project_root = cls.__mixclass__(project_root or '', '')
        obj.subpath = cls.__mixclass__('', subpath or '')
        return obj

    def __copy__(self):
        return SourcePath(project_root=self.project_root, subpath=self.subpath)

    def __deepcopy__(self, memo):
        return SourcePath(project_root=self.project_root, subpath=self.subpath)


class TargetPath(object):
    """A path for a file in a target directory that keeps track of the
    target_root, target and subpath.
    """
    target_root = None
    target = None
    subpath = None
    __mixclass__ = None

    def __new__(cls, target_root=None, target=None, subpath=None):
        subpath = pathlib.Path(subpath or '')
        assert not subpath.is_absolute(), ("The subpath argument cannot be an "
                                           "absolute path")

        # Create the mixclass, if needed, this is the class with either
        # PosixPath or WindowsPath mixed in with TargetPath
        if cls.__mixclass__ is None:
            flavor_cls = WindowsPath if os.name == 'nt' else PosixPath

            class MixClass(flavor_cls, TargetPath):
                pass
            MixClass.__name__ = cls.__name__
            cls.__mixclass__ = MixClass

        if isinstance(target, str):
            target = target.strip('.')  # '.html' -> 'html'

        obj = pathlib.Path.__new__(cls.__mixclass__,
                                   target_root or '',
                                   target or '',
                                   subpath or '')
        obj.target_root = cls.__mixclass__(target_root or '', '', '')
        obj.target = cls.__mixclass__('', target or '', '')
        obj.subpath = cls.__mixclass__('', '', subpath or '')
        return obj

    def __copy__(self):
        return TargetPath(target_root=self.target_root, target=self.target,
                          subpath=self.subpath)

    def __deepcopy__(self, memo):
        return TargetPath(target_root=self.target_root, target=self.target,
                          subpath=self.subpath)

    def get_url(self, context=None):
        """Construct the url for the path."""
        url = None

        # See if a relative url is requested and get that if it is
        if context is not None and context.get('relative_links', False):
            url = self._get_relative_url(context)

        # If a relative url could not be produced or one was not wanted, get
        # an absolute url.
        if url is None:
            url = self._get_absolute_url(context)

        # Cleanup the url by  and double slashes
        url = url.rstrip('/')  # stripping leading slashes
        url = re_dbl_slash.sub('/', url)  # strip dble leading slash

        return url

    def _get_relative_url(self, context):
        """Construct the relative url for the path."""
        document = context.document if hasattr(context, 'document') else None
        if document is None:
            return None

        # Get the target_filepath. Prepend a '.' if needed. ex: '.html'
        target = str(self.target)
        target = '.' + target if not target.startswith('.') else target

        # Get the target_filepath and target_path
        target_filepath = document.target_filepath(target)
        target_path = target_filepath.parent

        # Get the relative path
        relpath = os.path.relpath(self, target_path)

        # Construct a relative url relative to the target_path
        return str(relpath)

    def _get_absolute_url(self, context):
        """Construct the absolute url for the path."""
        # Get the parts of paths that will be used
        target_root = str(self.target_root).strip('.')
        target = str(self.target).strip('.')
        subpath = str(self.subpath).strip('.')

        url_str = (context['base_url'] if isinstance(context, dict) and
                   'base_url' in context else '/{target}/{subpath}')

        return url_str.format(target_root=target_root, target=target,
                              subpath=subpath)
