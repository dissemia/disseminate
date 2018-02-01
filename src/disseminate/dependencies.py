"""
Classes and functions for managing dependencies like static files (.css) and
images.
"""
import os

import regex

from .utils.file import mkdir_p
from . import settings

# This variable is effectively hard coded since this path is the one used
# by the module templates
media_root = 'media'

class DependencyError(Exception):
    """An error was encountered in finding or parsing dependencies."""
    pass


class Dependencies(object):
    """A class to keep track of the dependency files for each target type.

    Attributes
    ----------
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

    media_root = None
    dependencies = None

    _re_link = regex.compile(r'\<[\n\s]*link[\n\s]+'
                             r'(?P<contents>[^\>]+)'
                             r'\>')
    _re_attrs = regex.compile(r'((?P<key>\w+)'
                              r'\s*=\s*'
                              r'(?P<value>("[^"]*"'
                              r'|\'[^\']*\''
                              r'|\w+))'
                              r'|(?P<position>\w+))')

    def __init__(self, media_root=media_root):
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

                key = attrs['href']
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
                    # match found! Add it. The key has to be a path relative
                    # to media root
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

    def link_files(self, target_root,
                   segregate_targets=settings.segregate_targets):
        """Links files to the target output directories.

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
        """
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

                # And link if the target doesn't exist
                if not os.path.isfile(render_path):
                    os.link(abs_path, render_path)
