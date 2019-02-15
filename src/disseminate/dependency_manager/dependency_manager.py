"""
A manager for dependencies.
"""
import pathlib
import os
from collections import namedtuple
import urllib.parse
import logging

import regex

from ..tags import Tag
from ..convert import convert
from ..attributes import (parse_attributes, get_attribute_value, set_attribute,
                          kwargs_attributes)
from ..paths import SourcePath, TargetPath
from .. import settings


class MissingDependency(Exception):
    """A dependency was not found."""
    pass


class FileDependency(namedtuple('FileDependency', ['dep_filepath',
                                                   'dest_filepath',
                                                   ])):
    """A dependency on a file.

    Attributes
    ----------
    dep_filepath : :obj:`disseminate.SourcePath`
        The path of the existing dependency file.
        ex: 'src/media/images/fig1.png'
    dest_filepath: :obj:`disseminate.TargetPath`
        The destination path for the dependency file to be placed in a
        document's target directory.
        ex: 'html/media/images/fig1.png
    """

    def get_url(self, context=None):
        """Produce the url for this dependency."""
        return self.dest_filepath.get_url(context)


class DependencyManager(object):
    """Manage dependencies.

    Keep track, convert and manage dependencies (such as files) needed to
    construct a target.

    .. note: The dependency manager doesn't keep a reference to a context since
             many documents and subdocuments in a project use the same
             dependency manager, and each document has its own context.

    Parameters
    ----------
    project_root : :obj:`disseminate.SourcePath`
        The root directory for the document (source markup) files. (i.e. the
        input directory)
        ex: 'src/'
    target_root : :obj:`disseminate.TargetPath`
        The target directory for the output documents (i.e. the output
        directory). The final output directory also depends on the
    create_dir : bool, optional
        If True, the dependency manager will create directories in the target
        that do not exist.

    Attributes
    ----------
    dependencies : dict of sets
        A dict of sets of dependencies managed by this dependency manager.
        The keys are the target names (ex: '.html') and the values are
        a set of FileDependency tuples.
    """

    project_root = None
    target_root = None
    create_dirs = None
    dependencies = None

    # TODO: make the parameters root_context, like the label manager
    def __init__(self, project_root, target_root,
                 create_dirs=settings.create_dirs):
        assert isinstance(project_root, SourcePath)
        assert isinstance(target_root, TargetPath)

        self.project_root = project_root
        self.target_root = target_root
        self.create_dirs = create_dirs
        self.dependencies = dict()

    # TODO: Refactor to remove cache_path.
    @property
    def cache_path(self):
        cache_path = SourcePath(project_root=self.target_root,
                                subpath=settings.cache_path)
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    def add_dependency(self, dep_filepath, target, context, attributes=None):
        """Add a file dependency to the target directory of a rendered
        document.

        Parameters
        ----------
        dep_filepath : :obj:`pathlib.Path` or :obj:`disseminate.SourcePath`
            A subpath to the dependency file. An absolute path cannot work
            since the subpath cannot be determined. (If an absolute path was
            used, the whole directory tree leading up to the dependency file
            would be created in the target directory)
        target : str
            The extension for the target to add this dependency for. ex: .html,
            .tex
        context : :obj:`disseminate.document.DocumentContext`
            The context for a document to render.

        Returns
        -------
        dependency : set of :obj:`disseminate.dependency_manager.FileDependency`
            The created FileDependency object(s).
            A set is returned, rather than a single object, because the file
            may contain other dependencies that must be added. Examples include
            html files that reference local css files.

        Raises
        ------
        FileNotFoundError
            Raised if the file identified by path could not be found in the
            paths given by context.
        """
        assert context.is_valid('src_filepath', 'paths')
        src_filepath = context['src_filepath']

        # Convert the dep_filepath, if needed
        if not isinstance(dep_filepath, SourcePath):
            dep_filepath = pathlib.Path(dep_filepath)
            dep_filepath = SourcePath(project_root=dep_filepath.parent,
                                      subpath=dep_filepath.name)

        deps = set()

        # Workup the dep_filepath
        path = None
        if dep_filepath.is_file():
            # Source files can be used, since they have already parsed the
            # subpath of the file. However, the file must exist.
            path = dep_filepath
        else:
            # Otherwise, try to find the dep_filepath by searching the paths
            # in the context
            subpath = pathlib.Path(dep_filepath)
            basepaths = context['paths']
            path_func = lambda b, s: SourcePath(project_root=b, subpath=s)
            path = self._search_file(path_func=path_func, basepaths=basepaths,
                                     subpaths=subpath)

        # Raise an exception if the file was not found
        if path is None:
            msg = "The file '{}' was not found.".format(str(dep_filepath))
            raise FileNotFoundError(msg)

        # See if a dest_filepath already exists
        tracked_deps = settings.tracked_deps[target]
        path_func = lambda b, s: TargetPath(target_root=self.target_root,
                                            target=target,
                                            subpath=path.subpath.with_suffix(s))
        dest_filepath = self._search_file(path_func=path_func,
                                          basepaths='',
                                          subpaths=tracked_deps)

        # If a valid dest_filepath was not found, the file needs to be copied
        # or converted
        if dest_filepath is None:
            dest_filepath = self._add_file(dep_filepath=path, target=target,
                                           attributes=attributes)

        # See if a valid dest_filepath has been found or created. If so, create
        # a dependency.
        if dest_filepath is not None:
            dep = FileDependency(dep_filepath=path,
                                 dest_filepath=dest_filepath)

            # Add the dependency to the returned deps set
            deps.add(dep)

            # See if the added file corresponds to an extension that can be
            # scraped. This may add additional dependencies

            # dep_ext = path.suffix.strip('.')
            # scrape_method = getattr(self, 'scrape_' + dep_ext, None)
            # if scrape_method is not None:
            #     deps.add(scrape_method(path, target=target, context=context))

            # Add the dependendencies to the manager's dependencies dict
            s = self.dependencies.setdefault(src_filepath, set())
            s |= deps

        return deps

    def _search_file(self, path_func, basepaths, subpaths):
        """Search for files given a path function and a combination of
        base paths and subpaths. The first valid file is returned

        Parameters
        ----------
        path_func : function
            A function that takes (basepath, subpath) arguments to create a
            new path. This path will be checked to see if the file exists.
        basepaths : list of :obj:`pathlib.Path` or :obj:`pathlib.Path` or str
            One or more starting parts of a path.
        subpaths : list of :obj:`pathlib.Path` or :obj:`pathlib.Path` or str
            One or more ending parts of a path.

        Returns
        -------
        path : :obj:`pathlib.Path` or None
            A path pointing to a valid file.
            None is returned if no valid file is found.
        """
        # Convert to lists, if these are strings or path objects.
        basepaths = ([basepaths] if not isinstance(basepaths, list)
                     else basepaths)
        subpaths = [subpaths] if not isinstance(subpaths, list) else subpaths

        # Iterate over the combinations of basepaths and subpaths
        for basepath in basepaths:
            for subpath in subpaths:
                # Get the path from the path_func and see if it's a file
                path = path_func(basepath, subpath)
                if path.is_file():
                    return path

        # No valid filepath was found.
        return None

    def _add_file(self, dep_filepath, target, attributes=None):
        """Add the src_filepath dependency to target_filepath.

        This function checks to see if the document target is compatible with
        the file format given in src_filepath. If it is the file will be copied
        (hard linked) to the target_root. If it isn't the function will try to
        convert it to a file type that is compatible with target. In either
        case, the subpath of the src_filepath will be recreated in the target
        directory.

        Parameters
        ----------
        dep_filepath : :obj:`disseminate.SourcePath`
            The path of the dependency file.
        target : str
            The type of document target for which this dependency is created.

        Returns
        -------
        dest_filepath : str
            The destination filepath (:obj:`disseminate.TargetPath`) for the
            copied file
        """
        target_root = self.target_root
        src_suffix = dep_filepath.suffix

        # See if the extension of the src_filepath is compatible with an
        # extension that can be used with this target. If so, add it directly.
        if src_suffix in settings.tracked_deps[target]:
            # The file can be used directly with the given source_filepath
            # extension. Simply copy it over.
            dest_filepath = TargetPath(target_root=target_root,
                                       target=target,
                                       subpath=dep_filepath.subpath)

            self._copy_file(dep_filepath=dep_filepath,
                            dest_filepath=dest_filepath)

        else:
            # The file cannot be used directly for the given target. See if it
            # can be converted.
            dest_filepath = self._convert_file(dep_filepath=dep_filepath,
                                               target=target,
                                               attributes=attributes)

        return dest_filepath

    def _copy_file(self, dep_filepath, dest_filepath):
        """Copy or link a file for the given source_filepath to the given
        target_filepath.

        Parameters
        ----------
        dep_filepath : :obj:`disseminate.SourcePath`
            The path of the dependency file, either in the project_root or in the
            module.
        dest_filepath : :obj:`disseminate.TargetPath`
            The path of the file to copy/link to.

        Returns
        -------
        dest_filepath : str
            The target filepath (:obj:`disseminate.TargetPath`) for the copied
            file
        """
        assert isinstance(dep_filepath, SourcePath)
        assert isinstance(dest_filepath, TargetPath)

        # Do nothing if the target file is already copied
        if (dest_filepath.is_file() and
            (dest_filepath.stat().st_mtime >=
             dep_filepath.stat().st_mtime)):
            return None

        # In this case, the target file needs to be copied.
        # First, create the target directory
        if self.create_dirs:
            target_parent = dest_filepath.parent
            target_parent.mkdir(parents=True, exist_ok=True)

        # The link or copy the file
        logging.debug("Linking file '{}'".format(str(dep_filepath)))
        try:
            os.link(str(dep_filepath), str(dest_filepath))
        except FileExistsError:
            # If the file exists, the link will fail. Remove it first.
            os.remove(str(dest_filepath))
            os.link(str(dep_filepath), str(dest_filepath))

    def _convert_file(self, dep_filepath, target, attributes=None):
        target_root = self.target_root

        # Get a listing a valid extensions to convert the source_filepath to
        # for the given target
        convert_targets = settings.tracked_deps[target]

        # Format the attributes to a kwargs dict for this target,
        # suitable for the convert function
        if attributes:
            kwargs = kwargs_attributes(attrs=attributes, target=target)
        else:
            kwargs = dict()

        # Convert the file
        base_subpath = dep_filepath.subpath.with_suffix('')  # strip ext
        dest_basefilepath = TargetPath(target_root=target_root,
                                       target=target,
                                       subpath=base_subpath)
        new_path = convert(src_filepath=dep_filepath,
                           target_basefilepath=dest_basefilepath,
                           targets=convert_targets, **kwargs)
        return new_path

    #: regex for processing <link> tags in html headers
    _re_html_link = regex.compile(r'\<[\n\s]*link[\n\s]+'
                                  r'(?P<contents>[^\>]+)'
                                  r'\>')

    def scrape_html(self, html, target, context):
        """Scrape an html string for dependencies, like css and js files.

        .. note:: This function rewrites <link ...> tags to point to
                  dependency destination files.

        Parameters
        ----------
        html : str or :obj:`pathlib.Path`
            Either a path to an html file or a string in html format.
        target : str
            The type of document target for which this dependency is created.
        context : :obj:`disseminate.document.DocumentContext`
            The context for a document to render.

        Returns
        -------
        html : string
            The processed html string.

        Raises
        ------
        MissingDependency
            Raised when a file was not found.
        """
        assert context.is_valid('paths')

        def repl_html(m):
            # Parse the attributes of the link tag
            contents = m.groupdict()['contents']

            # Convert the attributes to an attrs tuple
            attrs = parse_attributes(contents)

            # Get the value of the 'href' attribute
            href = get_attribute_value(attrs=attrs, attribute_name='href')

            # Check to see if a 'href' attribute is present and that it doesn't
            # point to a url--urls aren't file dependencies. If so, skip this
            # link.
            if href is None or urllib.parse.urlparse(href).scheme != '':
                return m.group()

            # Get the filepath. The href may have a leading '/', and this should
            # be stripped
            path = href if not href.startswith('/') else href[1:]

            # Now see if it can be found and added. This will only add files
            # that are in settings.tracked_deps.
            deps = self.add_dependency(dep_filepath=path, target=target,
                                       context=context)
            dep = deps.pop()

            # Recreate the <link ...> tag
            url = dep.dest_filepath.get_url(context)
            attrs = set_attribute(attrs=attrs, attribute=('href', url))
            tag = Tag(name='link', content='', context=context,
                      attributes=attrs)
            return tag.html

        # Find link tags and parse their attributes
        return self._scrape_file(string=html, regexpr=self._re_html_link,
                                 repl=repl_html, context=context)

    #: regex for processing @import tags in css
    _re_css_import = regex.compile(r'@import\s*'
                                   r'[^"\']*'
                                   r'(["\'])'
                                   r'(?P<link>[^"\']+)'
                                   r'(\1)')

    def scrape_css(self, css, target, context):
        """Scrape a css string for dependencies, like css files.

        .. note:: This function rewrites @import tags to point to
                  dependency destination files.

        Parameters
        ----------
        css : str or :obj:`pathlib.Path`
            Either a path to a css file or a string in css format.
        target : str
            The type of document target for which this dependency is created.
        context : :obj:`disseminate.document.DocumentContext`
            The context for a document to render.

        Returns
        -------
        css : string
            The processed css string.

        Raises
        ------
        MissingDependency
            Raised when a file was not found.
        """
        assert context.is_valid('paths')

        # Find import commands
        def repl_css(m):
            # Parse the attributes of the link tag
            contents = m.groupdict()['link']

            # See if it's a url. If so, don't add it as a file dependency.
            parsed = urllib.parse.urlparse(contents)
            if parsed.scheme != '':
               return m.group()

            # Get the path of the file, a strip the leading '/' if present.
            path = (parsed.path if not parsed.path.startswith('/')
                    else parsed.path[1:])

            # Now see if it can be found and added. This will only add files
            # that are in settings.tracked_deps.
            deps = self.add_dependency(dep_filepath=path, target=target,
                                       context=context)
            dep = deps.pop()

            url = dep.dest_filepath.get_url(context)

            return '@import "{}"'.format(url)

        return self._scrape_file(string=css, regexpr=self._re_css_import,
                                 repl=repl_css, context=context)

    def _scrape_file(self, string, regexpr, repl, context):
        """Parse a filename specified by string, or the string itself, for
        matches of the given regex.

        Parameters
        ----------
        string : str or :obj:`pathlib.Path`
            Either a path to a text file or a string to parse.
        regexpr : generator of :obj:`Match`
            A generator of regex match objects.
        repl : function
            The match replacing function
        """
        # Load the string either as a file with a filename or the string itself.
        if isinstance(string, pathlib.Path):
            # It's a path object. Use it directly
            parse_str = string.read_text()
        else:
            # It's a filepath. Find the file and load its text.
            basepaths = context['paths']
            subpath = string.split('\n', 1)[0]

            path_func = lambda b, s: SourcePath(project_root=b, subpath=s)
            path = self._search_file(path_func=path_func, basepaths=basepaths,
                                     subpaths=subpath)

            # If it's a valid file, 'path' is not None. If it's not a valid
            # file, try parsing the string itself.
            parse_str = path.read_text() if path is not None else string

        return regexpr.sub(repl, parse_str)

    def reset(self, src_filepath=None):
        """Reset the dependencies tracked by the DependencyManager.

        Parameters
        ----------
        src_filepath : str or None
            If specified, remove all dependencies for the given document
            src_filepath.
            If not specified (None), all dependencies are removed.
        """
        if src_filepath in self.dependencies:
            del self.dependencies[src_filepath]
        else:
            self.dependencies.clear()
