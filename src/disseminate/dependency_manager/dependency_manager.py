"""
A manager for dependencies.
"""
import os
from collections import namedtuple

import regex

from ..convert import convert
from ..attributes import re_attrs
from ..utils.file import mkdir_p
from .. import settings

# Get the template path for the disseminate project
current_filepath = os.path.realpath(__file__)
current_path = os.path.split(current_filepath)[0]
template_path = os.path.join(current_path, '../templates')


class MissingDependency(Exception):
    """A dependency was not found."""
    pass


class FileDependency(namedtuple('FileDependency', ['media_path', 'path'])):
    """A dependency on a file.

    Attributes
    ----------
    media_path : str
        The path of the file relative to the media_root
        ex: 'images/fig1.png'
    path : str
        The actual (render) path of the existing file
        ex: 'src/media/images/fig1.png'
    """
    pass


class DependencyManager(object):
    """Manage dependencies.

    Keep track, convert and manage dependencies (such as files) needed to
    construct a target.

    Parameters
    ----------
    project_root : str
        The root directory for the document (source markup) files. (i.e. the
        input directory)
        ex: 'src/'
    target_root : str
        The target directory for the output documents (i.e. the output
        directory). The final output directory also depends on the
        segregate_targets option.
        ex: 'out/'
    seggregate_targets : bool, optional
        If True (default), the processed output documents for each target type
        will be place in its directory named for the target.
        ex: 'out/html'
    media_root : str, optional
        The project path in which media files are stored. The dependency
        media_path is relative to media_root, and the media_root path is
        relative to the project root.
        ex: 'media'

    Attributes
    ----------
    dependencies : set
        A set of dependencies managed by this dependency manager.
    """

    project_root = None
    target_root = None
    media_root = None
    dependencies = None

    #: regex for processing <link> tags in html headers
    _re_link = regex.compile(r'\<[\n\s]*link[\n\s]+'
                             r'(?P<contents>[^\>]+)'
                             r'\>')

    #: regex for processing html tag attributes
    _re_attrs = re_attrs

    def __init__(self, project_root, target_root,
                 segregate_targets=settings.segregate_targets,
                 media_root=media_root):
        self.project_root = project_root
        self.target_root = target_root
        self.segregate_targets = segregate_targets
        self.media_root = media_root
        self.dependencies = set()

    def target_path(self, target):
        """The final render path for the given target."""
        if self.segregate_targets:
            return os.path.join(self.target_root, target.strip('.'))
        else:
            return self.target_root

    def search_file(self, path):
        """Find a file for the given path.

        The file will be searched in the following order:
            - as a render path 'src/media/images/fig1.png'
            - relative to the project_root 'media/images/fig1.png'
            - in the disseminate module templates.

        Parameters
        ----------
        path : str
            The path of the file to be searched. This may either me a path
            relative to the project_root, a render path or a path in the
            disseminate module templates.

        Returns
        -------
        (media_path, render_path) or False
            If the file is found, a media_path and render_path is returned.
            If not, False is returned.
        """
        # Search as a render path
        if os.path.exists(path):
            media_path = os.path.relpath(path, self.project_root)
            return media_path, path

        # Search relative to the project_root
        path1 = os.path.join(self.project_root, path)  # generate render path
        if os.path.exists(path1):
            media_path = os.path.relpath(path1, self.project_root)
            return media_path, path1

        # Search in the module
        path2 = os.path.join(template_path, path)  # generate render path
        if os.path.exists(path2):
            media_path = os.path.relpath(path2, template_path)
            return media_path, path2

        return False

    def copy_file(self, target, media_path, path):
        """Copy or link a file for the given (render) path to the target's
        media path.

        Returns
        -------
        target_path :
            The string for the target path (render path) for the newly copied
            or linked file.
        """
        # Get the target path in a render path
        target_media_path = os.path.join(self.target_path(target), media_path)

        # Make sure the target's media_path exists
        mkdir_p(target_media_path)

        # copy the file at path to the target_path
        os.link(path, target_media_path)

        return target_media_path

    def add_file(self, targets, path, **kwargs):
        """Add a file dependency for the given path.

        The file will be converted to a suitable formant for the target, if
        needed.

        .. note:: Files should be added while generating the AST.

        Parameters
        ----------
        targets : list of str
            The targets for the dependency. ex: '.html' or '.tex'
        path : str
            The path of the file. The file will be searched using
            :meth:`DependencyManager.search_file`.
        kwargs : dict
            The kwargs to be used for the convert function, if the file needs
            to be converted.

        Returns
        -------
        True
            When the file was succesfully found and added.

        Raises
        ------
        MissingDependency
            Raised when a file was not found.
        """
        # Only go through targets that have tracked dependencies
        for target in [t for t in targets if t in settings.tracked_deps]:
            # Find the file
            paths = self.search_file(path)

            # Raise a MissingDependency if the file was not found.
            if paths is False:
                msg = "Could not find dependency file '{}'"
                raise MissingDependency(msg.format(path))

            # Get the extension for the file's path
            ext = os.path.splitext(path)[1]

            # See if the extension is compatible with an extension that can
            # be used with this target. If so, add it directly.
            if ext in settings.tracked_deps[target]:
                media_path, path = paths
                # Add the dependency
                dep = FileDependency(paths)
                self.dependencies.add(dep)

                # Link the file
                self.copy_file(target=target, media_path=media_path,
                               path=path)

            # If the file cannot be used directly, try converting it. This
            # will change its media_path, since the extension (and possibly the
            # filename) will change.
            else:
                # Get the suitable paths for the conversion. 'path' is the
                # location of the file (render path) and the target_basefilepath
                # is the path we want the final file to be created in (in
                # render path)
                media_path, path = paths

                if self.segregate_targets:
                    target_filepath = os.path.join(self.target_root,
                                                   target,
                                                   media_path)
                else:
                    target_filepath = os.path.join(self.target_root,
                                                   media_path)
                # Strip the extension to make the target_basefilepath
                target_basefilepath = os.path.splitext(target_filepath)[0]

                # The targets for the convert function are the allowed
                # extensions for this target.
                convert_targets = settings.tracked_deps[target]

                new_path = convert(src_filepath=path,
                                   target_basefilepath=target_basefilepath,
                                   targets=convert_targets, **kwargs)

                # The new_path is a render path for the newly generated file
                # We will need to get the media_path for this path.
                if new_path:
                    media_path = os.path.relpath(self.target_path(target),
                                                 new_path)

                    # add the dependency
                    dep = FileDependency(media_path=media_path, path=new_path)
