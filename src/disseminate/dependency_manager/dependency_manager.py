"""
A manager for dependencies.
"""
import os
from collections import namedtuple
import urllib.parse

import regex

from ..convert import convert
from ..attributes import re_attrs
from ..utils.file import mkdir_p
from .. import settings

# Get the template path for the disseminate project
current_filepath = os.path.realpath(__file__)
current_path = os.path.split(current_filepath)[0]
template_path = os.path.realpath(os.path.join(current_path, '../templates'))


#: regex for processing <link> tags in html headers
_re_link = regex.compile(r'\<[\n\s]*link[\n\s]+'
                         r'(?P<contents>[^\>]+)'
                         r'\>')

#: regex for processing html tag attributes
_re_attrs = re_attrs


class MissingDependency(Exception):
    """A dependency was not found."""
    pass


class FileDependency(namedtuple('FileDependency', ['src_filepath',
                                                   'target_filepath',
                                                   'dep_filepath',
                                                   'document_src_filepath',
                                                   ])):
    """A dependency on a file.

    Attributes
    ----------
    src_filepath : str
        The actual (render) path of the existing dependency file
        ex: 'src/media/images/fig1.png'
    target_filepath: str
        The actual (render) path for the existing dependency file for the
        target.
        ex: 'html/media/images/fig1.png
    dep_filepath : str
        The path of the file relative to the target_path
        ex: 'media/images/fig1.png'
    document_src_filepath : str or None
        The src_filepath (render path) of the document source markup file that
        owns the dependency.
        ex: 'src/chapter2/introduction.dm'
    """
    @property
    def url(self):
        """Produce the url for this dependency."""
        return settings.dep_root_url + self.dep_filepath


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

    Attributes
    ----------
    dependencies : dict of sets
        A dict of sets of dependencies managed by this dependency manager.
        The keys are the target names (ex: '.html') and the values are
        a set of FileDependency tuples.
    """

    project_root = None
    target_root = None
    dependencies = None

    def __init__(self, project_root, target_root,
                 segregate_targets=settings.segregate_targets):
        self.project_root = project_root
        self.target_root = target_root
        self.segregate_targets = segregate_targets
        self.dependencies = dict()

    def target_path(self, target):
        """The final render path for the given target."""
        if self.segregate_targets:
            return os.path.join(self.target_root, target.strip('.'))
        else:
            return self.target_root

    def cache_path(self):
        """Return the render path for the cache directory."""
        return os.path.join(self.target_root, settings.cache_dir)

    def get_dependency(self, target, src_filepath):
        """Return the FileDependency for a given target and src_filepath."""
        # Get the render_path for the src_filepath
        _, render_path = self.search_file(src_filepath)

        # Find the matching render_path
        dependencies = filter(lambda x: x.src_filepath == render_path,
                              self.dependencies[target])

        # Get the dependency's dep_path, if a match was found
        try:
            dependency = next(dependencies)
            return dependency
        except StopIteration:
            msg = "Could not find dependency file '{}'"
            raise MissingDependency(msg.format(src_filepath))

    def search_file(self, path, raise_error=True):
        """Find a file for the given path.

        The file will be searched in the following order:
            - as a render path 'src/media/images/fig1.png'
            - relative to the project_root 'media/images/fig1.png'
            - in the cache_dir
            - in the disseminate module templates.

        Parameters
        ----------
        path : str
            The path of the file to be searched. This may either me a path
            relative to the project_root, a render path or a path in the
            disseminate module templates.
        raise_error : bool, optional
            If True (default), a MissingDependency exception is raised if the
            file couldn't be found.

        Returns
        -------
        (dep_path, render_path) or False
            If the file is found, a dep_path and render_path is returned.
            If not, False is returned.

        Raises
        ------
        MissingDependency
            Raised when a file was not found (and raise_error is True).
        """
        if isinstance(path, str):
            # Search as a render path
            if os.path.exists(path):
                dep_path = os.path.relpath(path, self.project_root)
                return dep_path, path

            # Search relative to the project_root
            path1 = os.path.join(self.project_root, path)  # generate render path
            if os.path.exists(path1):
                dep_path = os.path.relpath(path1, self.project_root)
                return dep_path, path1

            # Search the cache_dir
            path2 = os.path.join(self.cache_path(), path)
            if os.path.exists(path2):
                dep_path = os.path.relpath(path2, self.cache_path())
                return dep_path, path2

            # Search in the module
            path3 = os.path.join(template_path, path)  # generate render path
            if os.path.exists(path3):
                dep_path = os.path.relpath(path3, template_path)
                return dep_path, path3

        if raise_error:
            msg = "Could not find dependency file '{}'"
            raise MissingDependency(msg.format(path))
        return False

    def copy_file(self, target, src_filepath, dep_filepath):
        """Copy or link a file for the given (render) src_filepath to the
        target's directory (dep_filepath).

        Returns
        -------
        src_filepath : str
            The string for the src_filepath (a render path) for the original
            file.
        dep_path : str
            The string for the file to copy or link in the target_root.
        """
        # Get the target src_filepath in a render src_filepath
        target_filepath = os.path.join(self.target_path(target), dep_filepath)

        # Make sure the target's dep_filepath exists
        mkdir_p(target_filepath)

        # copy the file at src_filepath to the target_path
        try:
            os.link(src_filepath, target_filepath)
        except FileExistsError:
            os.remove(target_filepath)
            os.link(src_filepath, target_filepath)

        return target_filepath

    def add_file(self, targets, path, document_src_filepath=None, **kwargs):
        """Add a file dependency for the given path.

        The file will be converted to a suitable formant for the target, if
        needed.

        .. note:: Files are added when generating the target document. (i.e.
                  after the AST is created.)

        Parameters
        ----------
        targets : list of str
            The targets for the dependency. ex: '.html' or '.tex'
        path : str
            The path of the dependency file. The file will be searched using
            :meth:`DependencyManager.search_file`.
        document_src_filepath: : str, optional
            The src_filepath (render path) of the document source markup files
            that own the dependency.
        kwargs : dict
            The kwargs to be used for the convert function, if the file needs
            to be converted.

        Returns
        -------
        targets_added : list of str
            A list of targets for which the dependency was added.

        Raises
        ------
        MissingDependency
            Raised when a file was not found.
        """
        targets_added = []

        # Only go through targets that have tracked dependencies
        for target in [t for t in targets if t in settings.tracked_deps]:
            # Find the file
            dep_path, render_path = self.search_file(path, raise_error=True)

            # Get the extension for the file's path
            ext = os.path.splitext(path)[1]

            # See if the extension is compatible with an extension that can
            # be used with this target. If so, add it directly.
            if ext in settings.tracked_deps[target]:
                # Link the file
                target_path = self.copy_file(target=target,
                                             src_filepath=render_path,
                                             dep_filepath=dep_path)

                # Add the dependency
                doc_src_filepath = document_src_filepath
                dep = FileDependency(src_filepath=render_path,
                                     target_filepath=target_path,
                                     dep_filepath=dep_path,
                                     document_src_filepath=doc_src_filepath)
                self.dependencies.setdefault(target, set()).add(dep)

                # Add it to the targets_added returned
                targets_added.append(target)

            # If the file cannot be used directly, try converting it. This
            # will change its dep_filepath and target_filepath, since the
            # extension (and possibly the filename) will change.
            else:
                # Get the suitable paths for the conversion. 'path' is the
                # location of the file (render path) and the target_basefilepath
                # is the path we want the final file to be created in (in
                # render path)
                target_filepath = os.path.join(self.target_path(target),
                                               dep_path)

                # Strip the extension to make the target_basefilepath. The
                # directories must be created as well
                target_basefilepath = os.path.splitext(target_filepath)[0]
                mkdir_p(target_basefilepath)

                # The targets for the convert function are the allowed
                # extensions for this target.
                convert_targets = settings.tracked_deps[target]

                new_path = convert(src_filepath=render_path,
                                   target_basefilepath=target_basefilepath,
                                   targets=convert_targets, **kwargs)

                # The new_path is a render path for the newly generated file
                # We will need to get the dep_path for this path.
                if new_path:
                    dep_path = os.path.relpath(new_path,
                                               self.target_path(target))

                    # add the dependency
                    doc_src_filepath = document_src_filepath
                    dep = FileDependency(src_filepath=render_path,
                                         target_filepath=new_path,
                                         dep_filepath=dep_path,
                                         document_src_filepath=doc_src_filepath)
                    self.dependencies.setdefault(target, set()).add(dep)

                    # Add it to the targets_added returned
                    targets_added.append(target)

        return targets_added

    def reset(self, document_src_filepath=None):
        """Reset the dependencies tracked by the DependencyManager.

        Parameters
        ----------
        document_src_filepath : str or None
            If specified, remove all dependencies for the given src_filepath of
            a document markup source file for all targets.
            If not specified (None), all dependencies are removed.
        """
        if isinstance(document_src_filepath, str):
            # Go through all targets
            for deps in self.dependencies.values():
                # Find the dependencies that match the document_src_filepath
                search = (lambda x: x.document_src_filepath ==
                          document_src_filepath)
                deps_to_remove = set(filter(search, deps))

                # Remove dependencies
                deps.difference_update(deps_to_remove)

            # Remove targets with empty dependency sets
            keys = list(self.dependencies.keys())
            for key in keys:
                if len(self.dependencies[key]) == 0:
                    del self.dependencies[key]

            # TODO: optional remove the untracked files
        else:
            self.dependencies.clear()

    def add_html(self, html):
        """Add dependencies, like css and js files, from html.

        Parameters
        ----------
        html : str
            Either a path to an html file (a render path) or a string in html
            format.

        Returns
        -------
        None

        Raises
        ------
        MissingDependency
            Raised when a file was not found.
        """
        # Load the html string
        if os.path.exists(html.strip()):
            with open(html, 'r') as f:
                html_str = f.read()
        else:
            html_str = html

        # Find link tags and parse their attributes
        for m in _re_link.finditer(html_str):
            # Parse the attributes of the link tag
            contents = m.groupdict()['contents']

            # Match the attributes, and find files
            attrs = dict()
            for n in _re_attrs.finditer(contents):
                d = n.groupdict()
                if isinstance(d['value'], str):
                    attrs[d['key']] = d['value'].strip('"').strip("'").strip()

            # Check to see if a 'href' attribute is present and that it doesn't
            # point to a url. If so, skip this link
            if ('href' not in attrs or
                urllib.parse.urlparse(attrs['href']).scheme != ''):
                continue

            # Get the filepath. The href may have a leading '/', and this should
            # be stripped
            path = (attrs['href'] if not attrs['href'].startswith('/') else
                    attrs['href'][1:])

            # Now see if it can be found and added. This will only add files
            # that are in settings.tracked_deps.
            self.add_file(targets=['.html', ], path=path)
