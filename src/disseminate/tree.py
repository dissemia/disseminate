"""
Classes and functions for generating trees of markup files.
"""
import glob
import os.path
import regex
import html
from datetime import datetime

from .document import Document
from .templates import get_template
from . import settings


class TreeException(Exception): pass


def load_index_files(index_path):
    """Return a list of documents (source markup) files identified by an index
    tree file (index.tree).

    The search is recursive, in index.tree files in sub-directories are
    listed.

    Parameters
    ----------
    index_path: str
        The path of an index tree file (index.tree).

    Returns
    -------
    documents: list
        An ordered list of documents (source markup) filenames and paths. These
        respect the ordering in the tree index file given by index_path.
    """
    # Check that the index_path exists
    if not os.path.exists(index_path):
        msg = "The index tree file at '{}' cannot be found."
        raise TreeException(msg.format(index_path))

    # Load the files in the index_path
    index_dir, index_filename = os.path.split(index_path)
    with open(index_path) as f:
        filenames = [i.strip() for i in f.readlines() if i.strip()]

    # Prepend the index_dir to all filenames since the files listed in the
    # tree index file are relative to the tree index path.
    filepaths = [os.path.join(index_dir, i) for i in filenames]

    document_paths = []

    # If any of the files are tree index files (index.tree), then ast those
    # as well
    for filepath in filepaths:
        path, filename = os.path.split(filepath)

        if filename == settings.index_filename:
            document_paths += load_index_files(filepath)
        else:
            document_paths.append(filepath)

    return document_paths


