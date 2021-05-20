"""
Classes for different kinds of paths.
"""
# TODO: Implement equivalence tests.

import pathlib
import os
import re
import weakref


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

    Parameters
    ----------
    project_root : Optional[str]
        The path for the project's root directory.
    subpath : Optional[str]
        The relative path within the project's root directory.
    """
    project_root = None
    subpath = None
    __mixclass__ = None

    def __new__(cls, project_root='', subpath=''):
        # A variety of objects, including strings, pathlib.Path object or other
        # objects can be passed to this method. It's simplest just to convert
        # them to a string before using them.
        project_root = str(project_root)
        subpath = str(subpath)

        subpath = pathlib.Path(subpath)
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

        obj = pathlib.Path.__new__(cls.__mixclass__, project_root, subpath)
        obj.project_root = cls.__mixclass__(project_root, '')
        obj.subpath = cls.__mixclass__('', subpath)
        return obj

    def __copy__(self):
        return SourcePath(project_root=self.project_root, subpath=self.subpath)

    def __deepcopy__(self, memo):
        return SourcePath(project_root=self.project_root, subpath=self.subpath)

    def use_name(self, name):
        """with_name(name) that returns a SourcePath.

        A new method name is used since the flavor_cls method takes precedence.

        Examples
        --------
        >>> p = SourcePath(project_root='/media', subpath='tests/fig1.png')
        >>> p.use_name('fig2.png')
        SourcePath('/media/tests/fig2.png')
        >>> p.use_name('fig2.png').subpath
        SourcePath('tests/fig2.png')
        """
        return SourcePath(project_root=self.project_root,
                          subpath=self.subpath.with_name(name))

    def use_suffix(self, suffix):
        """with_suffix(suffix) that returns a SourcePath.

        A new method name is used since the flavor_cls method takes
        precedence.

        Examples
        --------
        >>> p = SourcePath(project_root='/media', subpath='tests/fig1.png')
        >>> p.use_suffix('.pdf')
        SourcePath('/media/tests/fig1.pdf')
        >>> p.use_name('fig1.pdf').subpath
        SourcePath('tests/fig1.pdf')
        """
        return SourcePath(project_root=self.project_root,
                          subpath=self.subpath.with_suffix(suffix))

    def use_subpath(self, subpath):
        """Returns a SourcePath with the subpath replaced with the given string
        or path.

        Examples
        --------
        >>> p = SourcePath(project_root='/media', subpath='tests/fig1.png')
        >>> p.use_subpath('text.txt')
        SourcePath('/media/text.txt')
        >>> p.use_subpath('text.txt').subpath
        SourcePath('text.txt')
        """
        return SourcePath(project_root=self.project_root,
                          subpath=subpath)


class TargetPath(object):
    """A path for a file in a target directory that keeps track of the
    target_root, target and subpath.

    Parameters
    ----------
    target_root : Optional[str]
        The path for the root directory for rendered files.
    target : Optional[str]
        The sub-directory for the target type to render. ex: 'html' or 'tex'
    subpath : Optional[str]
        The relative path within the target sub-directory.
    """
    target_root = None
    target = None
    subpath = None
    __mixclass__ = None

    def __new__(cls, target_root='', target='', subpath=''):
        # A variety of objects, including strings, pathlib.Path object or other
        # objects can be passed to this method. It's simplest just to convert
        # them to a string before using them.
        target_root = str(target_root)
        target = str(target)
        subpath = str(subpath)

        subpath = pathlib.Path(subpath)
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

        obj = pathlib.Path.__new__(cls.__mixclass__, target_root, target,
                                   subpath)
        obj.target_root = cls.__mixclass__(target_root, '', '')
        obj.target = cls.__mixclass__('', target, '')
        obj.subpath = cls.__mixclass__('', '', subpath)
        return obj

    def __copy__(self):
        return TargetPath(target_root=self.target_root, target=self.target,
                          subpath=self.subpath)

    def __deepcopy__(self, memo):
        return TargetPath(target_root=self.target_root, target=self.target,
                          subpath=self.subpath)

    def get_url(self, context=None, target=None):
        """Construct the url for the path."""
        url = None

        # See if a relative url is requested and get that if it is
        if context is not None and context.get('relative_links', True):
            url = self._get_relative_url(context, target)

        # If a relative url could not be produced or one was not wanted, get
        # an absolute url.
        if url is None:
            url = self._get_absolute_url(context, target)

        # Cleanup the url by  and double slashes
        url = url.rstrip('/')  # stripping leading slashes
        url = re_dbl_slash.sub('/', url)  # strip dble leading slash

        return url

    def _get_relative_url(self, context, target=None):
        """Construct the relative url for the path."""
        # Get the target_filepath. Prepend a '.' if needed. ex: '.html'
        target = str(target or self.target)
        target = '.' + target if not target.startswith('.') else target

        # Get the target_filepath and target_path. This should be from the
        # document that owns the this context or
        document = context.get('document', None)

        # If one isn't found, try using the root document. This can happen
        # if a mock context is used to simulate a document, like the toc
        # from the EpubBuilder
        document = document or context.get('root_document', None)

        # Dereference the document, if it's a weakref
        document = (document() if isinstance(document, weakref.ref) else
                    document)

        if document is not None:
            target_filepath = document.target_filepath(target)
            target_path = target_filepath.parent
        else:
            # Give up
            return None

        # Get the relative path
        relpath = os.path.relpath(self, target_path)

        # Construct a relative url relative to the target_path
        return str(relpath)

    def _get_absolute_url(self, context, target=None):
        """Construct the absolute url for the path."""
        # Get the parts of paths that will be used
        target_root = str(self.target_root).strip('.')
        target = str(target or self.target).strip('.')
        subpath = str(self.subpath).strip('.')

        url_str = (context['base_url'] if isinstance(context, dict) and
                   'base_url' in context else '/{target}/{subpath}')

        return url_str.format(target_root=target_root, target=target,
                              subpath=subpath)

    def use_name(self, name):
        """with_name(name) that returns a TargetPath.

        A new method name is used since the flavor_cls method takes
        precedence.

        Examples
        --------
        >>> p = TargetPath(target_root='/media', subpath='tests/fig1.png')
        >>> p.use_name('fig2.png')
        TargetPath('/media/tests/fig2.png')
        >>> p.use_name('fig2.png').subpath
        TargetPath('tests/fig2.png')
        """
        return TargetPath(target_root=self.target_root,
                          target=self.target,
                          subpath=self.subpath.with_name(name))

    def use_suffix(self, suffix):
        """with_suffix(suffix) that returns a TargetPath.

        A new method name is used since the flavor_cls method takes
        precedence.

        Examples
        --------
        >>> p = TargetPath(target_root='/media', subpath='tests/fig1.png')
        >>> p.use_suffix('.pdf')
        TargetPath('/media/tests/fig1.pdf')
        >>> p.use_suffix('.pdf').subpath
        TargetPath('tests/fig1.pdf')
        """
        return TargetPath(target_root=self.target_root,
                          target=self.target,
                          subpath=self.subpath.with_suffix(suffix))

    def use_subpath(self, subpath):
        """Returns a TargetPath with the subpath replaced with the given string
        or path.

        Examples
        --------
        >>> p = TargetPath(target_root='/media', subpath='tests/fig1.png')
        >>> p.use_subpath('text.txt')
        TargetPath('/media/text.txt')
        >>> p.use_subpath('text.txt').subpath
        TargetPath('text.txt')
        """
        return TargetPath(target_root=self.target_root,
                          target=self.target,
                          subpath=subpath)
