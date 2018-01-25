"""
Classes and functions for generating trees of markup files.
"""
import glob
import os.path
import regex

#from .document import Document
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
    target : str
        The extension of the target documents. (ex: 'html')
    src_paths : list of str
        The document (markup source) paths, including filenames.
    target_paths : list of str
        The target paths, including filenames, of the generated documents.
    documents : dict
        A dict with the documents. The keys are target paths and the values
        are the document objects themselves (:obj:`disseminate.Document`).
    """

    subpath = None
    managed_dirs = None
    target = None
    src_paths = None
    target_paths = None
    documents = None

    def __init__(self, subpath=None, target=None):
        self.subpath = subpath
        self.target = target if target is not None else settings.default_target
        self.src_paths = []
        self.target_paths = []

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
        # The project_root is simply the current path if strip_base_project_path
        # is not True
        if not settings.strip_base_project_path:
            return '.'

        # Load the working directories
        self.find_managed_dirs(subpath)

        # Get all of the unique paths for the documents
        paths = sorted(set([os.path.split(i)[0] for i in self.src_paths]),
                       key=len)
        if len(paths) == 0:
            return '.'

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

        return best_path

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
        if not isinstance(self.src_paths, list):
            self.src_paths = []

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
            self.src_paths += new_documents

            # Check for duplicates
            documents_set = set(self.src_paths)
            if len(documents_set) < len(self.src_paths):  # a dupe exists
                # Find and report the duplicate
                seen = set()
                for i in self.src_paths:
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
        if not isinstance(self.src_paths, list):
            self.src_paths = []

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

        self.src_paths += filepaths

        # Check to make sure there are no duplicates. (sanity check)
        assert len(self.src_paths) == len(set(self.src_paths))

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
        self.src_paths = []
        self.find_documents_in_indexes(subpath=subpath)
        self.find_documents_by_type(subpath=subpath)
        self.convert_target_paths(subpath=subpath)

    def convert_target_paths(self, subpath=None):
        """Converts the src_filepaths to the target_filepaths using the
        project_root method (:meth:`Tree.project_root`) and the target type.

        subpath : str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.
        """
        if not isinstance(self.target_paths, list):
            self.target_paths = []

        # Get the project root
        project_root = self.project_root(subpath=subpath)

        # Get the target format. ex: '.html'
        target = (self.target if self.target.startswith('.') else
                  '.' + self.target)

        for i in self.src_paths:
            # Get a new path relative to the project_root
            relative_path = os.path.relpath(i, project_root)

            # Replace the extension with the target extension
            split_ext = list(os.path.splitext(relative_path)[:-1])
            split_ext.append(target)
            new_path = ''.join(split_ext)
            if new_path not in self.target_paths:
                self.target_paths.append(new_path)

    def find_template(self, document):
        """Locate the template for a given document.

        Parameters
        ----------
        document: :obj:`disseminate.Document`
            A document object.

        Returns
        -------
        template : :obj:`jinga2.environment.Template`
            A template object.
        """

    def render(self, *documents):
        """Render documents.

        This function function renders one, multiple or all documents.

        ..note: This function populates the self.documents attribute.

        Parameters
        ----------
        documents : list
            Documents can either be:
            - A document_path for a document (markup source) file. (i.e. .dm
              extension)
            - A target_path for a document. (i.e. .html extension)
            - A document object (:obj:`disseminate.Document`)
            - (empty) In this case, all the documents in the document_path
              will be rendered.
        """
        # Get contexts for each document
        # Get templates
        # render documents
        pass

    #def render_documents(self):
        """Converts documents.

        Processes self.src_paths into self.documents.
        """

    #def html(self):

    #def_get_global_contexts

    #def get_targets

