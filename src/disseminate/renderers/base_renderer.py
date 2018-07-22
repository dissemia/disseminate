"""
Renderers for contexts.

A renderer is used to convert information and ASTs stored in a context dict into
a string for a particular target, like '.html' or '.tex'.
"""
import os.path

from ..context.utils import context_targets


#: The location of the templates directory relative to this directory
module_templates_relpath = '../templates'


def process_context_template(context):
    # Get the subclasses of the BaseRenderer
    renderer_clses = BaseRenderer.renderer_subclasses()
    renderer_cls = renderer_clses[0]

    # Create the template renderer.
    template = context.get('template', 'default/template')
    targets = context_targets(context)
    context['template_renderer'] = renderer_cls(context=context,
                                                template=template,
                                                targets=targets,
                                                module_only=False)

    equation_template = context.get('equation_template', 'default/eq')
    context['equation_renderer'] = renderer_cls(context=context,
                                                template=equation_template,
                                                targets=['.tex'],
                                                module_only=False)


class BaseRenderer(object):
    """The Base Renderer is an ABC that defines the API for renderers."""

    #: If True, only search the disseminate module for templates--not the
    #: project directories for the project being rendered
    module_only = None

    #: The base name for the template file
    template = None

    #: The targets (extensions) of the files to render to.
    targets = None

    #: The order for the renderer. If multiple renderers are available,
    #: The renderer with the lower order number will be used first.
    order = 1000

    _module_templates_abspath = None

    def __init__(self, context, template, targets, module_only=False):
        self.module_only = module_only
        self.template = template
        self.targets = targets

        # Set the paths for this renderer in the context
        self.set_context_paths(context)

    @property
    def mtime(self):
        """The last modification time for the renderer templates."""
        raise NotImplementedError

    @property
    def module_path(self):
        """The render path for the templates directory in the disseminate
        module."""

        if self._module_templates_abspath is None:
            # Get the path for the current file and navigate to the templates
            # subdirectory.
            current_path = os.path.split(__file__)[0]
            templates_path = os.path.join(current_path,
                                          module_templates_relpath)
            self._module_templates_abspath = os.path.abspath(templates_path)

        # Return an absolute path
        return self._module_templates_abspath

    @property
    def from_module(self):
        """Is the template loaded from the disseminate module?

        Templates may be loaded from other places like the user's src directory,
        in which case, this question would answer False.
        """
        raise NotImplementedError

    @classmethod
    def renderer_subclasses(cls):
        """An ordered list of BaseRenderer subclasses."""
        return sorted(cls.__subclasses__(), key=lambda r: r.order)

    def template_filepaths(self, target=None):
        """A list of the template absolute (render) file paths.

        Multiple template filepaths may be returned if a template was inherited
        from one of more parents. In this case, the parents are listed after
        the main template file.

        Parameters
        ----------
        target : str, optional
            Return templates for the given target (ex: '.html).
            If None is specified, a listing of templates for all targets is
            returned.

        Returns
        -------
        template_filenames : list of str
            A listing of the template filename as well as parent template
            filenames, if the template was inherited.
        """
        raise NotImplementedError

    def set_context_paths(self, context):
        """Add the paths for the used templates in the context's paths entry."""
        assert context.is_valid('paths')
        context_paths = context['paths']

        try:
            template_filepaths = self.template_filepaths()
            template_paths = [os.path.split(path)[0]
                              for path in template_filepaths]
        except NotImplementedError:
            template_paths = []

        for path in template_paths:
            if path in context_paths:
                continue
            context_paths.append(path)

    def load_context(self, context):
        pass

    def render(self, context, target):
        """Render the given context into a string for the given target."""
        raise NotImplementedError

    def is_available(self, target):
        """Is a template available for the given target?"""
        return False
