"""
The template manager.
"""
import os.path

import jinja2

from ..context.utils import context_targets
from .. import settings


def procress_context_template(context):
    ## Update context

    # Create the template renderer
    context['template_renderer'] = JinjaTemplateRenderer(context,
                                                         module_only=False)


class TemplateRenderer(object):

    #: Only search the disseminate module for templates--not the project
    #: directories for the project being rendered
    module_only = None

    #: The base name for the template file
    template = None

    def __init__(self, context, module_only=False):
        self.module_only = module_only
        self.template = context.get('template', 'default/template')

    def template_files(self):
        """A list of the template file (render) paths."""
        raise NotImplementedError


class JinjaTemplateRenderer(TemplateRenderer):
    """Manage templates and the rendering of files.

    Multiple template managers may be available for each project.
    """

    _jinja_templates = None
    _environment = None

    def __init__(self, context, module_only=False):
        super(JinjaTemplateRenderer, self).__init__(context, module_only)

        # Prepare the cached templates dict
        self._jinja_templates = dict()

        # Load the template environment
        # Get the src_path
        src_filepath = context.get('src_filepath', None)
        src_path = (os.path.dirname(src_filepath) if src_filepath is not None
                    else None)

        # Create the filesystem loader to search paths for the template
        fsl = None
        if not self.module_only and src_path is not None:
            # Create a jinja2 FileSystemLoader that checks the directory of
            # src_path
            # and all parent directories.
            dir_tree = []

            parent_dir = src_path
            while parent_dir != "" and parent_dir != "/":
                dir_tree.append(parent_dir)
                parent_dir = os.path.dirname(parent_dir)

            fsl = jinja2.FileSystemLoader(dir_tree)

        dl = jinja2.PackageLoader('disseminate', 'templates')
        cl = jinja2.ChoiceLoader([fsl, dl]) if fsl is not None else dl

        # Create the environment
        kwargs = {'block_start_string': settings.template_block_start,
                  'block_end_string': settings.template_block_end,
                  'variable_start_string': settings.template_variable_start,
                  'variable_end_string': settings.template_variable_end,
                  'comment_start_string': settings.template_comment_start,
                  'comment_end_string': settings.template_comment_end,
                  'keep_trailing_newline': True,
                  }

        ae = jinja2.select_autoescape(['html', 'htm', 'xml'])
        env = jinja2.Environment(autoescape=ae, loader=cl, **kwargs)
        self._environment = env

        # Load and cache the template objects
        self.load_templates(context=context)

    @property
    def mtime(self):
        # Get all of the template objects
        templates = self._jinja_templates.values()

        # Get all of the filenames for the templates
        filenames = [t.filename for t in templates]

        # Get the maximum modification time
        mtimes = [os.path.getmtime(filename) for filename in filenames]
        return max(mtimes) if len(mtimes) > 0 else None

    def render(self, context, target):
        # get the template
        template = self.get_template(target)
        return template.render(**context)

    def load_templates(self, context):
        """Loads all the Jinja2 template objects needed to render the targets
        specified in the context."""
        # Get the targets specified in the context
        targets = context_targets(context)

        # find templates that haven't been loaded yet
        missing_targets = targets - self._jinja_templates.keys()

        # Get the name of the template. This may or may not include the
        # actual name of the template file.
        template = self.template

        # Load missing templates
        for target in missing_targets:
            # Construct the template file name. The the template name may
            # include the the template file's base filename (without extension)
            # ex: template = 'books/tufte/template',
            #     template_file1 = 'books/tufte/template.html'
            template_file1 = "".join((template, target))

            # Or, it may just be a path. If it's a path, use 'template' as the
            # default base filename
            # ex: template = 'books/tufte'
            #     template_file2 = 'books/tufte/template.html'
            template_path = os.path.join(template, 'template')
            template_file2 = "".join((template_path, target))

            # Get the template environment
            env = self._environment

            # Load the template and cache it in the jinja_templates
            # May raise a jinja2.TemplateNotFound exception
            jinja_template = env.select_template([template_file1,
                                                  template_file2])
            self._jinja_templates[target] = jinja_template

    def get_template(self, target):
        """Retrieve the Jinja2 template object for the given target.

        Parameters
        ----------
        target : str
            The target (extension) for the template to retrieve. ex: '.html'

        Returns
        -------
        template : :obj:`jinja2.Template`
            The Jinja2 template object for the given target.

        Raises
        ------
        jinja2.TemplateNotFound
            Raised exception if the template file could not be found.
        """
        # Return the cached version, if one is available
        return self._jinja_templates.get(target, None)
