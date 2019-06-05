"""
View for the document listing tree.
"""
from datetime import datetime

from flask import render_template, abort
from jinja2 import TemplateNotFound

from .blueprints import editor
from ..projects import load_projects


def tree_to_dict(docs, level=1):
    """Convert the root documents into a list of dicts, suitable for rendering
    in the view.
    """
    doc_list = []

    for number, doc in enumerate(docs, 1):
        d = dict()

        # Set the number and level for the doc
        d['number'] = number
        d['level'] = level

        # Get metainformation and information on the source file
        d['title'] = doc.title
        d['src_filepath'] = doc.src_filepath
        d['project_root'] = doc.project_root

        # Get information on the targets
        targets = list(doc.targets.keys())  # ex: ['.html', '.pdf']
        target_links = [doc.target_filepath(target).get_url()
                        for target in targets]
        d['targets'] = {target: target_link for target, target_link in
                        zip(targets, target_links)}

        # Get information on the modification time for the source
        mtime = doc.src_filepath.stat().st_mtime
        d['date'] = datetime.fromtimestamp(mtime)

        # See if there are sub-documents to render as well
        # subdocuments is a dict with the src_filepath of the subdoc as a key
        # and the subdoc itself as a vlue
        subdocs = doc.subdocuments

        if subdocs is not None:
            d['subdocs'] = tree_to_dict(subdocs.values(), level=level + 1)

        doc_list.append(d)

    return doc_list


@editor.route('/')
@editor.route('/index.html')
@editor.route('/tree.html')
def render_tree():
    # Load the documents
    docs = load_projects()

    try:
        return render_template('server/tree.html', docs=tree_to_dict(docs))
    except TemplateNotFound:
        abort(404)
