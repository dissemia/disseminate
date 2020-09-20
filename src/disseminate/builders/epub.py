"""
Builders for EPUB files
"""
import zipfile
import pathlib
import uuid
from datetime import datetime, timezone

from .builder import Builder
from ..paths.utils import find_file
from ..utils.classes import weakattr
from ..utils.string import slugify


class XHtml2Epub(Builder):
    """Convert xhtml files to an epub v3 file.

    Parameters
    ----------
    parameters, args : Tuple[:obj:`pathlib.Path`, str, tuple, list]
        The input parameters (dependencies), including filepaths for xhtml
        files, for the build. The parameters must include a 'toc.xhtml' file
        for the Table of Contents.
    """

    available = True
    priority = 1000
    action = 'Build xhtml2epub'

    infilepath_ext = '.xhtml'
    outfilepath_ext = '.epub'

    context = weakattr()
    package_subdir = pathlib.Path('xhtml')  # dir in ebook to store content
    toc_filename = 'toc.xhtml'

    _render_context = None

    def __init__(self, env, context, subbuilders=None, **kwargs):
        # Setup the arguments
        assert context is not None
        subbuilders = subbuilders or []

        super().__init__(env, **kwargs)
        self.context = context

        # Check the necessary parameters
        # One of the file should have a toc.xhtml
        assert any(p.name == self.toc_filename for p in self.parameters
                   if hasattr(p, 'name')), "epub requires a toc.xhtml file"

    def create_opf_builder(self, template_name='default/xhtml/content'):
        """Create a render builder for the content.opf file.

        Parameters
        ----------
        template_name : Optional[str]
            The name of the template to use for the content.opf.
        """
        builder_cls = XHtml2Epub.find_builder_cls(in_ext='.render')

        # Setup a renderer for the content.opfs
        fps = [p for p in self.parameters if hasattr(p, 'suffix')]

        render_context = (self._render_context or
                          self.context.filter(['paths', 'title', 'date']))
        render_context['template'] = template_name
        render_context['xhtml_files'] = self.filepath_dict_list(fps, '.xhtml')
        render_context['svg_files'] = self.filepath_dict_list(fps, '.svg')
        render_context['css_files'] = self.filepath_dict_list(fps, '.css')

        # Add required entries, if not present
        now = datetime.now(timezone.utc).replace(microsecond=0)
        date_str = now.isoformat().replace("+00:00", "Z")
        render_context.setdefault('uuid', str(uuid.uuid4()).upper())
        render_context.setdefault('title', 'Default Title')
        render_context.setdefault('date', date_str)

        self._render_context = render_context

        # Set the outfilepath for the content.opf
        outfilepath = self.outfilepath
        outfilepath = outfilepath.use_subpath('content.opf')

        # Create the builder
        builder = builder_cls(env=self.env, context=render_context,
                              outfilepath=outfilepath, render_ext='.opf',
                              use_cache=True)
        return builder

    def filepath_dict_list(self, filepaths, suffix):
        """Create a list of dicts from the given filepaths"""
        rv = []
        for filepath in filepaths:
            if filepath.suffix != suffix:
                continue

            # Is the filepath a toc file?
            is_toc = filepath.name == self.toc_filename

            # Generate the subpath for the file, as this is the relative
            # path in the epub container
            subpath = str(filepath.subpath)

            # Generate the navigation identifier for the file
            id = slugify(subpath) if not is_toc else 'toc'

            rv.append({'id': id,
                       'subpath': subpath,
                       'is_toc': is_toc})
        return rv

    def build(self, complete=False):
        context = self.context
        root_path = pathlib.Path('.')  # Base path for zip file

        # Create the epub
        with zipfile.ZipFile(self.outfilepath, 'w',
                             compression=zipfile.ZIP_DEFLATED) as epub:
            # Add the mimetype file
            epub.writestr('mimetype',
                          "application/epub+zip".encode(),
                          zipfile.ZIP_STORED)

            # Find and add the container.xml file
            contain_file = find_file(pathlib.Path('META-INF') / 'container.xml',
                                     context=context)
            epub.write(contain_file,
                       arcname=root_path / 'META-INF' / 'container.xml')

            # Create a builder for the content.opf
            builder = self.create_opf_builder()
            assert builder.build(complete=True)
            arc_name = self.package_subdir / builder.outfilepath.subpath
            epub.write(builder.outfilepath, arcname=arc_name)

            # Add files listed in the parameters
            filepaths = self.infilepaths

            for filepath in filepaths:
                # Rework the filepath for the archive. Use the subpath, if
                # available
                arcname = (filepath.subpath if hasattr(filepath, 'subpath') else
                           filepath)

                # Place the content in the package subdir (ex: 'xhtml/')
                arcname = self.package_subdir / arcname

                # Write the content file to the zip file.
                epub.write(filepath, arcname=arcname)

        self.build_needed(reset=True)
        return 'done'
