"""
Classes for different kinds of paths.
"""
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

    def __new__(cls, project_root, subpath=None, *args, **kwargs):
        # Create the mixclass, if needed, this is the class with either
        # PosixPath or WindowsPath mixed in with SourcePath
        if cls.__mixclass__ is None:
            flavor_cls = WindowsPath if os.name == 'nt' else PosixPath

            class MixClass(flavor_cls, SourcePath):
                pass

            cls.__mixclass__ = MixClass

        obj = pathlib.Path.__new__(cls.__mixclass__,
                                   project_root,
                                   subpath or '',
                                   *args, **kwargs)
        obj.project_root = (cls.__mixclass__(project_root)
                            if project_root is not None else None)
        obj.subpath = cls.__mixclass__(subpath) if subpath is not None else None
        return obj


class TargetPath(object):
    """A path for a file in a target directory that keeps track of the
    target_root, target and subpath.
    """
    target_root = None
    target = None
    subpath = None
    __mixclass__ = None

    def __new__(cls, target_root, target=None, subpath=None, *args, **kwargs):
        # Create the mixclass, if needed, this is the class with either
        # PosixPath or WindowsPath mixed in with TargetPath
        if cls.__mixclass__ is None:
            flavor_cls = WindowsPath if os.name == 'nt' else PosixPath

            class MixClass(flavor_cls, TargetPath):
                pass
            cls.__mixclass__ = MixClass

        if isinstance(target, str):
            target = target.strip('.')  # '.html' -> 'html'

        obj = pathlib.Path.__new__(cls.__mixclass__,
                                   target_root,
                                   target or '',
                                   subpath or '',
                                   *args, **kwargs)
        obj.target_root = cls.__mixclass__(target_root)
        obj.target = cls.__mixclass__(target) if target is not None else None
        obj.subpath = cls.__mixclass__(subpath) if subpath is not None else None

        return obj

    def get_url(self, context=None):
        context = context if isinstance(context, dict) else dict()
        url_str = context.get('base_url', '/{target}/{subpath}')
        url = url_str.format(target_root=self.target_root or '',
                             target=self.target or '',
                             subpath=self.subpath or '')

        # Cleanup the url by  and double slashes
        url = url.rstrip('/')  # stripping leading slashes
        url = re_dbl_slash.sub('/', url)  # strip dble leading slash

        return url
