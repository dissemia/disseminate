"""
Classes and functions for generating trees of markup files.
"""
import glob
import os.path

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

    documents = []

    # If any of the files are tree index files (index.tree), then parse those
    # as well
    for filepath in filepaths:
        path, filename = os.path.split(filepath)

        if filename == settings.index_filename:
            documents += load_index_files(filepath)
        else:
            documents.append(filepath)

    return documents


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
        - If an 'index.tree' is not available, one is generated using the
          default document (markup) extension (see settings.document_extension).
          For all *unmanaged* directories and subdirectories.
          These will be sorted by filename.

    Attributes
    ----------
    subpath: str, optional
        The subpath (sub-directory) of the current directory to search.
    managed_dirs: dict of str
        The subpaths (directories and subdirectories) managed by an index tree
        file (index.tree).

        ex: {'src/': 'src/index.tree'
             'src/sub1': 'src/index.tree'
    """

    subpath = None
    managed_dirs = None
    documents = None

    def __init__(self, subpath=None):
        self.subpath = subpath

    def find_managed_dirs(self, subpath=None, reload=False):
        """Populate the managed directories (self.managed_dirs) by locate index
        treefiles (e.g. index.tree).

        .. note:: The presence of an index.tree file in a directory implies
                  that the directory and all its subdirectories are managed by
                  this file. Consequently, index tree files in sub-directories
                  will be ignored, unless they are explicitly included in the
                  root index tree file.

        Parameters
        ----------
        subpath: str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.
        reload: bool, optional
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

        .. note:: This function only looks at index.tree files that are in
                  managed directories. See the :meth:`find_managed_dirs` above.

        Parameters
        ----------
        subpath: str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        if not isinstance(self.documents, list):
            self.documents = []

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
            self.documents += new_documents

            # Check for duplicates
            documents_set = set(self.documents)
            if len(documents_set) < len(self.documents):  # a dupe exists
                # Find and report the duplicate
                seen = set()
                for i in self.documents:
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

        Parameters
        ----------
        subpath: str, optional
            If specified, only look in the given subpath directory. If this is
            not specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        subpath = subpath if subpath is not None else self.subpath
        if not isinstance(self.documents, list):
            self.documents = []

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

        self.documents += filepaths

        # Check to make sure there are no duplicates. (sanity check)
        assert len(self.documents) == len(set(self.documents))

        return None
