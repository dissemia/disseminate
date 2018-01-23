"""
Classes and functions for generating trees of markup files.
"""
import glob
import os.path

from . import settings


class TreeException(Exception): pass


class Tree(object):
    """A tree of documents.

    Trees are simply a flat list of source files. Trees are constructed in one
    of two ways:

        - (Preferable) If 'index.tree' (see settings.index_filename) files are
          available, these are used to construct the tree. The 'index.tree'
          contains a list of filenames, in order, for the source files to
          render.
        - If an 'index.tree' is not available, one is generated using the
          default markup extension (see settings.document_extension). These
          will be sorted by filename.
    """

    def find_index_files(self, subpath=None):
        """Locate index files (e.g. index.tree) in the current directory and
        produce an index.

        Parameters
        ----------
        subpath: str, optional
            If specified, only the given subpath will be searched for index
            tree files.

        Returns
        -------
        index: dict
            A dict with directories and subdirectories as the key and a list of
            markup files (e.g. dsm) as the value.

            ex: {'src/': ['src/intro.dsm', 'src/discussion.dsm'}
        """
        if subpath:
            search_glob = os.path.join(subpath, '**', settings.index_filename)
        else:
            search_glob = os.path.join('**', settings.index_filename)
        index = {}

        for indexpath in glob.glob(search_glob, recursive=True):
            # parse the paths
            # indexpath: src/index.tree
            # directory: src/
            # filename: index.tree
            directory, filename = os.path.split(indexpath)

            # Open the index file and verify that all files exist
            with open(indexpath, 'r') as f:
                markup_files = [i.strip() for i in f.readlines() if i.strip()]

            # These files are relative to the subdirectory. Create paths that
            # are relative to the current directory.
            markup_files = [os.path.join(directory, i) for i in markup_files]

            # Verify that all the files exist
            for file in markup_files:
                if not os.path.exists(file):
                    msg = "The file '{}' in index tree '{}' does not exist."
                    raise TreeException(msg.format(file, indexpath))

            # Verify that there are no duplicates
            unique_files = set(markup_files)
            if len(unique_files) < len(markup_files):  # Then there's a dup
                seen = set()
                for i in markup_files:
                    if i in seen:
                        msg = "The file '{}' in index tree '{}' is duplicated."
                        raise TreeException(msg.format(i, indexpath))
                    else:
                        seen.add(i)

            # Add the entries to the index
            index.update({directory:markup_files})

        return index

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






