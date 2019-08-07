"""
Renderers for contexts.

A renderer is used to convert information and ASTs stored in a context dict into
a string for a particular target, like '.html' or '.tex'.
"""
from abc import ABC, abstractmethod

from ..utils.list import uniq
from .. import settings

#: The location of the templates directory relative to this directory
module_templates_relpath = '../templates'


class BaseRenderer(ABC):
    """The Base Renderer is an ABC that defines the API for renderers.

    A renderer selects a template and is used to render documents, dependencies
    or webpages.

    Arguments
    ---------
    context : :obj:`DocumentContext <.DocumentContext>`
        A dict with values for the document.
    template : str
        The name or subpath of the template.
        ex: 'default'
    module_only : Optional[bool]
        Only search the disseminate module for the template--i.e. do not use
        the user templates from the project directory.
    targets : Union[List[str], Tuple[Str]]
        If specified, use the given list of targets. Otherwise, use the
        targets specified in the document context.
        ex: ['.html', '.tex', '.txt']
    """

    _module_only = None
    _cached = None

    #: The base name for the template file
    template = None

    targets = None

    #: The order for the renderer. If multiple renderers are available,
    #: The renderer with the lower order number will be used first.
    order = 1000

    def __init__(self, context, template, module_only=None, targets=None):
        if module_only is None:
            module_only = settings.module_only
        self._cached = dict()

        self.module_only = module_only
        self.template = template

        # Set the template targets. Get the targets from the argument list, if
        # available, or the context, if the targets aren't specified.
        if targets is not None:
            self.targets = targets
        else:
            # Otherwise, try getting the targets from the context. A
            # DocumentContext is expected here, as it has an attributes
            # (targets) that properly formats the targets entry into a list of
            # strings with a preceeding '.'. ex: ['.html', '.tex']
            assert context.is_valid('targets')
            self.targets = context.targets

        # Reset the paths for this renderer in the context. This must be done
        # after the templates are loaded since the paths of the templates must
        # be used in setting the context paths
        self.add_context_paths(context=context)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return "{}({})".format(cls_name, self.template)

    @property
    def module_only(self):
        """Retrieve templates from the module/package only.

        When True, this is a safety feature as templates aren't escaped and a
        user-generated template could contain malicious code.
        """
        return (settings.module_only if self._module_only is None else
                self._module_only)

    @module_only.setter
    def module_only(self, value):
        self._module_only = value

    def is_available(self, target):
        """Is this renderer available for the given target?"""
        target = target if target.startswith('.') else '.' + target
        return target in {f.suffix for f in self.template_filepaths()}

    # TODO: use a caching decorator
    def paths(self):
        """The ordered list of final template paths (directories).

        Returns
        -------
        paths : List[:obj:`pathlib.Path`]
            The template directories.
        """
        if 'paths' not in self._cached:
            filepaths = self.template_filepaths()
            paths = []
            for template_filepath in filepaths:
                template_parent = template_filepath.parent
                if template_parent.is_dir():
                    paths.append(template_parent)
            self._cached['paths'] = uniq(paths)
        return self._cached['paths']

    @abstractmethod
    def template_filepaths(self):
        """The ordered list of template files.

        Returns
        -------
        paths : List[:obj:`pathlib.Path`]
            The template file paths.
        """
        pass

    # TODO: use a caching decorator
    def context_filepaths(self):
        """The ordered list of additional context files from templates.

        Returns
        -------
        paths : List[:obj:`pathlib.Path`]
            The file paths for additional context files from templates.
        """
        if 'context_filepaths' not in self._cached:
            context_files = []
            template_filepaths = self.template_filepaths

            # Construct the context filepaths from the template_filepaths
            for filepath in template_filepaths():
                # Construct a test context filename
                context_filepath = (filepath.parent /
                                    settings.template_context_filename)

                # See if the test context filename exists and add it to the list
                # of context_filepaths if it isn't in there already.
                if (context_filepath.is_file() and
                        context_filepath not in context_files):
                    context_files.append(context_filepath)

            self._cached['context_filepaths'] = context_files
        return self._cached['context_filepaths']

    @property
    def mtime(self):
        """The latest modification time for the renderer's templates.

        Returns
        -------
        mtime : Union[float, None]
            The modification time (if available) or None (if
            unavailable).
        """
        # Get all of the template files
        template_filepaths = self.template_filepaths()

        # Get all of the additional context files
        context_filepaths = self.context_filepaths()

        # Get the maximum modification time
        mtimes = [file.stat().st_mtime
                  for file in template_filepaths + context_filepaths]

        return max(mtimes) if len(mtimes) > 0 else None

    @abstractmethod
    def render(self, target, context):
        """Render the given context into a string for the given target.

        Parameters
        ----------
        target : str
            The target to render. ex: '.html'
        context : dict
            The dictionary of values to substitute in the template

        Returns
        -------
        rendered_string : str
            The rendered template string.
        """
        pass

    def add_context_paths(self, context, paths=None):
        """Add template paths to the context path entries.

        Parameters
        ----------
        context : :obj:`DocumentContext <.context.DocumentContext>`
            The context for the document.
        paths : List[:obj:`pathlib.Path`]
            The list of paths to add to the context paths.
        """
        context_paths = context.get('paths', None)
        paths = self.paths() if paths is None else paths

        if context_paths is not None and paths is not None:
            missing_paths = [path for path in paths
                             if path not in context_paths]

            # Add the missing paths to the front of the paths list.
            # We do this so that template directories are searched first
            context_paths[0:0] = missing_paths

    def add_dependencies(self, rendering, target, context):
        """Add dependencies for a rendered string.

        Parameters
        ----------
        rendering : str
            The rendered string to add dependencies for.
        target : str
            The target for the rendering. ex: '.html'
        context : :obj:`DocumentContext <.context.DocumentContext>`
            The context for the document.

        Returns
        -------
        processed_rendering : str
            The rendered string with dependency links replaced.
        """
        assert context.is_valid('dependency_manager')
        dep_manager = context['dependency_manager']

        # Keep track of the processed string of the rendering.
        processed_rendering = rendering

        # See if there's a scrape method for the given target.
        # ex: 'scrape_html'
        method = getattr(dep_manager, 'scrape_' + target.strip('.'), None)
        if method is not None:
            processed_rendering = method(processed_rendering, target, context)
        return processed_rendering
