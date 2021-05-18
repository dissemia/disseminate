"""
Image tags
"""
import pathlib

from .tag import Tag, TagError
from .utils import xhtml_percentwidth, tex_percentwidth
from ..signals import signal
from ..paths.utils import find_files
from ..formats import tex_cmd

add_file = signal('add_file')


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
    in_ext : Optional[str]
        Used to correctly identify the builder to add if the contents need
        to be rendered first.
    img_filepath : str
        The path for the (source) image.
    """

    active = True

    process_content = False
    process_typography = False

    html_name = 'img'
    in_ext = None
    _infilepath = None
    _outfilepaths = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._outfilepaths = dict()

    def content_as_filepath(self, content=None, context=None):
        """Returns a filepath from the content, if it's a valid filepath,
        or returns None if it isn't.

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
        filepath : Union[:obj:`pathlib.Path`. None]
            The filepath, if found, or None if a valid filepath was not found.
        """
        content = content or self.content
        context = context or self.context

        # Move the contents to the infilepath attribute
        if isinstance(content, pathlib.Path) and content.is_file():
            return content
        elif isinstance(content, str):
            # Get the infilepath for the file
            filepaths = find_files(content, context)
            return filepaths[0] if filepaths else None

        return None

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
        # See if a cached path exists already. This can only be done if the
        # content, attributes and context aren't specified because the
        # values of this tag will be used for these parameters.
        if all(i is None for i in (content, attributes, context)):
            if target in self._outfilepaths:
                return self._outfilepaths[target]
            else:
                can_cache = True
        else:
            can_cache = False

        # Retrieve the unspecified arguments
        content = content or self.content
        attrs = attributes or self.attributes
        context = context or self.context

        # Prepare the parameters. Either their a filepath of the contents
        # or the contents themselves.
        content = (self.content_as_filepath(content=content,
                                            context=context) or
                   content)
        parameters = [content] + list(attrs.filter(target=target).totuple())

        # Use the content's filepath suffix as the in_ext, if a file has
        # been
        # specified, otherwise use this class's in_ext attribute
        in_ext = (content.suffix if isinstance(content, pathlib.Path) else
                  self.in_ext)
        outfilepaths = add_file.emit(parameters=parameters, context=context,
                                     in_ext=in_ext, target=target,
                                     use_cache=False)
        assert len(outfilepaths) == 1

        outfilepath = outfilepaths[0]

        # Cache the outfilepath, if possible
        if can_cache:
            self._outfilepaths[target] = outfilepath

        return outfilepath

    def tex_fmt(self, content=None, attributes=None, context=None, **kwargs):
        # Add the file dependency
        outfilepath = self.add_file(target='.tex', content=content,
                                    context=context, attributes=attributes)

        # Format the width
        attrs = attributes or self.attributes.copy()
        attrs = tex_percentwidth(attrs, target='.tex')

        # Get the filename for the file.
        base = outfilepath.with_suffix('')
        suffix = outfilepath.suffix

        # If the filename has unicode characters, you need to detokenize them
        # for latex to run correctly
        try:
            str(outfilepath).encode('ascii')
        except UnicodeEncodeError:
            base = tex_cmd(cmd='detokenize', formatted_content=str(base))

        # Wrap this filename in curly braces, which is needed for paths with
        # spaces and absolute paths
        dest_filepath = "{{{base}}}{suffix}".format(base=base, suffix=suffix)

        return tex_cmd(cmd='includegraphics', attributes=attrs,
                       formatted_content=str(dest_filepath))

    def html_fmt(self, content=None, attributes=None, context=None,
                 method='html', **kwargs):
        # Add the file dependency
        target = '.' + method if not method.startswith('.') else method
        outfilepath = self.add_file(target=target, content=content,
                                    context=context, attributes=attributes)
        url = outfilepath.get_url(context=self.context, target=target)

        # Format the width and attributes
        attrs = attributes or self.attributes.copy()
        attrs = xhtml_percentwidth(attrs, target=target)
        attrs['src'] = url

        return super().html_fmt(content='', attributes=attrs, method=method,
                                **kwargs)
