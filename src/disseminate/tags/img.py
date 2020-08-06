"""
Image tags
"""
import pathlib

from .tag import Tag, TagError
from .utils import format_attribute_width
from ..paths.utils import find_files
from ..formats import tex_cmd


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

    def tex_fmt(self, content=None, attributes=None, context=None,
                mathmode=False, level=1):
        # Add the file dependency
        outfilepath = self.add_file(target='.tex', content=content,
                                    context=context, attributes=attributes)

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

    def html_fmt(self, content=None, attributes=None, context=None, level=1):
        # Add the file dependency
        outfilepath = self.add_file(target='.html', content=content,
                                    context=context, attributes=attributes)
        url = outfilepath.get_url(context=self.context)

        # Format the width and attributes
        attrs = self.attributes.copy() if attributes is None else attributes
        attrs = format_attribute_width(attrs, target='.html')
        attrs['src'] = url

        return super().html_fmt(attributes=attrs, level=level)


class RenderedImg(Img):
    """An img base class for saving and caching an image that needs to be
    rendered by an external program.

    A rendered image saves the contents of the tag into an infile, and the
    parent tag may convert this file to an outfile in the format needed
    by the document target format.

    .. note:: This class is not intended to be directly used as a tag. Rather,
              it is intended to be subclassed for other image types
              that need to be rendered first.

    Attributes
    ----------
    active : bool
        If True, the Tag can be used by the TagFactory.
    input_format : str
        The source format for the file to render. (ex: '.tex' or '.asy')
    """

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
                                           context=context,
                                           target=target,
                                           use_cache=False)

        # Set the produced file to the infilepath of this tag
        self._infilepath = builder.outfilepath
        return self._infilepath
