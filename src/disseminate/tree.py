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

    Trees are simply a flat list of source files. Trees are constructed in one
    of two ways:

        - (Preferable) If 'index.tree' (see settings.index_filename) files are
          available, these are used to construct the tree. The 'index.tree'
          contains a list of filenames, in order, for the source files to
          render.
          If an index.tree file exists in a directory, it is assumed that this
          file manages the tree index files and document files in its own
          directory and all subdirectories.
        - If an 'index.tree' is not available, one is generated using the
          default document (markup) extension (see settings.document_extension).
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
    document_files = None

    def __init__(self, subpath=None):
        self.subpath = subpath

    def find_managed_dirs(self, subpath=None):
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
            If specified, only look in the given subpath directory. If this is not
            specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        self.managed_dirs = dict()
        subpath = subpath if subpath is not None else self.subpath

        # Construct the glob pattern to search for index.tree files
        if subpath:
            search_glob = os.path.join(subpath, '**', settings.index_filename)
        else:
            search_glob = os.path.join('**', settings.index_filename)

        # Get the glob list and sort it by length so that root paths come up
        # first
        index_paths = sorted(glob.glob(search_glob, recursive=True), key=len)

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

    def find_index_files(self, subpath=None):
        """Identify the index files and populate the document (markup) source
        files in order.

        .. note:: This function only looks at index.tree files that are in
                  managed directories. See the :meth:`find_managed_dirs` above.

        Parameters
        ----------
        subpath: str, optional
            If specified, only look in the given subpath directory. If this is not
            specified, the value of self.subpath will be searched as well.

        Returns
        -------
        None
        """
        # Populate the managed_dirs
        self.find_managed_dirs(subpath)

        # Get a list of all index files. These are sorted by length so that
        # root directories are presented first
        index_files = set(self.managed_dirs.values)
        index_files = sorted(index_files, key=len)

        # Now create an index of document (markup) files. The index.tree
        # files may themselves include index.tree files in subdirectories,
        # so these have to be expanded


    # def find_index_files(self, subpath=None):
    #     """Locate index files (e.g. index.tree) in the current directory and
    #     produce an index.
    #
    #     Parameters
    #     ----------
    #     subpath: str, optional
    #         If specified, only the given subpath will be searched for index
    #         tree files.
    #
    #     Returns
    #     -------
    #     index: list of typles
    #         A list with tuples of the directories and document files.
    #
    #         ex: [('src', 'intro.dm'), ('src', 'discussion.dm')]
    #     """
    #     if subpath:
    #         search_glob = os.path.join(subpath, '**', settings.index_filename)
    #     else:
    #         search_glob = os.path.join('**', settings.index_filename)
    #     index = []
    #
    #     managed_paths = set()
    #     for indexpath in glob.glob(search_glob, recursive=True):
    #         # parse the paths
    #         # indexpath: src/index.tree
    #         # directory: src/
    #         # filename: index.tree
    #         directory, filename = os.path.split(indexpath)
    #
    #         # See if it's already in the managed paths so that sub-directories
    #         # of this index are not added. If so, do nothing else
    #         if any(i.startswith(directory) for i in managed_paths):
    #             continue
    #         managed_paths.append(directory)
    #
    #         # Open the index file and verify that all files exist
    #         with open(indexpath, 'r') as f:
    #             markup_files = [i.strip() for i in f.readlines() if i.strip()]
    #
    #         # These files are relative to the subdirectory. Create paths that
    #         # are relative to the current directory.
    #         markup_files = [os.path.join(directory, i) for i in markup_files]
    #
    #         # Verify that all the files exist
    #         for file in markup_files:
    #             if not os.path.exists(file):
    #                 msg = "The file '{}' in index tree '{}' does not exist."
    #                 raise TreeException(msg.format(file, indexpath))
    #
    #         # Verify that there are no duplicates
    #         unique_files = set(markup_files)
    #         if len(unique_files) < len(markup_files):  # Then there's a dup
    #             seen = set()
    #             for i in markup_files:
    #                 if i in seen:
    #                     msg = "The file '{}' in index tree '{}' is duplicated."
    #                     raise TreeException(msg.format(i, indexpath))
    #                 else:
    #                     seen.add(i)
    #
    #
    #         # Add the entries to the index
    #         for file in markup_files:
    #             index.append(os.path.split(file))
    #
    #     return index

    def find_document_files(self, subpath=None):
        """Locate documents (markup files) and produce an index.

        Parameters
        ----------
        subpath: str, optional
            If specified, only the given subpath will be searched for document
            files.

        Returns
        -------
        index: dict
            A dict with directories and subdirectories as the key and a list of
            markup files (e.g. dsm) as the value.

            ex: {'src/': ['src/intro.dsm', 'src/discussion.dsm'}
        """
        if subpath:
            search_glob = os.path.join(subpath, '**',
                                       '*' + settings.document_extension)
        else:
            search_glob = os.path.join('**',
                                       '*' + settings.document_extension)
        index = {}

        # Find all of the document files
        for documentpath in glob.glob(search_glob, recursive=True):
            # parse the paths
            # documentpath: src/index.ds
            # directory: src/
            # filename: index.ds
            directory, filename = os.path.split(documentpath)

            # Add it to the index
            file_list = index.setdefault(directory, [])
            file_list.append(documentpath)

        return index

    #def merge_indexes(self, preferred_index, supplemental_index):
    #    """Merges two indices.
    #        .. note: If entries are marked in both indexes, then the
    #             preferred_index takes precedence.
    #    """




