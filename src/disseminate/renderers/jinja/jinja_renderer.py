"""
Renderer using the Jinja2 template rendering system.
"""
import pathlib

import jinja2
import jinja2.meta

from .utils import filepaths_from_template
from ..base_renderer import BaseRenderer
from ... import settings


class JinjaRenderer(BaseRenderer):
    """Manage templates and the rendering of files.

    Multiple template managers may be available for each project.

    Attributes
    ----------
    jinja_templates : Dict[str, :obj:`jinja2.Template`]
        A dict with the target (key) and the loaded jinja2 template (value).
    environment : :obj:`jinja2.Environment`
        The jinja2 environment.
    """

    jinja_templates = None
    src_filepath = None
    _environment = None

    def __init__(self, context, template, module_only=None, targets=None):
        self.module_only = module_only  # needed by set_context_paths
        self.template = template

        # Prepare the cached templates dict
        self.jinja_templates = dict()

        # Set the src_filepath
        self.src_filepath = context.get('src_filepath', None)

        super().__init__(context=context, template=template,
                         module_only=module_only, targets=targets)

        # Load and cache the template objects. This is done after calling the
        # parent __init__ function since this function sets the 'template'
        # attribute needed by self.load_templates()
        self.load_templates()

    @property
    def environment(self):
        if getattr(self, '_environment', None) is None:
            # Setup the jinja2 loader and environment
            # Create the filesystem loader to search paths for the template
            fsl = None

            # Create a filesystem loader, if custom templates are allowed.
            if not self.module_only and self.src_filepath is not None:
                # Load the template environment
                src_filepath = self.src_filepath
                project_root = src_filepath.project_root
                src_path = src_filepath.parent

                # Create a jinja2 FileSystemLoader that checks the directory of
                # src_path and all parent directories up to the project root.
                dir_tree = []

                parent_dir = src_path
                while parent_dir != project_root and str(parent_dir) != "/":
                    dir_tree.append(str(parent_dir))
                    parent_dir = parent_dir.parent
                dir_tree.append(project_root)

                fsl = jinja2.FileSystemLoader(dir_tree)

            # Create the loaders
            dl = jinja2.PackageLoader('disseminate', 'templates')
            cl = jinja2.ChoiceLoader([fsl, dl]) if fsl is not None else dl

            # Create the environment
            kwargs = {'keep_trailing_newline': True,
                      }

            ae = jinja2.select_autoescape(['html', 'htm', 'xml'])
            env = jinja2.Environment(autoescape=ae, loader=cl, **kwargs)
            self._environment = env

        return self._environment

    # TODO: use a caching decorator
    def template_filepaths(self):
        if 'template_filepaths' not in self._cached:
            # Load the templates. The templates must be loaded and individually
            # checked because some templates may inherit from other templates,
            # and these should be added to the template_filepaths
            self.load_templates()

            # Get the filepaths for all templates. Sort these by the target
            # string.
            filepaths = []
            for target, template in sorted(self.jinja_templates.items()):
                filepaths += filepaths_from_template(template,
                                                     self.environment)
            self._cached['template_filepaths'] = filepaths
        return self._cached['template_filepaths']

    def load_templates(self):
        """Loads all the Jinja2 template objects needed to render the targets
        specified in the context."""

        # Get the targets for the template files
        targets = self.targets

        # Replace intermediary targets for compiled documents.
        # ex: 'pdf' targets, which need to be compiled, should be replaced
        # with their source format (.tex)
        targets = {settings.compiled_exts[t]
                   if t in settings.compiled_exts else t
                   for t in targets}

        # Get the loaded templates, and see which ones are stale and which are
        # missing. These are the targets that need to be loaded (again).
        templates_dict = self.jinja_templates

        stale_targets = {k for k, v in templates_dict.items()
                         if not v.is_up_to_date}
        missing_targets = targets - templates_dict.keys()
        load_targets = missing_targets | stale_targets

        # Load stale and missing templates
        for target in load_targets:
            # Construct the template file name. The the template name may
            # include the the template file's base filename (without extension)
            # ex: template = 'books/tufte/template',
            #     template_file1 = 'books/tufte/template.html'
            template_file1 = pathlib.Path(self.template).with_suffix(target)

            # Or, it may just be a path. If it's a path, use 'template' as the
            # default base filename
            # ex: template = 'books/tufte'
            #     template_file2 = 'books/tufte/template.html'
            template_path = pathlib.Path(self.template,
                                         settings.template_basename)
            template_file2 = template_path.with_suffix(target)

            # Get the template environment
            env = self.environment

            # Load the template and cache it in the jinja_templates
            # May raise a jinja2.TemplateNotFound exception
            jinja_template = env.select_template([str(template_file1),
                                                  str(template_file2)])
            templates_dict[target] = jinja_template

    def get_template(self, target, raise_error=True):
        """Retrieve the Jinja2 template object for the given target.

        Parameters
        ----------
        target : str
            The target (extension) for the template to retrieve. ex: '.html'
        raise_error : Optional[bool]
            If True (default), a TemplateNotFound exception is raised, if the
            template was not found.

        Returns
        -------
        template : :obj:`jinja2.Template`
            The Jinja2 template object for the given target.

        Raises
        ------
        jinja2.TemplateNotFound
            Raised exception if the template file could not be found.
        """
        self.load_templates()

        # Return the cached version, if one is available. If not raise an
        # exception
        template =  self.jinja_templates.get(target, None)

        if template is None and raise_error:
            template_name = self.template + target
            raise jinja2.exceptions.TemplateNotFound(name=template_name)
        else:
            return template

    def render(self, target, context):
        self.load_templates()

        # get the template and render
        template = self.get_template(target)
        rendering = template.render(**context)

        # add dependencies
        rendering = self.add_dependencies(rendering=rendering, target=target,
                                          context=context)

        return rendering
