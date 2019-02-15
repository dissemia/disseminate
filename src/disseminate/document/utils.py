import pathlib
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
    path : str or :obj:`pathlib.Path`, optional
        The path to search. By default, it is the current directory.
    document_extension : str, optional
        The source markup document extension. ex: '.dm'

    Returns
    -------
    project_paths : list
        A list of project paths as render paths.
    """
    # expand the user for the subpath directory
    path = pathlib.Path(path).expanduser()

    # Create a glob pattern to get all of the disseminate files in the path
    # and remove the filenames to retain the unique paths. Convert the paths
    # to strings so that they can be sorted more easily.
    glob_pattern = pathlib.Path('**', '*' + document_extension)
    paths = {str(p.parent) for p in path.glob(str(glob_pattern))}

    # Sort the paths by length so that root paths come up first. If two strings
    # have the same length, then they will be sorted alphabetically
    sorted_paths = sorted(paths, key=lambda i: (len(i), i), reverse=True)

    # Remove all entries that are subdirectories of the root project directories
    basepaths = set()

    while sorted_paths:
        basepath = sorted_paths.pop()
        basepaths.add(basepath)

        # Remove subdirectory
        sorted_paths = [i for i in sorted_paths if not i.startswith(basepath)]

    # Return the unique root paths as pathlib.Path objects.
    return [pathlib.Path(basepath) for basepath in basepaths]


def load_root_documents(path='',
                        document_extension=settings.document_extension):
    """Load the root documents from the project paths for the given path.

    Parameters
    ----------
    path : str or :obj:`pathlib.Path`, optional
        The path to search. By default, it is the current directory.
    document_extension : str, optional
        The source markup document extension. ex: '.dm'

    Returns
    -------
    root_documents : list
        A list of document objects (:obj:`disseminate.Document`).
    """
    documents = list()

    # Get the project paths and find the disseminate files in the root of these
    # paths
    project_paths = find_project_paths(path=path,
                                       document_extension=document_extension)

    for project_path in project_paths:
        # Find the paths for the root documents (non-recursive)
        glob_pattern = pathlib.Path('*' + document_extension)
        src_filepaths = project_path.glob(str(glob_pattern))

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
    # Strip leading '/' if present
    if isinstance(path, str):
        path = path if not path.startswith('/') else path[1:]

    # Make sure the path is a path object
    path = pathlib.Path(path)

    # See if the path is valid as is.
    if path.is_file():
        return path

    # Loop through the documents and see if a project_root or target_root
    # path is found.
    for document in documents:
        # Try constructing a render src_filepath
        src_filepath = document.project_root / path
        if src_filepath.is_file():
            return src_filepath

        # Check to see if the path can be constructed to a target_filepath
        targets = set()
        for subdoc in document.documents_list(only_subdocuments=False,
                                              recursive=True):
            targets = subdoc.targets
            for target, target_filepath in targets.items():
                if target_filepath.match(str(path)):
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

    for number, document in enumerate(documents, 1):
        context = document.context

        # Column 1: the document number
        kwargs = OrderedDict((('class', 'num'),))

        num = E('td', str(number))
        set_html_tag_attributes(html_tag=num, attrs_dict=kwargs)

        # Column 2: the source file
        src_filepath = document.src_filepath
        kwargs = OrderedDict((('class', 'src'),))
        src = E('td',
                E('a', str(src_filepath.subpath), href='/' + str(src_filepath)))
        set_html_tag_attributes(html_tag=src, attrs_dict=kwargs)

        # Column 3: target files
        kwargs = OrderedDict((('class', 'tgt'),))
        tgt_links = [E('a', target.strip('.'),
                       href=document.target_filepath(target).get_url(context))
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
        mtime = document.src_filepath.stat().st_mtime
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
