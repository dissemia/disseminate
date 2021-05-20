"""
A receiver to process headers in a context
"""
import regex
import pathlib

from ..signals import document_onload
from ...context import BaseContext
from ...context.utils import find_header_entries, load_from_string
from ...utils.list import uniq
from ... import settings


@document_onload.connect_via(order=1000)
def process_headers(context, **kwargs):
    """Process header strings for entries in a context by loading them into
    the context.

    Context information comes from the following sources:

    1. The document itself and its header file
    2. Additional headers from the template

    The information in (1) takes precedence over (2). For this reason, (1)
    should be loaded after (2), but (2) is specified by some entries, like
    renderers, template, targets, in (1), so (1) is pre-loaded before (2).
    """
    assert context.is_valid('paths')

    # 1. Load the context entries with headers
    # See which context entries have a header
    keys = find_header_entries(context)

    # Load the context from the document's header
    header_context = BaseContext()
    for key in keys:
        rest, d = load_from_string(context[key])

        # Replace the entry with the context removed
        context[key] = rest

        # Update the context
        header_context.match_update(d)

    # 2. Load the template paths and the 'context.txt' files
    #    First load the template paths for the template and any parent
    #    templates. The template_name may be different from the header_context
    #    than the one specified in this context.
    template_name = header_context.get('template') or context.get('template')
    template_paths = find_template_paths(template_name=template_name)

    for template_path in list(template_paths):
        template_paths += find_jinja2_parent_templates(template_path)
    template_paths = uniq(template_paths)

    # Next, find the additional context files and load their context values.
    # These are done in *reverse* order because the parent templates are
    # listed last and the child templates listed first. The child template
    # values take precedence.
    template_context = BaseContext()

    # Get the additional context filepaths in reverse order
    fps = find_additional_context_filepaths(template_paths[::-1])
    for context_filepath in fps:
        template_context.load(context_filepath.read_text())

    # Now load the template paths and context values
    paths = context['paths']
    paths[0:0] = template_paths  # insert at top of list w/o creating new list

    # Copy over entries in the template_context, first, then those from the
    # header_context. Since the header_context contains entries from the
    # headers of source files, these take precedence over template values
    context.match_update(template_context, overwrite=True)
    context.match_update(header_context, overwrite=True)


def find_template_paths(template_name):
    """Find template paths from a template name.

    Parameters
    ----------
    template_name : str
        The name of the template. ex: books/tufte

    Returns
    -------
    template_paths : List[:obj:`pathlib.Path`]
        A list of template path directories for the template.
    """
    paths = []

    # find template paths
    for template_basename in settings.module_template_paths:
        template_path = template_basename / template_name

        if template_path.is_dir() and template_path not in paths:
            # for template='books/tufte', for example
            # Add template plate to the front
            paths.insert(0, template_path)
        elif (template_path.parent.is_dir() and
              template_path.parent not in paths):
            # for template='default/template', for example
            paths.insert(0, template_path.parent)

    return uniq(paths)


_re_jinja2_extends = regex.compile(r'extends\s*[\"\']([^\'\"]+)[\"\']')


def find_jinja2_parent_templates(template_path):
    """Find additional templates from jinja2 template paths.

    Parameters
    ----------
    template_path : :obj:`pathlib.Path`
        The path for the directory of the child template.

    Returns
    -------
    template_paths : List[:obj:`pathlib.Path`]
        A list of template path directories for the parent templates.
    """
    # Find all template files
    template_files = template_path.glob('**/template*')

    # Find "extends" statements. This regex will find items
    # like {% extends "default/template.html" %}
    matches = [_re_jinja2_extends.search(tf.read_text())
               for tf in template_files]

    # Remove None enties
    matches = filter(bool, matches)  # remove None entries

    # Find the paths
    paths = []
    for match in matches:
        # Format the template name: Strip the template filename and
        # target directory
        # ex: 'default/xhtml/template.xhtml' -> 'default'
        template_name = match.group(1)
        template_name = pathlib.Path(template_name).parent.parent

        # Add the path as long as the above didn't return the current
        # directory, which is not a template
        if str(template_name) != '.':
            paths += find_template_paths(template_name)

    return uniq(paths)


def find_additional_context_filepaths(template_paths, context_filename=None):
    """Find additional context files (context.txt) for the given template path.

    Parameters
    ----------
    template_paths : List[:obj:`pathlib.Path`]
        The list of template directory paths to search for additional context
        files
    context_filename : Optional[str]
        The default filename for the additional context files in the template
        directories (ex: context.txt)

    Returns
    -------
    additional_context_paths : List[:obj:`pathlib.Path`]
        A list of filepaths for additional context files in the template
        directories.
    """
    context_filename = context_filename or settings.template_context_filename
    additional_context_filepaths = []

    for template_path in template_paths:
        context_filepath = template_path / context_filename
        if context_filepath.is_file():
            additional_context_filepaths.append(context_filepath)
            continue

        context_filepath = template_path.parent / context_filename
        if context_filepath.is_file():
            additional_context_filepaths.append(context_filepath)
            continue

    return uniq(additional_context_filepaths)
