"""
A CompositeBuilder for html files.
"""
from .target_builder import TargetBuilder
from .xhtml_builder import XHtmlBuilder
from ...paths import TargetPath
from ...utils.list import uniq
from ... import settings


class EpubBuilder(TargetBuilder):
    """A builder for epub files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.epub'

    only_root = True
    add_parallel_builder = False
    add_render_builder = False

    _xhtml_builder = None
    _epub_builder = None
    _render_toc_context = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the subbuilders
        self.create_subbuilders()

    def find_or_create_xhtml_builders(self, **kwargs):
        """Find or create the target XHtmlBuilder for all documents in the
        document tree."""
        # Get all documents in the document tree
        context = self.context
        env = self.env
        doc = context.document
        doc_list = doc.documents_list(only_subdocuments=False, recursive=True)

        xhtml_builders = []
        for doc in doc_list:
            builders = doc.context.setdefault('builders', dict())
            if '.xhtml' not in builders:
                xhtml_builder = XHtmlBuilder(env=env, context=doc.context,
                                             target='xhtml', **kwargs)

                builders['.xhtml'] = xhtml_builder
            else:
                xhtml_builder = builders['.xhtml']

            xhtml_builders.append(xhtml_builder)
        return xhtml_builders

    def xhtml_filepaths(self, xhtml_builders=None):
        """Return a flat list of xhtml, css, svg filepaths from the
        XHtmlBuilders"""
        # Find or create all of the xhtml builders for this document and
        # all subdocuments
        xhtml_builders = xhtml_builders or self.find_or_create_xhtml_builders()

        # Find all the xhtml filepaths for these xhtml_builders
        filepaths = [builder.outfilepath for builder in xhtml_builders]

        # Find all the xhtml filepaths for other dependencies
        for xhtml_builder in xhtml_builders:
            subbuilders = xhtml_builder._parallel_builder.subbuilders
            filepaths += [builder.outfilepath for builder in subbuilders]

        # Return filepaths for build xhtml files and other dependencies
        # created
        allowed_exts = set(settings.tracked_deps['.xhtml']) | {'.xhtml'}
        return uniq([filepath for filepath in filepaths
                     if filepath.suffix in allowed_exts])

    def has_toc_xhtml(self, xhtml_filepaths=None):
        """Evaluates whether there is a toc.xhtml file in the xhtml files."""
        xhtml_filepaths = xhtml_filepaths or self.xhtml_filepaths()
        return any(filepath.subpath == 'toc.xhtml'
                   for filepath in xhtml_filepaths)

    def create_toc_xhtml_builder(self, context=None,
                                 template_name='default/xhtml/toc.xhtml'):
        """Create a toc.xhtml file for the document.

        Parameters
        ----------
        context : :obj:`.document.DocumentContext`
            The document context for the document that owns this builder.
        outfilepath : Optional[:obj:`paths.TargetPath`]
            The outfilepath to use for the toc.xhtml
        template_name : Optional[str]
            The name of the template file to use in making the toc.
        """
        context = context or self.context
        cache_path = self.env.cache_path
        outfilepath = TargetPath(target_root=cache_path, target='xhtml',
                                 subpath='toc.xhtml')

        # Find the render builder class
        builder_cls = self.find_builder_cls(in_ext='.render')

        # Create a mock "toc" document for the toc_xhtml_builder.
        # This will require a new context (render_context), owned by this
        # builder so that the render builder can hold a weakref to it.
        render_context = context.filter(['toc', 'label_manager',
                                         'root_document', 'relative_links'])
        self._render_toc_context = render_context

        # Modify the new context and toc tag to mock a new toc document
        toc = render_context['toc'].copy()
        render_context['template'] = template_name
        render_context['toc'] = toc
        render_context['doc_id'] = 'toc.dm'

        toc.doc_id = 'toc.dm'
        toc.context = render_context

        # If no toc entries are present in the toc tag, modify the toc tag to
        # return entries to the documents in the document tree. This is because
        # epub docs require at least 1 reference
        if len(toc.get_labels()) == 0:
            toc.toc_kind = ('all', 'documents', 'expanded')

        builder = builder_cls(env=self.env, context=render_context,
                              outfilepath=outfilepath, render_ext='.xhtml',
                              use_media=False, use_cache=True, target='xhtml')
        return builder

    def create_subbuilders(self):
        """Create subbuilders needed by this builder"""
        # Get parameters needed to create builders
        env = self.env
        context = self.context

        # Reset this builder's subbuilders
        self.subbuilders.clear()

        # 1. Create the xhtml builders for all document files
        xhtml_builders = self.find_or_create_xhtml_builders()
        xhtml_filepaths = self.xhtml_filepaths(xhtml_builders=xhtml_builders)
        self.subbuilders += xhtml_builders

        # 2. Build the toc file, if needed
        if not self.has_toc_xhtml(xhtml_filepaths=xhtml_filepaths):
            toc_builder = self.create_toc_xhtml_builder(context=self.context)
            self.subbuilders.append(toc_builder)
            xhtml_filepaths.append(toc_builder.outfilepath)

        # 3. Create xhtml to epub builder
        xhtml2epub_cls = self.find_builder_cls(in_ext='.xhtml',
                                               out_ext='.epub')
        xhtml2epub = xhtml2epub_cls(env=env, parameters=xhtml_filepaths,
                                    context=context, target='epub',
                                    use_media=False, use_cache=True)
        self.subbuilders.append(xhtml2epub)

        # 4. Create a copy builder to be placed in the final epub directory
        copy_builder_cls = self.find_builder_cls(in_ext='.*', out_ext='.*')
        copy_builder = copy_builder_cls(env=env, target='epub',
                                        use_cache=False)
        self.subbuilders.append(copy_builder)

        # Setup the paths
        copy_builder.parameters = [xhtml2epub.outfilepath]
        copy_builder.outfilepath = self.outfilepath
