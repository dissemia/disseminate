"""
A builder that renders a string to a file.
"""
import pathlib
import logging

import jinja2, jinja2.meta

from .builder import Builder
from .utils import generate_mock_parameters, generate_outfilepath
from ..paths import SourcePath
from ..utils.list import uniq
from ..utils.classes import weakattr
from .. import settings


class JinjaRender(Builder):
    """A builder that renders a file using Jinja2.

    Parameters
    ----------
    env: :obj:`.builders.Environment`
        The build environment
    parameters, args : Tuple[:obj:`.paths.SourcePath`, str, tuple, list]
        The input parameters (dependencies), including filepaths, for the build
    outfilepath : Optional[:obj:`.paths.TargetPath`]
        If specified, the path for the output file.
    context : dict
        A context to use with the renderer.
    render_ext : str
        The extension for the rendered file. Either this or the outfilepath
        must be specified. ex: '.tex'
    """

    available = True
    action = 'render'
    priority = 1000
    active_requirements = ('priority',)
    scan_parameters = False  # This is done after all parameters are loaded

    context = weakattr()

    infilepath_ext = '.render'  # dummy extension for find_builder_cls

    render_ext = None
    rendered_string = None

    def __init__(self, env, context, render_ext=None, **kwargs):
        super().__init__(env, **kwargs)

        # Checks
        assert render_ext or self.outfilepath, ("Either a render_ext or an "
                                                "outfilepath must be specified")
        self.render_ext = render_ext or self.outfilepath.suffix
        self.context = context

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

    @property
    def parameters(self):
        parameters = list(self._parameters) if self._parameters else []
        context = self.context

        # Render the string and add it (as well as dependent template files)
        # to the list of returned input parameters
        if context is not None:
            # Get the template filepath to use with the renderer
            target = self.render_ext

            template_filepath = context.get('template', 'default/template')
            templates = [template_filepath + '/template' + target,
                         template_filepath + target]

            # Get the Jinja2 environment
            jinja_env = self.jinja_environment()

            # Retrieve the template
            template = jinja_env.get_or_select_template(templates)

            # Add the template filepaths to the infilepath dependencies.
            # These are added to the parameters so that if they are changed,
            # the decider can trigger a new build.
            filepaths = template_filepaths(template=template,
                                           environment=jinja_env)
            parameters += filepaths

            # Add the context filepaths to the infilepath dependencies
            filepaths = context_filepaths(filepaths)
            parameters += filepaths

            # Scan for additional dependencies
            parameters += self.env.scanner.scan(parameters=parameters)

            # Render the template and add it to the infilepath (so that it can
            # be used by the decider to decide whether a build is needed)
            self.rendered_string = template.render(**context)
            parameters.append(self.rendered_string)

        return uniq(parameters)

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def build(self, complete=False):
        outfilepath = self.outfilepath
        logging.debug("Rendering to '{}'".format(outfilepath))
        outfilepath.write_text(self.rendered_string)

        self.build_needed(reset=True)  # reset build flag
        return self.status

    @property
    def outfilepath(self):
        outfilepath = self._outfilepath

        if outfilepath is None:
            parameters = self.parameters

            if parameters:
                # Create an a mock infilepath with hash from the parameters
                sourcepath = generate_mock_parameters(env=self.env,
                                                      context=self.context,
                                                      parameters=parameters,
                                                      ext='.render')

                # Generate an outfilepath from the mock parameters
                outfilepath = generate_outfilepath(env=self.env,
                                                   parameters=sourcepath,
                                                   append=self.outfilepath_ext,
                                                   ext=self.render_ext,
                                                   target=self.target,
                                                   use_cache=self.use_cache,
                                                   use_media=self.use_media)

        # Make sure the outfilepath directory exists
        if outfilepath and not outfilepath.parent.is_dir():
            outfilepath.parent.mkdir(parents=True, exist_ok=True)

        return outfilepath

    @outfilepath.setter
    def outfilepath(self, value):
        self._outfilepath = value


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
    template_filename = pathlib.Path(template.filename)
    filenames.append(SourcePath(project_root=template_filename.parent,
                                subpath=template_filename.name))

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
        context_fp = SourcePath(project_root=filepath.parent,
                                subpath=settings.template_context_filename)

        # See if the test context filename exists and add it to the list
        # of context_filepaths if it isn't in there already.
        if (context_fp.is_file() and
                context_fp not in filepaths):
            filepaths.append(context_fp)
    return filepaths
