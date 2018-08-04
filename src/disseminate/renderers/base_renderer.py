"""
Renderers for contexts.

A renderer is used to convert information and ASTs stored in a context dict into
a string for a particular target, like '.html' or '.tex'.
"""
import pathlib

from ..context.utils import context_targets
from ..paths import SourcePath

#: The location of the templates directory relative to this directory
module_templates_relpath = '../templates'


def process_context_template(context):
    """Process the template entries in a given conext"""
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

    # Create the equation renderer.
    equation_template = context.get('equation_template', 'default/eq')
    context['equation_renderer'] = renderer_cls(context=context,
                                                template=equation_template,
                                                targets=['.tex'],
                                                module_only=False)


class BaseRenderer(object):
    """The Base Renderer is an ABC that defines the API for renderers.

    A renderer selects a template and is used to render documents, dependencies
    or webpages.

    Arguments
    ---------
    context : :obj:`disseminate.document.DocumentContext`
        A dict with values for the document.
    template : str
        The name or subpath of the template.
    targets : list of str
        The target extensions (ex: ['.html', '.tex']) of target documents.
        A template for each target should be available.
    module_only : bool, optional
        Only search the disseminate module for the template--i.e. do not use
        the user templates from the project directory.
    """

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

    @classmethod
    def renderer_subclasses(cls):
        """An ordered list of BaseRenderer subclasses."""
        return sorted(cls.__subclasses__(), key=lambda r: r.order)

    def __init__(self, context, template, targets, module_only=False):
        self.module_only = module_only
        self.template = template
        self.targets = targets

        # Set the paths for this renderer in the context
        self._set_context_paths(context)

    @property
    def mtime(self):
        """The last modification time for the renderer templates.

        Returns
        -------
        mtime : float or None
            The (largest) modification time for the templates.
            None is returned if an mtime could not be found.
        """
        raise NotImplementedError

    @property
    def module_path(self):
        """The render path for the templates directory in the disseminate
        module.

        Returns
        -------
        module_path : :obj:`pathlib.Path`
            The path for the templates directory in the disseminate module.
        """
        cls = self.__class__

        if cls._module_templates_abspath is None:
            # Get the path for the current file and navigate to the templates
            # subdirectory.
            module_file = pathlib.Path(__file__)
            module_path = module_file.parent
            templates_path = module_path / module_templates_relpath
            templates_path = SourcePath(project_root=templates_path.resolve())
            cls._module_templates_abspath = templates_path

        # Return an absolute path
        return cls._module_templates_abspath

    @property
    def from_module(self):
        """Is the template loaded from the disseminate module?

        Templates may be loaded from other places like the user's src directory,
        in which case, this question would answer False.

        Returns
        -------
        from_module : bool
            True, if the selected template is from the disseminate module.
            False, if the selected template is from the user's project.
        """
        raise NotImplementedError

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
        template_filenames : list of :obj:`pathlib.Path`
            A listing of the template filenames as well as parent template
            filenames, if the template was inherited.
        """
        raise NotImplementedError

    def is_available(self, target):
        """Is a template available for the given target?"""
        return False

    def render(self, target, context):
        """Render the given context into a string for the given target."""
        raise NotImplementedError

    def _add_dependencies(self, rendering, target, context):
        """Add dependencies for a rendered string."""
        assert context.is_valid('dependency_manager')
        dep_manager = context['dependency_manager']

        # See if there's a scrape method for the given target.
        # ex: 'scrape_html'
        method = getattr(dep_manager, 'scrape_' + target.strip('.'), None)
        if method is not None:
            deps = method(rendering, target, context)
            return deps
        return None

    def _set_context_paths(self, context):
        """Add the paths for the used templates in the context's paths entry."""
        assert context.is_valid('paths')
        context_paths = context['paths']

        try:
            template_filepaths = self.template_filepaths()
            template_paths = [template_filepath.parent
                              for template_filepath in template_filepaths]
        except NotImplementedError:
            template_paths = []

        for path in template_paths:
            if path in context_paths:
                continue
            context_paths.append(path)
