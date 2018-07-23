"""
Classes for different kinds of paths.
"""
import pathlib
import os


# We need to derive the WindowsPath and PosixPath so that we can add
# entries into its __dict__.
class WindowsPath(pathlib.WindowsPath):
    pass


class PosixPath(pathlib.PosixPath):
    pass


class SourcePath(pathlib.Path):
    """A path for a file in the source directory that keeps track of the
    project_root and subpath.
    """
    project_root = None
    subpath = None

    def __new__(cls, project_root, subpath, *args, **kwargs):
        cls = WindowsPath if os.name == 'nt' else PosixPath
        obj = pathlib.Path.__new__(cls, project_root, subpath,
                                   *args, **kwargs)
        obj.project_root = project_root
        obj.subpath = subpath
        return obj


class TargetPath(pathlib.Path):
    """A path for a file in a target directory that keeps track of the
    target_root, target and subpath.
    """
    target_root = None
    target = None
    subpath = None

    def __new__(cls, target_root, target, subpath, *args, **kwargs):
        target = target.strip('.')
        cls = WindowsPath if os.name == 'nt' else PosixPath
        obj = pathlib.Path.__new__(cls, target_root, target, subpath,
                                   *args, **kwargs)
        obj.target_root = target_root
        obj.target = target
        obj.subpath = subpath
        return obj
