"""
A TargetBuilder for pdf files.
"""
from .target_builder import TargetBuilder
from .tex_builder import TexBuilder


class PdfBuilder(TargetBuilder):
    """A builder for Pdf files."""

    available = True
    priority = 1000
    infilepath_ext = '.dm'
    outfilepath_ext = '.pdf'

    add_parallel_builder = False
    add_render_builder = False

    _tex_builder = None
    _pdf_builder = None

    def __init__(self, env, context, parameters=None, outfilepath=None,
                 subbuilders=None, **kwargs):
        # Setup the subbuilders
        subbuilders = subbuilders or []

        # Find the tex_builder or create one.
        builders = context.setdefault('builders', dict())
        if '.tex' not in builders:
            tex_builder = TexBuilder(env=env, context=context, target='tex',
                                     **kwargs)

            builders['.tex'] = tex_builder
        else:
            tex_builder = builders['.tex']

        self._tex_builder = tex_builder
        subbuilders.append(tex_builder)

        # Now add a Pdf converter
        tex2pdf_cls = self.find_builder_cls(in_ext='.tex', out_ext='.pdf')
        tex2pdf = tex2pdf_cls(env=env, target='pdf', use_media=False,
                              use_cache=True, **kwargs)
        self._pdf_builder = tex2pdf
        subbuilders.append(tex2pdf)

        # And a copy builder
        copy_builder_cls = self.find_builder_cls(in_ext='.*', out_ext='.*')
        copy_builder = copy_builder_cls(env=env, target='pdf', use_cache=False,
                                        **kwargs)
        subbuilders.append(copy_builder)

        super().__init__(env=env, context=context, parameters=parameters,
                         outfilepath=outfilepath, subbuilders=subbuilders,
                         **kwargs)

        # Setup the paths
        tex2pdf.parameters = [tex_builder.outfilepath]

        copy_builder.parameters = [tex2pdf.outfilepath]
        copy_builder.outfilepath = self.outfilepath

    def add_build(self, parameters, outfilepath=None, context=None, **kwargs):
        return self._tex_builder.add_build(parameters=parameters,
                                           outfilepath=outfilepath,
                                           context=context, **kwargs)
