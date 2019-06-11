"""Utilities for the JinjaRenderer."""
import pathlib
from glob import glob

import jinja2.meta


def template_paths(loader):
    """Generate a list of all search paths for templates, given a Jinja2
    loader.

    Parameters
    ----------
    loader : Union[Type[:obj:`jinja2.BaseLoader`], \
        Type[:obj:`jinja2.Environment`]]
        The loader or environment to retrieve template paths from.

    Returns
    -------
    template_paths : List[:obj:`pathlib.Path`]
        The template paths (directories).
    """
    paths = []

    if hasattr(loader, 'loader'):
        # Process environment
        paths += template_paths(loader.loader)

    elif hasattr(loader, 'loaders'):
        # Process ChoiceLoader
        for loader in loader.loaders:
            paths += template_paths(loader)

    elif hasattr(loader, 'searchpath'):
        # Process FileSystemLoader
        paths += [pathlib.Path(p) for p in loader.searchpath]

    elif (hasattr(loader, 'provider') and
         hasattr(loader.provider, 'module_path')):
        # Process PackageLoader
        package_path = loader.provider.module_path  # ex: '/.../disseminate'
        submodule_path = loader.package_path  # ex: 'templates'

        # Create the final path
        path = pathlib.Path(package_path) / submodule_path
        paths.append(path)

    return paths


def filepaths_from_paths(template_paths, template_basename):
    """Find template filepaths given a list of template_paths and a
    template base name.

    .. note:: This function will not include parent templates for inherited
              templates.

    Parameters
    ----------
    template_paths : List[:obj:`pathlib.Path`]
        A list of template paths
    template_basename : str
        The base name of the template (without extension)
        ex: report/default or report/default/template

    Returns
    -------
    template_filepaths : List[:obj:`template_filepaths`]
        A list of template file paths.
    """
    # Append the template name to the template_paths
    base_paths = [base_path / template_basename for base_path in template_paths]

    template_filepaths = []

    for base_path in base_paths:
        # First see if there are template files directly
        # We use glob instead of the glob method of pathlib.Path objects
        # because the glob function works with partial filenames from
        # base_path.
        # ex: templates/default.*
        filepaths = [pathlib.Path(p)
                     for p in sorted(glob(str(base_path) + '.*'))]

        template_filepaths += filepaths

    return template_filepaths


def filepaths_from_template(template, environment):
    # Prepare a list of absolute paths (render paths) for the templates
    filenames = list()

    # Get the loader from the environment
    loader = environment.loader

    # Find the parent templates for the template
    # Get the template name
    name = template.name

    # Get the template's filename and add it to the filenames set
    filenames.append(pathlib.Path(template.filename))

    # Load the source code for the template using the loader
    source = loader.get_source(environment, name)

    # Produce a Jinja2 AST from the source
    ast = environment.parse(source)

    # Get a list of all parent template names from the AST
    parent_names = list(jinja2.meta.find_referenced_templates(ast))

    # Convert the parent names to template file paths (render paths)
    # This is done by loading the parent template objects.
    parent_templates = [environment.get_template(parent_name)
                        for parent_name in parent_names]

    # Run this function on those templates
    for parent_template in parent_templates:
        filenames += filepaths_from_template(parent_template, environment)

    return filenames
