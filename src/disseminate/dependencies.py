"""
Classes and functions for managing dependencies like static files (.css) and
images.
"""
import os
import glob

import regex

from disseminate.attributes import re_attrs
from .utils.file import mkdir_p
from . import settings

# This variable is effectively hard coded since this path is the one used
# by the module templates
media_root = 'media'

class DependencyError(Exception):
    """An error was encountered in finding or parsing dependencies."""
    pass


class Dependencies(object):
    """Track and handle dependency files for each target type.

    Attributes
    ----------
    target_root : str
        The target directory for the output documents (i.e. the output
        directory). The final output directory also depends on the
        segregate_targets option.
        ex: 'out/'
    media_root : str
        The path to lookup and store media files. The dependencies paths are
        relative to media_root, and the media_root path is relative to the
        project root.
    dependencies : dict of sets
        - The key is the target type. ex: '.html' or '.tex'
        - The value is a dict of dependencies. The key is the path relative to
          the media_root. The value is the file in a render path (i.e. relative
          to the current directory or an absolute path).
          ex: {'.html':
                 {'css/default.css': '/var/www/css/default.css'}}
    """

    target_root = None
    media_root = None
    dependencies = None

    _re_link = regex.compile(r'\<[\n\s]*link[\n\s]+'
                             r'(?P<contents>[^\>]+)'
                             r'\>')
    _re_attrs = re_attrs

    def __init__(self, target_root=None,
                 segregate_targets=settings.segregate_targets,
                 media_root=media_root):
        self.target_root = target_root
        self.segregate_targets = segregate_targets
        self.media_root = media_root
        self.dependencies = dict()

    def add_html(self, html_string, path):
        """Add dependencies, like css and js files, from an html string.

        .. note:: This method populates the dependencies attribute.

        Parameters
        ----------
        html_string : str
            A string in HTML format to seek dependencies.
        path : str
            A path to start searching. The search will traverse from the bottom
            directory to the top, looking for the dependencies.

        Returns
        -------
        None
        """
        if self.dependencies is None:
            self.dependencies = dict()

        # allowed attributes
        allowed_attrs = {'stylesheet', }
        dependent_files = dict()  # key: relative path, value: render path

        # Find link tags and parse their attributes
        for m in self._re_link.finditer(html_string):
            # Parse the attributes of the link tag
            contents = m.groupdict()['contents']

            # Match the attributes
            attrs = dict()
            for n in self._re_attrs.finditer(contents):
                d = n.groupdict()
                if isinstance(d['value'], str):
                    attrs[d['key']] = d['value'].strip('"').strip("'").strip()

            # Check to see if it's a valid file
            if (attrs.get('rel', None) in allowed_attrs and
               'href' in attrs and
               not attrs['href'].startswith('http')):

                # Get the file. It's the value of the 'href' attribute
                key = attrs['href']
                ext = os.path.splitext(key)[1]

                # Check to make sure it's one of the tracked types of
                # extensions for html
                if ext in settings.tracked_deps['.html']:
                    dependent_files[key] = None

        # Now try to find the dependent files and their render paths
        for key in dependent_files.keys():
            # The key can't start with a forward slash for os.path.join to work
            cleaned_path = key if not key.startswith('/') else key[1:]

            search_path = path

            while search_path != '' and search_path != "/":
                # See if the current search_path has a valid file
                test_path = os.path.join(search_path, cleaned_path)

                if os.path.isfile(test_path):
                    # match found! Add it if it exists. The key has to be a
                    # path relative to media root
                    dependent_files[key] = test_path
                    break

                # Move up a directory
                search_path = os.path.split(search_path)[0]

            # At this point, if the file wasn't found, raise an error
            if dependent_files[key] is None:
                msg = "Could not find dependency file '{}'"
                raise DependencyError(msg.format(key))
            # TODO: check to make sure the file doesn't exist from somewhere
            # else

            # get the path relative to the target_root
            # TODO: add url_root
            target_path = os.path.join("/", cleaned_path)

        d = self.dependencies.setdefault('.html', dict())
        d.update(dependent_files)
        return None

    def translate_files(self, target_root=None, segregate_targets=None):
        """Translate files to the target output directories.

        In most cases, the files will be linked if the files are already in a
        usable format. If the file isn't in a usable format for the target,
        a translator function

        Parameters
        ----------
        target_root : str
            The target directory for the output documents (i.e. the output
            directory). The final output directory also depends on the
            segregate_targets option.
            ex: 'out/'
        segregate_targets : bool
            If True, the processed output documents for each target type will be
            place in its directory named for the target.
            ex: 'out/html'

        Returns
        -------
        None
        """
        target_root = (target_root if target_root is not None else
                       self.target_root)
        segregate_targets = (segregate_targets if segregate_targets is not None
                             else self.segregate_targets)

        # Cycle through each target type
        for target, dep_dict in self.dependencies.items():
            # strip the leading period from the target extension.
            # '.html' -> 'html'
            target = target if not target.startswith('.') else target[1:]

            # cycle each dependency for this target
            for media_path, abs_path in dep_dict.items():
                # Strip leading '/'
                media_path = (media_path if not media_path.startswith('/') else
                              media_path[1:])

                # Construct the render path form the media_path
                if segregate_targets:
                    render_path = os.path.join(target_root, target, media_path)
                else:
                    render_path = os.path.join(target_root, media_path)

                # Create the directory for the render_path
                mkdir_p(render_path)

                # Translate the file
                dep_ext = os.path.splitext(render_path)[1]
                translator = settings.tracked_deps['.html'][dep_ext]

                if translator is None:
                    # And link if the target. Overwrite if neccessary
                    # TODO: implement overwrite
                    if not os.path.isfile(render_path):
                        os.link(abs_path, render_path)

    def clean(self, target_root=None, segregate_targets=None):
        """Removes unused dependencies and empty directories in the target
        media_root.

        Parameters
        ----------
        target_root : str
            The target directory for the output documents (i.e. the output
            directory). The final output directory also depends on the
            segregate_targets option.
            ex: 'out/'
        segregate_targets : bool
            If True, the processed output documents for each target type will be
            place in its directory named for the target.
            ex: 'out/html'

        Returns
        -------
        None
        """
        target_root = (target_root if target_root is not None else
                       self.target_root)
        segregate_targets = (segregate_targets if segregate_targets is not None
                             else self.segregate_targets)

        # Construct a set of managed files in render paths and find which files
        # are not managed by this dependencies object
        render_paths = set()
        for target, dep_dict in self.dependencies.items():
            # Strip the leading period from the target extention
            # ".html" -> "html"
            target_name = target.strip('.')

            # Construct the root media path into a render path
            media_root = (os.path.join(target_root, target_name)
                          if segregate_targets else
                          target_root)

            # Add all of the media files as render paths
            for media_path in dep_dict.keys():
                # Remove the leading '/' from media_path so that we can
                # join its path
                media_path = (media_path if not media_path.startswith('/')
                              else media_path[1:])

                render_paths.add(os.path.join(media_root, media_path))

            # Now find all the files and directories in the media path and see
            # which ones aren't managed by this dependencies object
            glob_paths = glob.glob(os.path.join(media_root, '**'),
                                  recursive=True)

            # Process files first, then directories, so that empty directories
            # can be removed after untracked files are removed.
            glob_files = [i for i in glob_paths if os.path.isfile(i)]
            glob_dirs = [i for i in glob_paths if os.path.isdir(i)]

            # Remove untracked files that suppose to be tracked (i.e. are in
            # the tracked_types list
            for file in glob_files:
                file_ext = os.path.splitext(file)[1]
                if (file not in render_paths and
                   file_ext in settings.tracked_deps[target]):

                    os.remove(file)

            # Remove empty dirs
            for dir in glob_dirs:
                if not os.listdir(dir):  # test if dir is empty
                    os.rmdir(dir)

