"""
A builder that renders a string to a file.
"""
import pathlib
import logging

import jinja2
import jinja2.meta

from .builder import Builder
from .exceptions import BuildError
from .utils import generate_mock_parameters, generate_outfilepath
from ..paths import SourcePath
from ..paths.utils import find_file
from ..utils.list import uniq
from ..utils.classes import weakattr
from .. import settings


def run(template, context, outfilepath, target):
    """Run the command with the given arguments."""
    # rendered_string = asyncio.run(template.render_async(**context,
    #                               outfilepath=outfilepath, target=target))
    if 'target' in context:
        rendered_string = template.render(**context, outfilepath=outfilepath)
    else:
        rendered_string = template.render(**context, outfilepath=outfilepath,
                                          target=target)
    outfilepath.write_text(rendered_string)
    return outfilepath


@jinja2.pass_context
def rewrite_path(context, stub):
    """A Jinja2 filter for rewriting paths, like css paths.

    .. note:: This function will only modify the path if an existing file can
              be found in the target directory. If not, it will log an error
              and return the path unchanged. This means that the dependent
              .css (and other) files should have been copied to the target
              directory before rendering the template.

    .. note:: This function is not sped up from using a ThreadPoolExecutor,
              and implementing with a ProcessPoolExecutor gives problems
              with pickling objects.
    """
    # Strip leading slashes so that the stub is not an absolute path
    stub = stub.strip('/')

    # Find the file with respect to the outfilepath
    outfilepath = context['outfilepath']
    paths = [outfilepath.parent,  # the outfilepath directory
             outfilepath.use_subpath('')  # the target_root / target
             ]

    try:
        filepath = find_file(stub, context={'paths': paths})
    except FileNotFoundError:
        msg = "Could not find '{}' in the target directory"
        logging.error(msg.format(stub))
        return stub

    # Make it a relative path, if specified
    target = context['target']
    string = filepath.get_url(context=context, target=target)

    return str(string)


class JinjaRender(Builder):
    """A builder that renders a file using Jinja2.

    .. note:: The JinjaRender should not render the template until the build
              step to make sure the document and context are properly loaded
              first.

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
    scan_parameters_on_init = False  # Scan after all parameters are loaded

    context = weakattr()

    infilepath_ext = '.render'  # dummy extension for find_builder_cls

    render_ext = None

    def __init__(self, env, context, render_ext=None, **kwargs):
        super().__init__(env, **kwargs)

        # Checks
        assert render_ext or self.outfilepath, ("Either a render_ext or an "
                                                "outfilepath must be "
                                                "specified")
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
                                     keep_trailing_newline=True,)
            env.filters['rewrite_path'] = rewrite_path

            self.env._jinja_environment = env
        return self.env._jinja_environment

    def template(self):
        """Retrieve the template from the context"""
        context = self.context
        # Get the template filepath and convert to a pathlib.Path
        template_filepath = context.get('template', 'default')
        template_filepath = pathlib.Path(template_filepath)

        # get the target extension without a period
        target = self.render_ext.strip('.')

        # create the list of template paths to search
        # path1. ex: 'default '/ 'html' / 'template' '.html'
        path1 = template_filepath / target / 'template'
        path1 = path1.with_suffix('.' + target)

        # path2. ex: 'default/xhtml/toc' / '.xhtml
        path2 = template_filepath.with_suffix('.' + target)

        # path3: ex: 'default/xhtml/toc.xhtml'
        path3 = template_filepath

        templates = list(map(str, [path1, path2, path3]))
        # Get the Jinja2 environment
        jinja_env = self.jinja_environment()

        # Retrieve the template
        template = jinja_env.get_or_select_template(templates)
        return template

    @property
    def parameters(self):
        parameters = list(self._parameters) if self._parameters else []
        context = self.context

        # Render the string and add it (as well as dependent template files)
        # to the list of returned input parameters
        if context is not None:
            # Retrieve the template
            jinja_env = self.jinja_environment()
            template = self.template()

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

            # add hashes (from tags) to context values
            parameters += sorted(v.hash for v in context.values()
                                 if hasattr(v, 'hash') and v.hash is not None)

        return uniq(parameters)

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

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

    # Note: Enable this function and comment out the build to run the
    # render in the thread pool. This slows the run, however, by about 30-40%
    # def run_cmd(self, *args):
    #     if self.future is None:
    #         template = self.template()
    #         outfilepath = self.outfilepath
    #
    #         logging.debug("Rendering '{}' with Jinja2 "
    #                       "'{}'".format(outfilepath, template))
    #         future = executor.submit(run, template=template,
    #                                  context=self.context,
    #                                  outfilepath=outfilepath,
    #                                  target=self.render_ext)
    #         self.future = future

    def build(self, complete=False):
        template = self.template()
        context = self.context
        outfilepath = self.outfilepath

        logging.debug("Rendering '{}' with Jinja2 "
                      "'{}'".format(outfilepath, template))
        if 'target' in context:
            rendered_string = template.render(**context,
                                              outfilepath=outfilepath)
        else:
            rendered_string = template.render(**context,
                                              target=self.render_ext,
                                              outfilepath=outfilepath)

        outfilepath.write_text(rendered_string)
        self.build_needed(reset=True)
        return self.status

    @staticmethod
    def runtime_success(future):
        """Test whether a future from a subprocess is successful."""
        return future.result().exists()  # outfilepath exists

    @staticmethod
    def runtime_error(future, error_msg=None, raise_error=True):
        """Raise an error from a future working with subprocess"""
        outfilepath = future.result()

        if error_msg is None:
            error_msg = ("The render of  '{}' was "
                         "unsuccessful.".format(outfilepath))
        if raise_error:
            e = BuildError(error_msg)
            raise e
        else:
            logging.warning(error_msg)


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
        # Construct a test context filename1
        # ex: filepath: 'templates/default/html'
        #     context_fp: templates/default/context.txt
        context_fp = SourcePath(project_root=filepath.parent.parent,
                                subpath=settings.template_context_filename)

        # See if the test context filename exists and add it to the list
        # of context_filepaths if it isn't in there already.
        if (context_fp.is_file() and
                context_fp not in filepaths):
            filepaths.append(context_fp)
    return filepaths
