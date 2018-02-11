"""
A manager for dependencies.
"""
import os
from collections import namedtuple

import regex

from ..attributes import re_attrs
from .. import settings

# Get the template path for the disseminate project
current_filepath = os.path.realpath(__file__)
current_path = os.path.split(current_filepath)[0]
template_path = os.path.join(current_path, '../templates')


class FileDependency(namedtuple('FileDependency', ['path', 'media_path'])):
    """A dependency on a file.

    Attributes
    ----------
    path : str
        The actual (render) path of the existing file
        ex: 'src/media/images/fig1.png'
    media_path : str
        The path of the file relative to the media_root
        ex: 'images/fig1.png'
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

    def add_file(self, targets, path):
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

        Returns
        -------
        True
            When the file was succesfully found and added.
        """
        pass

