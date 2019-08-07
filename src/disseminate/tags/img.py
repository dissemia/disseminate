"""
Image tags
"""
import pathlib

from .tag import Tag, TagError
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
    img_filepath = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)

        # Move the contents to the src_filpath attribute
        if isinstance(content, list):
            contents = ''.join(content).strip()
        elif isinstance(content, SourcePath):
            contents = content
        else:
            contents = self.content.strip()
        self.content = ''

        if contents:
            self.img_filepath = contents
        else:
            msg = "An image path must be used with the img tag."
            raise TagError(msg)

    def tex_fmt(self, content=None, mathmode=False, level=1):
        # Get the file dependency
        assert self.context.is_valid('dependency_manager')

        dep_manager = self.context['dependency_manager']

        # Raises MissingDependency if the file is not found
        deps = dep_manager.add_dependency(dep_filepath=self.img_filepath,
                                          target='.tex',
                                          context=self.context,
                                          attributes=self.attributes)
        dep = deps.pop()
        dest_filepath = dep.dest_filepath
        dest_subpath = dest_filepath.subpath

        return tex_cmd(cmd='includegraphics', attributes=self.attributes,
                       formatted_content=str(dest_subpath))

    def html_fmt(self, content=None, level=1):
        # Add the file dependency
        assert self.context.is_valid('dependency_manager')
        dep_manager = self.context['dependency_manager']

        # Raises MissingDependency if the file is not found
        deps = dep_manager.add_dependency(dep_filepath=self.img_filepath,
                                          target='.html',
                                          context=self.context,
                                          attributes=self.attributes)
        dep = deps.pop()
        url = dep.get_url(context=self.context)

        # Use the parent method to render the tag. However, the 'src' attribute
        # should be fixed first.

        self.attributes['src'] = url
        return super(Img, self).html_fmt(level=level)


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
        content_line = content.splitlines()[0]  # check filename in 1st line
        if pathlib.Path(content_line).is_file():
            # It's a file. Use it directly.
            pass
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
