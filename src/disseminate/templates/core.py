"""
Core functions for getting and rendering templates
"""
import os.path

import jinja2

from . import settings


environments = {}


def get_template(src_filepath, target,
                 template_basename=settings.default_basefilename,
                 module_only=False):
    """Fetch the best template for rendering a document.

    A template must implement a render method that takes kwargs to render
    the template.

    Parameters
    ----------
    src_filepath : str
        The directory and filename path of the document (source markup) file.
        This path will be searched first, the the function will traverse parent
        directories to find a suitable template.
    target : str
        The target extension to render. ex: ".html", ".tex"
    template_name : str, optional
        The base filename of the template file. ex: "template"
    module_only : bool, optional
        If specified, the template will be searched in disseminate's package
        only (not in the source paths). By default, this option is False.

    Returns
    -------
    template
        A template object that has a 'render' method to return a rendered
        template string. The render method accepts kwargs for variables in the
        template.
    """
    # Get the top path and see if an environment has already been created
    if module_only:
        top_dir = '__module__'
    else:
        top_dir = os.path.dirname(src_filepath)

    if top_dir in environments:
        env = environments[top_dir]
    else:
        fsl=None

        if module_only:
            # An environment hasn't been created yet. Make one.
            # Create a jinja2 FileSystemLoader that checks the directory of
            # src_filepath
            # and all parent directories.
            dir_tree = []

            parent_dir = top_dir
            while parent_dir != "":
                dir_tree.append(parent_dir)
                parent_dir = os.path.dirname(parent_dir)

            fsl = jinja2.FileSystemLoader(dir_tree)
        dl = jinja2.PackageLoader('disseminate', 'templates/template_files')

        if fsl is not None:
            cl = jinja2.ChoiceLoader([fsl, dl])
        else:
            cl = dl

        # Create the environment
        env = jinja2.Environment(loader=cl)
        environments[top_dir] = env

    # Now return the template from the environment
    target = target if target.startswith(".") else "." + target
    template_file = "".join((template_basename, target))
    default_file = "".join(('template', target))

    try:
        return env.select_template([template_file, default_file])
    except jinja2.TemplateNotFound:
        return None