class Tree(object):
    """A tree of documents.

    Trees are simply a flat list of documents (markup source) files. Trees are
    constructed in one of two ways:

        - (Preferable) If tree index files (index.tree by default, see
          settings.index_filename) files are available, these are used to
          construct the tree first. The 'index.tree' contains a list of
          filenames, in order, for the source files to render, or they may
          further contain other index.tree files. If an index.tree file exists
          in a directory, it is assumed that this file *manages* the tree index
          files and document files in its own directory and all subdirectories.
        - If an 'index.tree' is not available, then the directory is considered
          unmanaged. A list of documents is constructed for files matching the
          default document extenstion ('.dm' by default, see
          settings.document_extension).
          These will be sorted by filename and added after the indexed files.

    Attributes
    ----------
    subpath : str, optional
        The subpath (sub-directory) of the current directory to search.
    managed_dirs : dict of str
        The subpaths (directories and subdirectories) managed by an index tree
        file (index.tree).

        ex: {'src/': 'src/index.tree'
             'src/sub1': 'src/index.tree'}
    target_list : list of str
        A list of target extensions to render documents to.
        ex: ['.html', '.tex', '.txt']
    src_filepaths : list of str
        The document (markup source) paths, including filenames.
    documents : list of :obj:`disseminate.Document`
        The documents for this tree.
    global_context : dict
        The global context to store variables shared between all documents.
    """

    subpath = None
    managed_dirs = None
    target_list = None
    output_dir = None
    src_filepaths = None
    documents = None
    global_context = None

    def __init__(self, subpath=None, target_list=settings.default_target_list,
                 output_dir=None):
        assert isinstance(target_list, list) or isinstance(target_list, tuple)
        self.subpath = subpath
        self.target_list = target_list
        self.output_dir = output_dir
        self.src_filepaths = []
        self.documents = []
        self.global_context = {}
        self._project_root = None

    def project_root(self, subpath=None):
        """Evaluate the path (directory) of the project root.

        This function depends on settings.strip_base_project_path. If the
        settings.strip_base_project_path is True, then this function will
        attempt to find the 'common denominator' path for all the documents
        and return this path. Otherwise it will return the current directory.

        Parameters
        ----------
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        project_root : str
            The string for the project root
        """
        # Cache the project_root
        if getattr(self, '_project_root', None) is not None:
            return self._project_root

        # The project_root is simply the current path if strip_base_project_path
        # is not True
        if not settings.strip_base_project_path:
            self._project_root = '.'
            return self._project_root

        # Load the working directories
        self.find_managed_dirs(subpath)

        # Get all of the unique paths for the documents
        paths = sorted(set([os.path.split(i)[0] for i in self.src_filepaths]),
                       key=len)
        if len(paths) == 0:
            self._project_root = '.'
            return self._project_root

        # Go directory-by-directory to see if they're common to all paths
        reference_path = paths[0]
        regex_string = r'([^/]+/?){'

        # Start with the first path (i.e. the current path, '.')
        best_path = '.'

        # Build the path directory-by-directory
        for i in range(1,15):
            base_path = regex.match(regex_string + repr(i) + r'}',
                                    reference_path)
            base_path = base_path.group() if base_path is not None else None

            if base_path and all(i.startswith(base_path) for i in paths):
                # A new base path is found
                best_path = base_path
            else:
                break

        self._project_root = best_path
        return self._project_root

    def find_managed_dirs(self, subpath=None, reload=False):
        """Populate the managed directories (self.managed_dirs) by locate index
        treefiles (e.g. index.tree).

        This method sets the self.managed_dirs attribute.

        .. note:: The presence of an index.tree file in a directory implies
                  that the directory and all its subdirectories are managed by
                  this file. Consequently, index tree files in sub-directories
                  will be ignored, unless they are explicitly included in the
                  root index tree file.

        Parameters
        ----------
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.
        reload : bool, optional
            If True, the managed directories will be re-evaluated, regardless
            of whether they were evaluated before. Otherwise, the result
            from a previous evaluation (if available) are used.

        Returns
        -------
        None
        """
        if not reload and isinstance(self.find_managed_dirs, dict):
            return None
        self.managed_dirs = dict()
        subpath = subpath if subpath is not None else self.subpath

        # expand the user for the subpath directory
        if isinstance(subpath, str):
            subpath = os.path.expanduser(subpath)

        # Construct the glob pattern to search for index.tree files
        if subpath:
            search_glob = os.path.join(subpath, '**', settings.index_filename)
        else:
            search_glob = os.path.join('**', settings.index_filename)

        # Get the glob list and sort it by length so that root paths come up
        # first. If two strings have the same length, then they will be sorted
        # alphabetically
        index_paths = sorted(glob.glob(search_glob, recursive=True),
                             key=lambda i: (len(i), i))

        # Go through each tree index file and mark its directory and
        # sub-directories as managed
        for index_path in index_paths:
            index_dir, index_filename = os.path.split(index_path)

            # Do nothing if this directory is already managed by another
            # index tree file.
            if index_dir in self.managed_dirs:
                continue

            # Find all subdirectories to index_dir and mark these as managed
            # as well. The os.path.split is designed to just isolate the
            # directory name without the trailing '/' (and to make it
            # compatible with managed paths calculated above)
            glob_search = os.path.join(index_dir, '**/')
            sub_dirs = [os.path.split(i)[0] for i in
                        glob.glob(glob_search, recursive=True)]

            for sub_dir in sub_dirs:
                self.managed_dirs[sub_dir] = index_path

        return None

    def find_documents_in_indexes(self, subpath=None):
        """Find the document (markup source) files listed in the index files
        and populate the document (markup) source
        files in order.

        This method populates the self.documents attribute

        .. note:: This function only looks at index.tree files that are in
                  managed directories. See the :meth:`find_managed_dirs` above.

        Parameters
        ----------
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        if not isinstance(self.src_filepaths, list):
            self.src_filepaths = []

        # Populate the managed_dirs
        self.find_managed_dirs(subpath)

        # Get a list of all index files. These are sorted by length so that
        # root directories are presented first, then they are sorted
        # alphabetically.
        index_files = set(self.managed_dirs.values())
        index_files = sorted(index_files,
                             key=lambda i: (len(i), i))

        # Now load the indexes to get the document (markup) files.
        for index_file in index_files:
            new_documents = load_index_files(index_file)
            self.src_filepaths += new_documents

            # Check for duplicates
            documents_set = set(self.src_filepaths)
            if len(documents_set) < len(self.src_filepaths):  # a dupe exists
                # Find and report the duplicate
                seen = set()
                for i in self.src_filepaths:
                    if i in seen:
                        msg = "The file '{}' in index tree '{}' is duplicated."
                        raise TreeException(msg.format(i, index_file))
                    else:
                        seen.add(i)

            # Check that the new documents all exist
            for i in new_documents:
                if not os.path.exists(i):
                    msg = "The file '{}' in index tree '{}' does not exist."
                    raise TreeException(msg.format(i, index_file))

    def find_documents_by_type(self, subpath=None):
        """Find the document (markup source) files that are not managed by
        index tree files.

        Only files with the document extension (settings.document_extension)
        are returned. (ex: .dm)

        This method populates the self.documents attribute.

        Parameters
        ----------
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        subpath = subpath if subpath is not None else self.subpath

        # expand the user for the subpath directory
        if isinstance(subpath, str):
            subpath = os.path.expanduser(subpath)

        if not isinstance(self.src_filepaths, list):
            self.src_filepaths = []

        # Populate the managed_dirs
        self.find_managed_dirs(subpath)

        # Find all dirs with document files that are not managed
        if subpath:
            search_glob = os.path.join(subpath, '**',
                                       '*' + settings.document_extension)
        else:
            search_glob = os.path.join('**',
                                       '*' + settings.document_extension)

        # Find the files and separate them into ('directory', 'filename')
        # tuples
        filepaths = [os.path.split(i) for i in
                     glob.glob(search_glob, recursive=True)]

        # Remove any paths that are managed (i.e. whose directory is already
        # in the self.managed_dirs
        filepaths = [i for i in filepaths if i[0] not in self.managed_dirs]

        # Sort the filepaths by the directory and filenames lengths to present
        # root directories first
        filepaths = sorted(filepaths, key=lambda i: (len(i[0]), i, len(i[1])))

        # Join the filepaths and add them to the documents
        filepaths = [os.path.join(*i) for i in filepaths]

        self.src_filepaths += filepaths

        # Check to make sure there are no duplicates. (sanity check)
        assert len(self.src_filepaths) == len(set(self.src_filepaths))

        return None

    def find_documents(self, subpath=None):
        """Finds all the document (source markup) files in the tree by first
        looking up tree index files, then finding documents in unmanaged
        directories.

        Since tree index files are searched first, these documents appear in
        the tree *before* files from unmanaged directories.

        This method resets and populates the self.documents attribute.

        Parameters
        ----------
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        self.src_filepaths = []
        self.find_documents_in_indexes(subpath=subpath)
        self.find_documents_by_type(subpath=subpath)

    def convert_src_filepath(self, src_filepath, target_list=None,
                             output_dir = None,
                             segregate_target=settings.segregate_targets,
                             subpath=None):
        """Converts the src_filepath to a dict of targets.

        .. note:: The method uses the project_root (:meth:`Tree.project_root`)
                  method to find the project root.

        Parameters
        ----------
        src_filepath : str
            A filename for a document (markup source) file. This file should
            exist.
        target_list : list, optional
            A list of target extension of the rendered document.
            (ex: ['.html', ]) If None is specified, then self.target_list will
            be used.
        output_dir : str, optional
            If specified, files will be saved in this directory.
        segregate_target : bool, optional
            If True, rendered target documents will be saved in a subdirectory
            with the target extension's name (ex: 'html' 'tex')
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        targets : dict
            A dict with the target extension as keys (ex: '.html') and the
            value is the target_filepath for that target.
            (ex: 'html/index.html')
        """
        # Get the project root
        project_root = self.project_root(subpath=subpath)

        # Get the target format. ex: '.html'
        target_list = (target_list if target_list is not None
                       else self.target_list)
        target_list = [t if t.startswith('.') else '.' + t
                       for t in target_list]

        # Get the output_directory, if specified
        output_dir = (output_dir if isinstance(output_dir, str) else
                      self.output_dir)

        # expand the user for the output directory
        if output_dir is not None:
            output_dir = os.path.expanduser(output_dir)

        # Get a new path relative to the project_root
        relative_path = os.path.relpath(src_filepath, project_root)

        returned_targets = {}
        for target in target_list:
            # Segregate the targets, if specified
            if segregate_target:
                relative_path = os.path.join(target.strip('.'), relative_path)

            # Set path to output_dir, if specified
            if output_dir is not None:
                relative_path = os.path.join(output_dir, relative_path)

            # Replace the extension with the target extension
            split_ext = list(os.path.splitext(relative_path)[:-1])
            split_ext.append(target)
            new_path = ''.join(split_ext)
            returned_targets[target] = new_path

        return returned_targets

    def convert_target_filepath(self, target_filepath):
        """Converts a target_filepath to a src_filepath.

        .. note:: This method looks up the src_filepath based on rendered
                  documents. Consequently, the documents should have been found
                  and rendered, before using this method.

        Parameters
        ----------
        target_filepath : str
            A filepath for a target. ex: 'html/index.html'

        Returns
        -------
        src_filepath, target : str, str
            The corresponding src_filepath (ex: 'src/index.dm') and the target
            of the given target_filepath (ex: '.html).

        Raises
        ------
        TreeException
            If the document and src_filepath could not be found.
        """
        base, target = os.path.splitext(target_filepath)

        # First look in the documents to see if a match can be found.
        if isinstance(self.documents, list):
            for doc in self.documents:
                doc_target_filepath = doc.targets.get(target, None)

                if (doc_target_filepath is not None and
                   doc_target_filepath == target_filepath):
                    return doc.src_filepath, target

        # A source document was not found, raise an exception
        msg = ("The source document for the '{}' target filepath could not "
               "be found.")
        raise TreeException(msg.format(target_filepath))

    def render(self, src_filepaths=None,
               target_list=None, output_dir=None, ):
        """Render documents.

        This function renders the src_filepaths documents.

        ..note: This function populates the self.target_filepaths attribute.

        Parameters
        ----------
        src_filepaths : list of str or str, optional
            A filename for a document (markup source) file. This file should
            exist.
        target_list : list of str, optional
            If specified, the list of target extensions with be rendered.
            If not specified, the value of self.target_list will be used.
        output_dir : str, optional
            If specified, files will be saved in this directory.
        """
        # Generate the global context, if needed
        self.global_context = (self.global_context
                               if isinstance(self.global_context, dict)
                               else dict())

        # Check to see if the tree needs to be updated. The tree is updated
        # when:
        # - No src_filepaths are specified. In this case, all src_filepaths
        #   are used.
        # The tree doesn't need to be updated when:
        # - src_filepaths points to one or more files that was previously
        #   rendered alone. This is because the rest of the tree hasn't changed.
        if src_filepaths is None:
            src_filepaths = self.src_filepaths

        # Check to see if it matches the last request src_filepaths and targets
        # If so, just render these documents
        #if (src_filepaths == getattr(self, 'last_src_filepaths', None) and
        #    target_list == getattr(self, '_last_target_list', None)):
        #    pass
        #else:
        #    src_filepaths = self.src_filepaths

        # render documents
        for src_filepath in self.src_filepaths:
            targets = self.convert_src_filepath(src_filepath,
                                                target_list=target_list,
                                                output_dir=output_dir)

            doc = Document(src_filepath=src_filepath,
                           targets=targets,
                           global_context=self.global_context)
            doc.render()
            self.documents.append(doc)

        return True

    def html(self, target_list=settings.default_target_list,
             output_dir=None,
             segregate_target=settings.segregate_targets,
             subpath=None):
        """Renders an html stub string for the target_paths of the current
        tree.

        Parameters
        ----------
        target_list : list of str, optional
            If specified, the list of target extensions with be rendered.
            If not specified, the value of self.target_list will be used.
        output_dir : str, optional
            If specified, files will be saved in this directory.
        segregate_target : bool, optional
            If True, rendered target documents will be saved in a subdirectory
            with the target extension's name (ex: 'html' 'tex')
        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        html : str
            An html stub of this tree.
        """
        target_list = target_list if target_list is not None else target_list
        project_root = self.project_root(subpath=subpath)

        result_str = "<p><em>Project Directory:</em> {}</p>\n"
        result_str = result_str.format(project_root)

        # Add an entry for each src_filepath
        elem_strs = []
        for count, src_filepath in enumerate(self.src_filepaths, 1):
            # Add the count
            elem_str = "<tr><td class=\"num\">{}.</td>"
            elem_str = elem_str.format(count)

            # Get the src_filepath relative to the project_root
            relative_src_filepath = os.path.relpath(src_filepath, project_root)

            # Get the target file paths
            kwargs = {'src_filepath': src_filepath,
                      'target_list': target_list,
                      'segregate_target': segregate_target,
                      'output_dir': output_dir,
                      'subpath': subpath}
            targets = self.convert_src_filepath(**kwargs)

            # Create an entry and link for the source file
            elem_str += "<td class=\"src\"><a href=\"{}\">{}</a></td>"
            elem_str = elem_str.format(html.escape(src_filepath),
                                       html.escape(relative_src_filepath))

            # Add links for the targets
            if isinstance(target_list, list):
                elem_str += "<td class=\"tgt\">("
                target_str = []
                for target in target_list:
                    if target not in targets:
                        continue
                    str = "<a href=\"{}\">{}</a>"
                    str = str.format(html.escape(targets[target]),
                                                 html.escape(target.strip('.')))
                    target_str.append(str)
                elem_str += " ".join(target_str) + ")</td>"
            else:
                elem_str += "<td class=\"tgt\"></td>"

            # Add the modification time and date
            date = datetime.fromtimestamp(os.path.getmtime(src_filepath))
            date = date.strftime("%b %d, %Y at %I:%M%p").replace(" 0", " ")
            elem_str += "<td class=\"date\">" + date + "</td>"

            # Terminate the tag for this item
            elem_str += "</tr>"
            elem_strs.append(elem_str)

        top = "<table>\n  "
        top += ("<thead>"
                "<th>num</th>"
                "<th>source</th>"
                "<th>targets</th>"
                "<th>last saved</th>"
                "</thead>\n")
        top += "<tbody>"
        bottom = "</tbody>\n</table>"
        result_str += "\n".join((top, *elem_strs, bottom))
        return result_str
