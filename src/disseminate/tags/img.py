"""
Image tags
"""
import pathlib

from .tag import Tag, TagError
from .utils import find_files, format_attribute_width
from ..formats import tex_cmd
from ..utils.string import hashtxt
from ..paths import SourcePath
from .. import settings


class Img(Tag):
    """The img tag for inserting images.

    Attributes
    ----------
    active : bool
        If True, the Tag can be used by the TagFactory.
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    img_filepath : str
        The path for the image.
    """

    active = True

    process_content = False
    process_typography = False

    html_name = 'img'
    filepath = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Move the contents to the filepath attribute
        if isinstance(content, list):
            contents = ''.join(content).strip()
        elif isinstance(content, pathlib.Path) and content.is_file():
            contents = content
        elif isinstance(content, str):
            # Get the filepath for the file
            filepaths = find_files(content, context)
            contents = (filepaths[0] if filepaths else None)
        else:
            contents = None
        self.content = ''

        if contents:
            self.filepath = contents
        else:
            msg = "An image path must be used with the img tag."
            raise TagError(msg)

    @property
    def mtime(self):
        """The last modification time of this tag and dependent files."""
        mtimes = [super().mtime]

        # Get the image file's modification time
        img_filepath = pathlib.Path(self.filepath)
        if img_filepath.is_file():
            mtime = img_filepath.stat().st_mtime
            mtimes.append(mtime)

        # Remove None values from mtimes
        mtimes = list(filter(bool, mtimes))

        # The mtime is the latest mtime of all the tags and labels
        return max(mtimes)

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Get the file dependency
        assert self.context.is_valid('dependency_manager')

        dep_manager = self.context['dependency_manager']

        # Raises MissingDependency if the file is not found
        deps = dep_manager.add_dependency(dep_filepath=self.filepath,
                                          target='.tex',
                                          context=self.context,
                                          attributes=self.attributes)
        dep = deps.pop()
        dest_filepath = dep.dest_filepath

        # Format the width
        attributes = attributes if attributes is not None else self.attributes
        attrs = format_attribute_width(attributes, target='.tex')

        return tex_cmd(cmd='includegraphics', attributes=attrs,
                       formatted_content=str(dest_filepath))

    def html_fmt(self, content=None, attributes=None, level=1):
        # Add the file dependency
        assert self.context.is_valid('dependency_manager')
        dep_manager = self.context['dependency_manager']

        # Raises MissingDependency if the file is not found
        deps = dep_manager.add_dependency(dep_filepath=self.filepath,
                                          target='.html',
                                          context=self.context,
                                          attributes=self.attributes)

        dep = deps.pop()
        url = dep.get_url(context=self.context)

        # Format the width and attributes
        attrs = self.attributes.copy() if attributes is None else attributes
        attrs = format_attribute_width(attrs, target='.html')
        attrs['src'] = url

        return super().html_fmt(attributes=attrs, level=level)


class RenderedImg(Img):
    """An img base class for saving and caching an image that needs to be
    rendered by an external program.

    .. note:: This class is not intended to be directly used as a tag. Rather,
              it is intended to be subclassed for other image types that need
              to be rendered first.

    Attributes
    ----------
    active : bool
        If True, the Tag can be used by the TagFactory.
    """

    active = False

    def __init__(self, name, content, attributes, context, render_target):
        if isinstance(content, list):
            content = ''.join(content).strip()
        else:
            content = content.strip()

        # Determine if contents is a file or code
        filepaths = find_files(content, context=context)
        if len(filepaths) == 1:
            # It's a file. Use it directly.
            content = filepaths[0]

        else:
            # Render the content, if needed.
            content = self.render_content(content=content, context=context)

            # Get the cache filepath from the dependency manager
            cache_filepath = self.cache_filepath(content=content,
                                                 context=context,
                                                 target=render_target)

            # Write the contents, if the cached file hasn't been written
            # already. Modification times do not need to be checked since the
            # hash guarantees that if the contents to render have changed, the
            # hash changes
            if not cache_filepath.is_file():
                # Create the needed directories
                cache_filepath.parent.mkdir(parents=True, exist_ok=True)

                # Write the file using
                cache_filepath.write_text(content)

            # Set the tag content to the newly saved file path. This path
            # should be relative to the .cache directory
            content = cache_filepath

        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

    def render_content(self, content, context):
        """Render the content.

        This function is called to render the content into a format that can
        be saved. By default, this function returns the content unaltered.
        Subclasses may override this function to implement their own renderers.
        """
        return content

    def cache_filepath(self, content, context, target):
        """Return a SourcePath for the file to render in the cached directory.
        """
        assert context.is_valid('dependency_manager', 'src_filepath')

        dep_manager = context['dependency_manager']
        src_filepath = context['src_filepath']

        # Get the cache path. ex: cache_path = {target_root}/'.cache'
        cache_path = dep_manager.cache_path

        # Construct the filename for the rendered image, including the
        # subpath.
        # ex: filename = 'chapter1/intro_231aef342.asy'
        content_hash = hashtxt(content)
        filepath = (str(src_filepath.subpath.with_suffix('')) + '_' +
                    content_hash + target)
        filepath = pathlib.Path(settings.media_path, filepath)

        # Construct a filepath in the cache directory. Create dirs as
        # needed.
        return SourcePath(project_root=cache_path, subpath=filepath)

    def template_kwargs(self):
        """Get the kwargs to pass to the template.

        Returns
        -------
        Union[None, dict]
            A dict or keyword arguments to pass to the template.
        """
        return dict()

    def template_args(self):
        """Get the args to pass to the template

        The args will be passed to the template as 'args', which can be iterated
        over.

        Returns
        -------
        Union[None, tuple]
            A tuple of arguments to pass to the template as the 'args'
            parameter/variable.
        """
        return tuple()
