import os.path
import glob
from datetime import datetime
from collections import OrderedDict

from lxml.builder import E
from lxml import etree
from markupsafe import Markup

from .document import Document
from ..tags.utils import set_html_tag_attributes
from .. import settings


def find_project_paths(path='', document_extension=settings.document_extension):
    """Find the project paths within the given path.

    This function will only return the root project paths for directories
    containing disseminate files (i.e. files with the document_extension)

    Parameters
    ----------
    path : str, optional
        The path to search. By default, it is the current directory.
    document_extension : str, optional
        The source markup document extension. ex: '.dm'

    Returns
    -------
    project_paths : list
        A list of project paths as render paths.
    """
    # expand the user for the subpath directory
    path = os.path.expanduser(path)

    # Create a glob pattern to get all of the disseminate files in the path
    # and remove the filenames to retain the unique paths
    glob_pattern = os.path.join(path, '**', '*' + document_extension)
    paths = {os.path.split(i)[0]
             for i in glob.glob(glob_pattern, recursive=True)}

    # Sort the paths by length so that root paths come up first. If two strings
    # have the same length, then they will be sorted alphabetically
    sorted_paths = sorted(paths, key=lambda i: (len(i), i), reverse=True)

    # Remove all entries that are subdirectories of the root project directories
    root_paths = set()

    while sorted_paths:
        # Add root path
        root_path = sorted_paths.pop()
        root_paths.add(root_path)

        # Remove subdirectory
        sorted_paths = [i for i in sorted_paths if not i.startswith(root_path)]

    return root_paths


def load_root_documents(path='',
                        document_extension=settings.document_extension):
    """Load the root documents from the project paths for the given path."""
    documents = list()

    # Get the project paths and find the disseminate files in the root of these
    # paths
    project_paths = find_project_paths(path=path,
                                       document_extension=document_extension)

    for project_path in project_paths:
        # Find the paths for the root documents (non-recursive)
        glob_pattern = os.path.join(project_path, '*' + document_extension)
        src_filepaths = glob.glob(glob_pattern)

        # Load the documents. Note that recursive references in documents
        # will raise a DuplicateLabel error
        root_documents = [Document(src_filepath=s) for s in src_filepaths]

        documents += root_documents

    return documents


def translate_path(path, documents):
    """Translate a path to a render path.

    Given a src_filepath or target_filepath and documents, this function finds
    the corresponding render path for a path relative to the project_root or
    target_root. The file in the given render_path exists.

    Parameters
    ----------
    path : str
        The path relative to project_root or target_root.
    documents : list of :obj:`disseminate.Document`
        The documents whose paths should be checked.

    Returns
    -------
    render_path : str or None
    """
    # Strip the trailing slash, if present
    path = path if not path.startswith('/') else path[1:]

    # See if the path is already a render path
    if os.path.isfile(path):
        return path

    # Loop through the documents and see if a project_root or target_root
    # path is found.
    for document in documents:
        # Try constructing a render src_filepath
        src_filepath = os.path.join(document.project_root, path)
        if os.path.isfile(src_filepath):
            return src_filepath

        # Get all the targets for the document and sub-documents
        targets = set()
        for subdoc in document.documents_list(only_subdocuments=False,
                                              recursive=True):
            targets.update(subdoc.target_list)

        for target in targets:
            # Strip the target name of the preceeding period
            stripped_target = target.strip('.')

            # Try constructing a render target_filepath
            target_filepath = os.path.join(document.target_root,
                                           stripped_target, path)
            if os.path.isfile(target_filepath):
                return target_filepath

            # Try constructing a render target_filepath not include the target
            # sub-directory
            target_filepath = os.path.join(document.target_root, path)
            if os.path.isfile(target_filepath):
                return target_filepath

    return None


def render_tree_html(documents, level=1):
    """Render the html html for the given documents.

    Returns
    -------
    html : str
        An html stub of this tree.
    """
    tables = []
    document_elements = []

    for document in documents:
        # Column 1: the document number
        kwargs = OrderedDict((('class', 'num'),))
        num = E('td', str(document.number))
        set_html_tag_attributes(html_tag=num, attrs_dict=kwargs)

        # Column 2: the source file
        kwargs = OrderedDict((('class', 'src'),))
        src = E('td',
                E('a', document.src_filepath, href='/' + document.src_filepath))
        set_html_tag_attributes(html_tag=src, attrs_dict=kwargs)

        # Column 3: target files
        kwargs = OrderedDict((('class', 'tgt'),))
        tgt_links = [E('a', target.strip('.'),
                       href=document.target_filepath(target, render_path=False))
                     for target in document.targets.keys()]
        # Add commas to targets
        if len(tgt_links) > 1:
            new_tgt_links = [tgt_links[0]]
            for tgt_link in tgt_links[1:]:
                new_tgt_links.append(", ")
                new_tgt_links.append(tgt_link)
            tgt_links = new_tgt_links
        tgt = E('td', "(", *tgt_links, ")") if len(tgt_links) > 0 else E('td')
        set_html_tag_attributes(html_tag=tgt, attrs_dict=kwargs)

        # Column 4: src mtime
        kwargs = OrderedDict((('class', 'date'),))
        mtime = os.path.getmtime(document.src_filepath)
        d = datetime.fromtimestamp(mtime)
        date_str = d.strftime("%b %d, %Y at %I:%M%p").replace(" 0", " ")
        date = E('td', date_str)
        set_html_tag_attributes(html_tag=date, attrs_dict=kwargs)

        # Add the document row to the document_elements
        kwargs = OrderedDict((('class', 'level-' + str(level)),))
        row = E('tr', num, src, tgt, date)
        set_html_tag_attributes(html_tag=row, attrs_dict=kwargs)
        document_elements.append(row)

        # Add sub-documents
        if document.subdocuments is not None:
            sub_docs = document.subdocuments.values()
            document_elements += render_tree_html(sub_docs, level+1)

        if level == 1 and document_elements:

            title = E('div', E('strong', 'Project Title: '),
                        document.title,
                        **{'class': 'caption-title'})
            head = E('thead',
                     E('tr',
                       E('th', 'num'),
                       E('th', 'source'),
                       E('th', 'targets'),
                       E('th', 'last saved')))
            kwargs = OrderedDict((('class', 'tablesorter'), ('id', 'index')))
            table = E('table', title, head, *document_elements)
            set_html_tag_attributes(html_tag=table, attrs_dict=kwargs)
            tables.append(table)

    if level == 1:
        if tables:
            kwargs = OrderedDict((('class', 'tableset'),))
            div = E('div', *tables)
            set_html_tag_attributes(html_tag=div, attrs_dict=kwargs)
            s = etree.tostring(div, pretty_print=True).decode('utf-8')
            return Markup(s)  # Mark string as safe, since it's escaped by lxml
        else:
            return ''
    else:
        return document_elements
