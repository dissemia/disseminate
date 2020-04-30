"""
Image tags
"""
import pathlib

from .tag import Tag, TagError
from .utils import format_attribute_width
from ..paths.utils import find_files
from ..formats import tex_cmd
from ..utils.string import hashtxt
from ..paths import SourcePath
from .. import settings


class ImgFileNotFound(TagError):
    """The image file was not found."""
    pass


class Img(Tag):
    """The img tag for inserting images.

    When rendering to a target document format, this tag may use a converter,
    the attributes and context of this tag to convert the infile to an outfile
    in a needed format.

    Attributes
    ----------
    active : bool
        If True, the Tag can be used by the TagFactory.
    html_name : str
        If specified, use this name when rendering the tag to html. Otherwise,
        use name.
    img_filepath : str
        The path for the (source) image.
    """

    active = True

    process_content = False
    process_typography = False

    html_name = 'img'
    _infilepath = None
    _outfilepaths = None

    def __init__(self, name, content, attributes, context):
        super().__init__(name=name, content=content, attributes=attributes,
                         context=context)
        self._outfilepaths = dict()

    @property
    def mtime(self):
        """The last modification time of this tag and dependent files."""
        mtimes = [super().mtime]

        # Get the modification times of files
        img_filepath = pathlib.Path(self.infilepath())
        if img_filepath.is_file():
            mtime = img_filepath.stat().st_mtime
            mtimes.append(mtime)

        # Remove None values from mtimes
        mtimes = list(filter(bool, mtimes))

        # The mtime is the latest mtime of all the tags and labels
        return max(mtimes)

    def infilepath(self, content=None, context=None):
        """The infilepath for the image for the given document target.

        The infile may be converted to an outfile for the target document
        format.

        Parameters
        ----------
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.tag.Tag>`], :obj:`Tag <.tag.Tag>`]]
            The contents of the tag. It can either be a string, a tag or a list
            of strings, tags and lists.
        context : Optional[:obj:`Type[BaseContext] <.BaseContext>`]
            The context with values for the document.

        Returns
        -------
        infilepath : str
            The infilepath for the image source file.

        Raises
        ------
        ImgFileNotFound
            Raises an ImgFileNotFound exception if a filepath couldn't be
            found in the tag contents.
        """
        if self._infilepath is not None:
            return self._infilepath

        # Retrieve unspecified parameters
        content = content or self.content
        context = context or self.context

        # Move the contents to the infilepath attribute
        if isinstance(content, list):
            contents = ''.join(content).strip()
        elif isinstance(content, pathlib.Path) and content.is_file():
            contents = content
        elif isinstance(content, str):
            # Get the infilepath for the file
            filepaths = find_files(content, context)
            contents = filepaths[0] if filepaths else None
        else:
            contents = None

        if contents is None:
            msg = "An image path '{}' could not be found.".format(content)
            raise ImgFileNotFound(msg)

        # Convert the file to the format needed by target
        self._infilepath = contents

        return self._infilepath

    def add_file(self, target, content=None, attributes=None, context=None):
        """Convert and add the file dependency for the specified document
        target.

        Parameters
        ----------
        target : str
            The document target format. ex: '.html', '.tex'
        content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
            <.tag.Tag>`], :obj:`Tag <.tag.Tag>`]]
            The contents of the tag. It can either be a string, a tag or a list
            of strings, tags and lists.
        attributes : Optional[Union[str, \
            :obj:`Attributes <.attributes.Attributes>`]]
            The attributes of the tag.
        context : Optional[:obj:`Type[BaseContext] <.BaseContext>`]
            The context with values for the document.

        Returns
        -------
        outfilepath : :obj:`.paths.TargetPath`
            The filepath for the file in the target document directory.

        Raises
        ------
        ImgFileNotFound
            Raises an ImgFileNotFound exception if a filepath couldn't be
            found in the tag contents.
        BuildError
            If a builder could not be found for the builder
        """
        # See if a cached version is available
        if target in self._outfilepaths:
            return self._outfilepaths[target]

        # If not get the outfilepath for the given document target
        assert self.context.is_valid('builders')

        # Retrieve the unspecified arguments
        target = target if target.startswith('.') else '.' + target
        content = content or self.content
        attrs = attributes or self.attributes
        context = context or self.context

        # Retrieve builder
        target_builder = self.context.get('builders', dict()).get(target)
        assert target_builder, ("A target builder for '{}' is needed in the "
                                "document context")

        # Raises ImgNotFound if the file is not found
        parameters = ([self.infilepath(content=content)] +
                      list(attrs.filter(target=target).totuple()))
        build = target_builder.add_build(parameters=parameters, context=context)

        self._outfilepaths[target] = build.outfilepath
        return self._outfilepaths[target]

    def tex_fmt(self, content=None, attributes=None, mathmode=False, level=1):
        # Add the file dependency
        outfilepath = self.add_file(target='.tex', content=content,
                                    attributes=attributes)

        # Format the width
        attributes = attributes or self.attributes
        attrs = format_attribute_width(attributes, target='.tex')

        # Get the filename for the file. Wrap this filename in curly braces
        # in case the filename includes special characters
        base = outfilepath.with_suffix('')
        suffix = outfilepath.suffix
        dest_filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

        return tex_cmd(cmd='includegraphics', attributes=attrs,
                       formatted_content=str(dest_filepath))

    def html_fmt(self, content=None, attributes=None, level=1):
        # Add the file dependency
        outfilepath = self.add_file(target='.html', content=content,
                                    attributes=attributes)
        url = outfilepath.get_url(context=self.context)

        # Format the width and attributes
        attrs = self.attributes.copy() if attributes is None else attributes
        attrs = format_attribute_width(attrs, target='.html')
        attrs['src'] = url

        return super().html_fmt(attributes=attrs, level=level)


