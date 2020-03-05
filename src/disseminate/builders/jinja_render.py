"""
A builder that renders a string to a file.
"""
import pathlib
import logging

import jinja2

from .builder import Builder
from .. import settings


class JinjaRender(Builder):
    """A builder that renders a file using a (Jinja2) renderer.

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    infilepaths, args : Tuple[:obj:`.paths.SourcePath`]
        The filepaths for input files in the build
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.
    context : dict
        A context to use with the renderer.
    """

    action = 'render'
    priority = 1000
    active_requirements = ('priority',)

    rendered_string = None

    def __init__(self, env, context, template=None, **kwargs):
        super().__init__(env, **kwargs)

        # Get the template filepath to use with the renderer
        target = self.outfilepath.suffix
        template_filepath = (template or
                             context.get('template', 'default/template'))
        templates = [template_filepath + '/template' + target,
                     template_filepath + target]

        # Get the Jinja2 environment
        jinja_env = self.jinja_environment()

        # Retrieve the template
        template = jinja_env.get_or_select_template(templates)

        # Add the template filepaths to the infilepath dependencies.
        # These are added to the infilepaths so that if they are changed, the
        # decider can trigger a new build.
        filepaths = template_filepaths(template=template, environment=jinja_env)
        self.infilepaths += filepaths

        # Add the context filepaths to the infilepath dependencies
        filepaths = context_filepaths(filepaths)
        self.infilepaths += filepaths

        # Render the template and add it to the infilepath (so that it can be
        # used by the decider to decide whether a build is needed)
        self.rendered_string = template.render(**context)
        self.infilepaths.append(self.rendered_string)

    def jinja_environment(self):
        """The jinja environment."""
        if getattr(self.env, '_jinja_environment', None) is None:
            # Create the loaders
            dl = jinja2.PackageLoader('disseminate', 'templates')

            # Create the environment
            ae = jinja2.select_autoescape(['html', 'htm', 'xml'])
            env = jinja2.Environment(autoescape=ae, loader=dl,
                                     keep_trailing_newline=True)
            self.env._jinja_environment = env
        return self.env._jinja_environment

    @property
    def status(self):
        return "done" if not self.build_needed() else "ready"

    def build(self, complete=False):
        outfilepath = self.outfilepath
        logging.debug("Rendering to '{}'".format(outfilepath))
        outfilepath.write_text(self.rendered_string)

        self.build_needed(reset=True)  # reset build flag
        return self.status


# Utilities

def template_filepaths(template, environment):
    """Return a list of filepaths from a Jinja2 template object.

    Parameters
    ----------
    template : :obj:`jinja2.Template`
        The jinja2 template object to load filepaths for
    environment : :obj:`jinja2.Environment`
        The jinja2 environment object

    Returns
    -------
    filepaths : List[:obj:`pathlib.Path`]
        A list of paths.
    """
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
        filenames += template_filepaths(parent_template, environment)

    return filenames


def context_filepaths(template_filepaths):
    """Return a list of context modifier files (ex: context.txt) from template
    filepaths.

    Parameters
    ----------
    template_filepaths : List[:obj:`pathlib.Path`]
        A list of filepaths for templates.

    Returns
    -------
    filepaths : List[:obj:`pathlib.Path`]
        A list of paths.
    """
    filepaths = []
    # Construct the context filepaths from the template_filepaths
    for filepath in template_filepaths:
        # Construct a test context filename (ex: 'templates/context.txt')
        context_filepath = (filepath.parent /
                            settings.template_context_filename)

        # See if the test context filename exists and add it to the list
        # of context_filepaths if it isn't in there already.
        if (context_filepath.is_file() and
                context_filepath not in filepaths):
            filepaths.append(context_filepath)
    return filepaths
