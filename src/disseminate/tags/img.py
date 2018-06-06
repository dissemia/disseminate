"""
Image tags
"""
import os.path
import hashlib

from .core import Tag, TagError
from ..attributes import set_attribute, format_tex_attributes
from ..utils.file import mkdir_p
from ..templates import get_template
from .. import settings


class Img(Tag):
    """The img tag for inserting images."""

    active = True
    html_name = 'img'
    src_filepath = None
    dependency_manager = None

    def __init__(self, name, content, attributes, context):
        super(Img, self).__init__(name, content, attributes, context)

        # Move the contents to the src_filpath attribute
        if isinstance(content, list):
            contents = ''.join(content).strip()
        else:
            contents = self.content.strip()
        self.content = ''

        if contents:
            self.src_filepath = contents
        else:
            msg = "An image path must be used with the img tag."
            raise TagError(msg)

    def tex(self, level=1, mathmode=False, content=None):
        # Get the file dependency
        assert 'dependency_manager' in self.context

        deps = self.context['dependency_manager']
        document_src_filepath = (self.context['src_filepath']
                                 if 'src_filepath' in self.context else
                                 None)
        deps.add_file(targets=['.tex'], path=self.src_filepath,
                      document_src_filepath=document_src_filepath,
                      attributes=self.attributes)
        dep = deps.get_dependency(target='.tex',
                                  src_filepath=self.src_filepath)
        path = dep.dep_filepath

        # get the attributes for tex
        valid_attrs = settings.tex_valid_attributes.get('img', None)
        attrs_str = format_tex_attributes(self.attributes,
                                          attribute_names=valid_attrs)
        return "\\includegraphics" + attrs_str + "{{{}}}".format(path)

    def html(self, level=1, content=None):
        # Add the file dependency
        assert 'dependency_manager' in self.context

        deps = self.context['dependency_manager']
        document_src_filepath = (self.context['src_filepath']
                                 if 'src_filepath' in self.context else
                                 None)
        deps.add_file(targets=['.html'], path=self.src_filepath,
                      document_src_filepath=document_src_filepath,
                      attributes=self.attributes)
        dep = deps.get_dependency(target='.html',
                                  src_filepath=self.src_filepath)
        url = dep.url

        # Use the parent method to render the tag. However, the 'src' attribute
        # should be fixed first.

        self.attributes = set_attribute(self.attributes, ('src', url),
                                        method='r')
        return super(Img, self).html(level)


class RenderedImg(Img):
    """An img base class for saving and caching an image that needs to be
    rendered by an external program.

    .. note:: This class is not intended to be directly used as a tag. Rather,
              it is intended to be subclassed for other image types that need
              to be rendered first.

    Attributes
    ----------
    template : str, optional
        If specified, use this template to render the file. The contents of the
        tag will be passed as the 'body' variable.
    """

    active = False

    template = None

    def __init__(self, name, content, attributes, context, render_target,
                 template=None):
        self.template = template
        if isinstance(content, list):
            content = ''.join(content).strip()
        else:
            content = content.strip()

        # Determine if contents is a file or code
        if os.path.isfile(content):
            pass
        else:
            # Get the cache path from the dependency manager
            assert 'dependency_manager' in context
            deps = context['dependency_manager']

            # ex: cache_path = '.cache'
            cache_path = deps.cache_path()

            # Get the media_path. The temporary file will be stored in this
            # directory.
            # ex: media_path = '.cache/media'
            media_path = os.path.join(cache_path, settings.media_dir)

            # Get the doc_src_filepath and root_path to better organize the
            # temporary files in the final directories. This allows the
            # directory structure of the source file to be created in the
            # target
            doc_src_filepath = context.get('src_filepath', None)
            project_root = context.get('project_root', None)

            # Find the cache directory for the file to create
            # ex: cache_dir = '.cache/media/chapter1'
            if project_root and doc_src_filepath:
                doc_src_path = os.path.relpath(doc_src_filepath, project_root)
                doc_src_path = os.path.split(doc_src_path)[0]
                cache_dir = os.path.join(media_path,
                                         doc_src_path)
            else:
                cache_dir = media_path

            # Use a template, if specified
            if self.template:
                src_filepath = context.get('src_filepath', '')
                template = get_template(src_filepath=src_filepath,
                                        target='.tex',
                                        template_basename=self.template)

                # Get the kwargs and args to pass to the template
                kwargs = self.template_kwargs()
                kwargs = kwargs if kwargs is not None else dict()
                args = self.template_args()
                args = args if args is not None else tuple()
                kwargs['args'] = args

                content = template.render(body=content, **kwargs)

            # Construct the filename for the rendered image
            # ex: filename = 'chapter1_231aef342.asy'
            content_hash = hashlib.md5(content.encode("UTF-8")).hexdigest()[:10]
            if doc_src_filepath:
                doc_basefilename = os.path.split(doc_src_filepath)[1]
                filename = (os.path.splitext(doc_basefilename)[0] + '_' +
                            content_hash + render_target)
            else:
                filename = content_hash + render_target

            # Construct the final cache filepath
            # ex: cache_filepath='.cache/media/chapter1/chapter1_231aef342.asy'
            cache_filepath = os.path.join(cache_dir, filename)

            # write the contents, if needed
            if not os.path.isfile(cache_filepath):
                # Create the needed directories
                mkdir_p(cache_dir)

                # Write the file using
                with open(cache_filepath, 'w') as f:
                    f.write(content)

            # Set the tag content to the newly saved file path. This path
            # should be relative to the .cache directory
            content = os.path.relpath(cache_filepath, cache_path)

        super(RenderedImg, self).__init__(name, content, attributes, context)

    def template_kwargs(self):
        """Get the kwargs to pass to the template.

        Returns
        -------
        None or dict
            A dict or keyword arguments to pass to the template.
        """
        return None

    def template_args(self):
        """Get the args to pass to the template

        The args will be passed to the template as 'args', which can be iterated
        over.

        Returns
        -------
        None or tuple
            A tuple of arguments to pass to the template as the 'args'
            parameter/variable.
        """
        return None
