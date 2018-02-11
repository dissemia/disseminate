"""
Classes and functions for generating trees of markup files.
"""
import glob
import os.path
import html
import time
from datetime import datetime

from .document import DocumentFactory
from .dependency_manager import DependencyManager
from . import settings


class TreeException(Exception): pass


def load_index_files(index_path, project_root=''):
    """Return a list of documents (source markup) files, relative to the
    project_root, identified by an index tree file (index.tree).

    The search is recursive. The index.tree files listed from sub-directories
    are included recursively.

    Parameters
    ----------
    index_path : str
        The path of an index tree file (index.tree).
    project_root : str, optional
        The project_root path. All files returned will be relative to this path.

    Returns
    -------
    src_filepaths: list of str
        An ordered list of documents (source markup) filenames and paths,
        relative to the project_root. These respect the ordering in the tree
        index file given by index_path.
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

    src_filepaths = []

    # If any of the files are tree index files (index.tree), then ast those
    # as well
    for filepath in filepaths:
        path, filename = os.path.split(filepath)

        if filename == settings.index_filename:
            src_filepaths += load_index_files(filepath)
        else:
            src_filepaths.append(filepath)

    # Return the src_filepaths, relative to project_root
    return [os.path.relpath(i, project_root) for i in src_filepaths]


class Tree(object):
    """A tree of documents.

    Trees are simply a flat list of documents (markup source) files. There is
    one tree for each project. Trees are constructed in one of two ways:

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

    .. note:: **tree paths**. The tree src_filepaths and target_filepaths are
              relative to the project_root and target_root, respectively.
              **render paths**. However, when creating documents, the paths
              are render_paths. These are either absolute or relative to the
              current directory.

    Attributes
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
    segregate_targets : bool
        If True, the processed output documents for each target type will be
        place in its directory named for the target.
        ex: 'out/html'
    target_list : list of str
        A list of target extensions to render documents to.
        ex: ['.html', '.tex', '.txt']
    managed_dirs : dict of str
        The directories and subdirectories managed by an index tree file
        (i.e. they contain an index.tree).
        ex: {'src/': 'src/index.tree'
             'src/sub1': 'src/index.tree'}
    src_filepaths : list of str
        The document (markup source) paths, including filenames, relative to
        the target root.
    documents : dict of :obj:`disseminate.Document`
        The documents for this tree. The keys are src_filepaths and the
        values are documents.
    global_context : dict
        The global context to store variables shared between all documents.
    """

    project_root = None
    target_root = None
    segregate_targets = None
    target_list = None
    managed_dirs = None
    src_filepaths = None
    documents = None
    global_context = None

    def __init__(self, project_root, target_root,
                 segregate_targets=settings.segregate_targets,
                 target_list=settings.default_target_list):
        assert isinstance(target_list, list) or isinstance(target_list, tuple)
        self.project_root = project_root
        if target_root == '.' or target_root == './':
            self.target_root = ''
        else:
            self.target_root = target_root
        self.segregate_targets = segregate_targets
        self.target_list = target_list
        self.src_filepaths = []
        self.document_factory = DocumentFactory()
        self.documents = {}
        self.global_context = {}

        # Populate the dependencies in the global context
        dep = DependencyManager(project_root=self.project_root,
                                target_root=self.target_root,
                                segregate_targets=self.segregate_targets)
        self.global_context['_dependencies'] = dep

        # The time of the last render
        self._last_render = None

    def find_managed_dirs(self, reload=False):
        """Populate the managed directories (self.managed_dirs) by locating
        index treefiles (e.g. index.tree).

        This method sets the self.managed_dirs attribute. This attribute
        contains managed directories (relative to the project_root) as keys and
        the corresponding tree index file path (index.tree, relative to the
        project root) as values.

        ex: {'': 'index.tree',
             'sub1': 'index.tree',
             'sub1/sub12': 'index.tree'}

             In this case, the index.tree in the project root manages the '',
             'sub1' and 'sub2' directories.

        .. note:: The presence of an index.tree file in a directory implies
                  that the directory and all its subdirectories are managed by
                  this file. Consequently, index tree files in sub-directories
                  will be ignored, unless they are explicitly included in the
                  root index tree file.

        Parameters
        ----------
        reload : bool, optional
            If True, the managed directories will be re-evaluated, regardless
            of whether they were evaluated before. Otherwise, the result
            from a previous evaluation (if available) are used.

        Returns
        -------
        None
        """
        if not reload and isinstance(self.managed_dirs, dict):
            return None
        self.managed_dirs = dict()
        project_root = self.project_root

        # expand the user for the subpath directory
        if isinstance(project_root, str):
            project_root = os.path.expanduser(project_root)

        # Construct the glob pattern to search for index.tree files. These are
        # render paths
        search_glob = os.path.join(project_root, '**',
                                   settings.index_filename)

        # Get the glob list and sort it by length so that root paths come up
        # first. If two strings have the same length, then they will be sorted
        # alphabetically
        index_paths = sorted(glob.glob(search_glob, recursive=True),
                             key=lambda i: (len(i), i))

        # Go through each tree index file and mark its directory and
        # sub-directories as managed
        for index_path in index_paths:
            index_dir, index_filename = os.path.split(index_path)
            rel_index_path = os.path.relpath(index_path, project_root)
            rel_index_dir = os.path.relpath(index_dir, project_root)

            # Do nothing if this directory is already managed by another
            # index tree file.
            if rel_index_dir in self.managed_dirs:
                continue

            # Find all subdirectories to index_dir and mark these as managed
            # as well. The os.path.split is designed to just isolate the
            # directory name without the trailing '/' (and to make it
            # compatible with managed paths calculated above)
            glob_search = os.path.join(index_dir, '**/')
            sub_dirs = [os.path.split(i)[0] for i in
                        glob.glob(glob_search, recursive=True)]

            for sub_dir in sub_dirs:
                # Set sub_dir relative to the project root
                sub_dir = os.path.relpath(sub_dir, project_root)
                sub_dir = sub_dir if sub_dir != '.' else ''
                self.managed_dirs[sub_dir] = rel_index_path

        return None

    def find_documents_in_indexes(self):
        """Find the document (markup source) files listed in the index files
        and populate the document (markup) source files in order.

        This method populates the self.src_filepaths attributes.

        .. note:: This function only looks at index.tree files that are in
                  managed directories. See the :meth:`find_managed_dirs` above.

        Returns
        -------
        None
        """
        if not isinstance(self.src_filepaths, list):
            self.src_filepaths = []

        # Populate the managed_dirs
        self.find_managed_dirs()

        # Get a list of all index files. These are sorted by length so that
        # root directories are presented first, then they are sorted
        # alphabetically.
        index_files = set(self.managed_dirs.values())
        index_files = sorted(index_files,
                             key=lambda i: (len(i), i))

        # The index_files have to be translated to render paths. i.e. they have
        # to be converted from the project_root to the current directory
        index_files = [os.path.join(self.project_root, i) for i in index_files]

        # Now load the indexes to get the document (markup) files.
        for index_file in index_files:
            new_documents = load_index_files(index_file,
                                             project_root=self.project_root)
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

            # Check that the new documents all exist.
            for i in new_documents:
                # These must be translated to render paths. i.e. from the
                # project_root
                i_current_dir = os.path.join(self.project_root, i)
                if not os.path.exists(i_current_dir):
                    msg = "The file '{}' in index tree '{}' does not exist."
                    raise TreeException(msg.format(i_current_dir, index_file))

    def find_documents_by_type(self):
        """Find the document (markup source) files that are not managed by
        index tree files.

        Only files with the document extension (settings.document_extension)
        are returned. (ex: .dm)

        This method populates the self.documents attribute.

        Returns
        -------
        None
        """
        project_root = self.project_root

        # expand the user for the subpath directory
        if isinstance(project_root, str):
            project_root = os.path.expanduser(project_root)

        if not isinstance(self.src_filepaths, list):
            self.src_filepaths = []

        # Populate the managed_dirs
        self.find_managed_dirs(project_root)

        # Find all dirs with document files that are not managed. These are
        # render paths
        search_glob = os.path.join(project_root, '**',
                                   '*' + settings.document_extension)

        # Find the files and convert filepaths relative to the project_root
        filepaths = [os.path.relpath(i, project_root) for i in
                     glob.glob(search_glob, recursive=True)]

        # and separate them into ('directory', 'filename') tuples
        filepaths = [os.path.split(i) for i in filepaths]

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

    def find_documents(self):
        """Finds all the document (source markup) files in the tree by first
        looking up tree index files, then finding documents in unmanaged
        directories.

        Since tree index files are searched first, these documents appear in
        the tree *before* files from unmanaged directories.

        This method resets and populates the self.documents attribute.

        Returns
        -------
        None
        """
        self.src_filepaths = []
        self.find_documents_in_indexes()
        self.find_documents_by_type()

    def convert_src_filepath(self, src_filepath, target_list=None,
                             relative_root=None):
        """Converts the src_filepath to a dict of targets and their target
        paths (relative to target_root).

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
        relative_root : str, optional
            If specified, the returned paths will be relative to the given
            output root directory.This is useful for constructing web links to
            the target.

            ex: 'out/html/main.html' becomes 'main.html' if relative_root=''

        Returns
        -------
        targets : dict
            A dict with the target extension as keys (ex: '.html') and the
            value is the target_filepath for that target.
            (ex: 'html/index.html')
        """
        # Get the target format. ex: '.html'
        target_list = (target_list if target_list is not None
                       else self.target_list)
        target_list = [t if t.startswith('.') else '.' + t
                       for t in target_list]

        returned_targets = {}
        for target in target_list:

            # Get the outpath relative to the target_root
            if relative_root is None:
                # Segregate the targets, if specified
                if self.segregate_targets:
                    outpath = target.strip('.')
                else:
                    outpath = ''
            else:
                outpath = relative_root

            # Get the target_filepath (relative to target_root) by constructing
            # the filename from the output_dir and the src_filepath, to
            # maintain the directory structure of src_filepath
            base, ext = os.path.splitext(os.path.join(src_filepath))
            new_path = os.path.join(outpath, base + target)
            returned_targets[target] = new_path

        return returned_targets

    def convert_target_filepath(self, target_filepath):
        """Converts a target_filepath (relative to target_root) to a
        src_filepath (relative to project_root).

        .. note:: This method looks up the src_filepath based on rendered
                  documents. Consequently, the documents should have been found
                  and rendered, before using this method.

        .. note:: The tree uses src and target filepaths relative to the
                  project_root and target_root, respectively, yet documents use
                  render src and target filepaths that are either absolute or
                  relative to the current directory. Consequently, this method
                  must translate tree paths and directory paths.

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
        # Get the target_filepath relative to the current directory
        render_target_filepath = os.path.join(self.target_root,
                                              target_filepath)
        base, target = os.path.splitext(render_target_filepath)

        # First look in the documents to see if a match can be found.
        # The document src_filepath and targets paths are either absolute or
        # relative to the current_directory
        for doc in self.documents.values():
            doc_target_filepath = doc.targets.get(target, None)

            if (doc_target_filepath is not None and
               doc_target_filepath == render_target_filepath):

                # Get src_filepath relative to project_root
                src_filepath = os.path.relpath(doc.src_filepath,
                                               self.project_root)
                return src_filepath, target

        # A source document was not found, raise an exception
        msg = ("The source document for the '{}' target filepath could not "
               "be found.")
        raise TreeException(msg.format(target_filepath))

    def render(self, target_list=None):
        """Render documents.

        .. note:: This function populates the self.documents attribute.

        .. note:: The tree uses src and target filepaths relative to the
                  project_root and target_root, respectively, yet documents use
                  src and target filepaths that are either absolute or relative
                  to the current directory. Consequently, this method must
                  translate tree paths and directory paths.

        Parameters
        ----------
        target_list : list of str, optional
            If specified, the list of target extensions with be rendered.
            If not specified, the value of self.target_list will be used.
        """
        target_list = (target_list if target_list is not None else
                       self.target_list)

        # Generate the global context, if needed
        self.global_context = (self.global_context
                               if isinstance(self.global_context, dict)
                               else dict())

        # Update the documents in this tree. Remove any documents from
        # self.documents that are no longer managed or don't exist.
        self.find_documents()
        self.documents = {k: v for k, v in self.documents.items()
                          if k in self.src_filepaths}

        # Run and update the AST for each document that needs updating or each
        # new document. Running the `get_ast` method for each document
        # guarantees that the `local_context` and  `global_context` are up to
        # date.
        last_render = self._last_render
        current_render = time.time()

        src_filepaths_to_render = []  # keep track of which docs to render

        for src_filepath in self.src_filepaths:
            doc = self.documents.get(src_filepath, None)

            # Update if any of the following applies
            if (doc is None or  # the document hasn't been created yet
               last_render is None or  # documents haven't been rendered yet
               (os.path.isfile(src_filepath) and  # the file was recently saved
               os.stat(src_filepath).st_mtime > current_render)):
                # Create new document, if needed
                if doc is None:
                    targets = self.convert_src_filepath(src_filepath,
                                                        target_list=target_list)

                    # Convert the source and target paths, which are relative
                    # to the project_root and target_root, to render paths,
                    # which are absolute or relative to the current directory
                    render_src_filepath = os.path.join(self.project_root,
                                                       src_filepath)
                    render_targets = {k: os.path.join(self.target_root, v)
                                      for k,v in targets.items()}

                    # Create the Document object
                    kwargs = {'src_filepath': render_src_filepath,
                              'targets': render_targets,
                              'global_context': self.global_context}
                    doc = self.document_factory.document(**kwargs)
                    self.documents[src_filepath] = doc

                # Update the AST
                doc.get_ast()

                src_filepaths_to_render.append(src_filepath)

        # Render the documents. At this point, all of the documents should
        # have been created and populated in the self.documents
        for src_filepath in src_filepaths_to_render:
            doc = self.documents[src_filepath]
            doc.render()

        return True

    def html(self, target_list=None):
        """Renders an html stub string for the target_paths of the current
        tree.

        Parameters
        ----------
        target_list : list of str, optional
            If specified, the list of target extensions with be rendered.
            If not specified, the value of self.target_list will be used.

        Returns
        -------
        html : str
            An html stub of this tree.
        """
        target_list = (target_list if target_list is not None else
                       self.target_list)

        result_str = "<p><em>Project Directory:</em> {}</p>\n"
        result_str = result_str.format(self.project_root)

        # Add an entry for each src_filepath
        elem_strs = []
        for count, src_filepath in enumerate(self.src_filepaths, 1):
            # Add the count
            elem_str = "<tr><td class=\"num\">{}.</td>"
            elem_str = elem_str.format(count)

            # Get the target file paths
            kwargs = {'src_filepath': src_filepath,
                      'target_list': target_list,
                      'relative_root': '/'}

            targets = self.convert_src_filepath(**kwargs)

            # Create an entry and link for the source file
            elem_str += "<td class=\"src\"><a href=\"{}\">{}</a></td>"
            elem_str = elem_str.format(html.escape('/' + src_filepath),
                                       html.escape(src_filepath))

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

            # Add the modification time and date. To do this, we need to
            # get the path absolute path or path relative to the current
            # directory
            current_src_filepath = os.path.join(self.project_root, src_filepath)
            mtime = os.path.getmtime(current_src_filepath)
            date = datetime.fromtimestamp(mtime)
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