class RenderedImg(Img):

    in_ext = None

    def add_file(self, target, content=None, attributes=None, context=None):
        # Return a cached version, if available
        if self._infilepath is not None:
            return self._infilepath

        # First, try to see if there are filepaths in the content
        try:
            return super().add_file(target=target, content=content,
                                    attributes=attributes, context=context)
        except ImgFileNotFound:
            pass

        # At this stage, a file couldn't be found in the contents. Try saving
        # them. Check that the in_ext and out_ext are set
        assert isinstance(self.in_ext, str)

        # Otherwise, try saving the contents to a temp file. Retrieve builder
        target_builder = self.context.get('builders', dict()).get(target)
        assert target_builder, ("A target builder for '{}' is needed in the "
                                "document context")

        # Setup the builder
        content = content or self.content
        attrs = attributes or self.attributes
        parameters = [content] + list(attrs.filter(target=target).totuple())

        builder = target_builder.add_build(parameters=parameters,
                                           in_ext=self.in_ext,
                                           target=target)

        # Set the produced file to the infilepath of this tag
        self._infilepath = builder.outfilepath
        return self._infilepath

# class RenderedImg(Img):
#     """An img base class for saving and caching an image that needs to be
#     rendered by an external program.
#
#     A rendered image saves the contents of the tag into an infile, and the
#     parent tag may convert this file to an outfile in the format needed by the
#     document target format.
#
#     .. note:: This class is not intended to be directly used as a tag. Rather,
#               it is intended to be subclassed for other image types that need
#               to be rendered first.
#
#     Attributes
#     ----------
#     active : bool
#         If True, the Tag can be used by the TagFactory.
#     input_format : str
#         The source format for the file to render. (ex: '.tex' or '.asy')
#     """
#
#     active = False
#     input_format = None
#
#     def __init__(self, name, content, attributes, context):
#         # Make sure a format is specified to save to so that the final image
#         # can be rendered.
#         assert (self.input_format is not None and
#                 self.input_format.startswith('.')), ("RenderImage needs a "
#                                                      "format to save to")
#
#         # Strip extra space on the edges so that the hash can be more consistent
#         if isinstance(content, str):
#             content = content.strip()
#
#         super().__init__(name=name, content=content, attributes=attributes,
#                          context=context)
#
#     def infilepath(self, content=None, context=None):
#         """The image infilepath for the rendered image"""
#         if self._filepath is not None:
#             return self._filepath
#
#         # Retrieve unspecified arguments and setuo
#         context = context or self.context
#
#         # Determine if contents is a file or code
#         filepaths = find_files(string=content or self.content,
#                                context=context)
#         if len(filepaths) == 1:
#             # It's a file. Use it directly.
#             self._filepath = filepaths[0]
#
#         else:
#             # Get the cache infilepath from the dependency manager
#             cache_filepath = self.write_infile(content=content,
#                                                context=context)
#
#             # Set the tag content to the newly saved file path. This path
#             # should be relative to the .cache directory
#             self._filepath = cache_filepath
#
#         return self._filepath
#
#     def write_infile(self, content=None, context=None):
#         """Save the tag contents to an input file to be rendered, and
#         return  a SourcePath for the input file (in the self.input_format).
#
#         This function will do the following:
#         1. input_path. Generate a temporary filename and path (infilepath) to
#            write to using context and self.input_format.
#         2. write content. Use prepare_content to generate the content to write
#            to the input_path.
#         3. Return the written input_path.
#
#         Parameters
#         ----------
#         content : Optional[Union[str, List[Union[str, list, :obj:`Tag \
#         <disseminate.tags.tag.Tag>`], :obj:`Tag <disseminate.tags.tag.Tag>`]]
#             The contents of the tag. It can either be a string, a tag or a list
#             of strings, tags and lists.
#         context : Optional[:obj:`Type[BaseContext] <.BaseContext>`]
#             The context with values for the document.
#
#         Returns
#         -------
#         input_filepath : :obj:`.paths.SourcePath`
#             The infilepath for the saved input file to render.
#         """
#         # Retrieve unspecified arguments
#         context = context or self.context
#         content = content or self.prepare_content(content=content,
#                                                   context=context)
#
#         assert context.is_valid('dependency_manager', 'src_filepath')
#
#         dep_manager = context['dependency_manager']
#         src_filepath = context['src_filepath']
#
#         # Get the cache path. ex: cache_path = {target_root}/'.cache'
#         cache_path = dep_manager.cache_path
#
#         # Construct the filename for the rendered image, including the
#         # subpath.
#         # ex: filename = 'chapter1/intro_231aef342.asy'
#         content_hash = hashtxt(content)
#         filepath = (str(src_filepath.subpath.with_suffix('')) + '_' +
#                     content_hash + self.input_format)
#         filepath = pathlib.Path(settings.media_path, filepath)
#
#         # Construct a infilepath in the cache directory. Create dirs as
#         # needed.
#         input_filepath = SourcePath(project_root=cache_path, subpath=filepath)
#
#         # Save the contents of this tag to that file
#         # Write the contents, if the cached file hasn't been written
#         # already. Modification times do not need to be checked since the
#         # hash guarantees that if the contents to render have changed, the
#         # hash changes
#         # Render the content, if needed.
#         content = self.prepare_content(content=content, context=context)
#
#         if not input_filepath.is_file():
#             # Create the needed directories
#             input_filepath.parent.mkdir(parents=True, exist_ok=True)
#
#             # Write the file using
#             input_filepath.write_text(content)
#
#         return input_filepath
#
#     def prepare_content(self, content=None, context=None):
#         """Prepare the content to save in the input file to be rendered.
#
#         This function should prepare content from the tag's content into a
#         string in the format of self.input_format.
#         """
#         return content or self.content
#
#     # def template_kwargs(self):
#     #     """Get the kwargs to pass to the template.
#     #
#     #     Returns
#     #     -------
#     #     Union[None, dict]
#     #         A dict or keyword arguments to pass to the template.
#     #     """
#     #     return dict()
#     #
#     # def template_args(self):
#     #     """Get the args to pass to the template
#     #
#     #     The args will be passed to the template as 'args', which can be iterated
#     #     over.
#     #
#     #     Returns
#     #     -------
#     #     Union[None, tuple]
#     #         A tuple of arguments to pass to the template as the 'args'
#     #         parameter/variable.
#     #     """
#     #     return tuple()
