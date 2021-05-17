import pathlib

from .utils.types import IntPositionalValue, StringPositionalValue
from .__version__ import __version__


#: Document Defaults
#: -----------------

#: The default extension of markup files
document_extension = '.dm'

#: The default directory for source files
document_src_directory = 'src'

#: Maximum file size
document_max_size = 204800  # 200kB

#: If True, directories for target files will be created, if they not already
#: exist
create_dirs = True

#: HTTP Server
#: -----------

#: default port on the localhost to listen for http requests
default_port = 8899

#: A list of extensions that will be sent with the 'text/plain' MIME type
text_extensions = ['.tex', ]

#: CLI
#: ---

#: Use terminal colors for the CLI
colored_term = True

#: Options for the 'init's subcommand
cli_init_starter_name_color = 'red'
cli_init_starter_subheadind_color = 'magenta'

#: Convert and Tag Defaults
#: ------------------------

#: The default prefix for tags
tag_prefix = r'@'

#: Maximum depth of tag trees
tag_max_depth = 30

# If True, converted files will be updated only when they're changed. Otherwise
# converted files will always be updated
convert_cache = True

#: The location in the target_root to store temporary cached files
cache_path = '.cache'

#: The default location for media (image, css, js) files.
media_path = 'media'


#: Attributes
#: ----------

#: For attribute entries that are target-specific, use the following character
#: or string to separate the key and target. ex: class.html
attribute_target_sep = '.'

#: Context
#: -------

#: Attribute in the context in which the body of a file (the string and AST)
#: is stored in.
body_attr = 'body'

#: Maximum depth of loaded context dicts
context_max_depth = 6

#: Maximum file size for context header files
context_max_size = 8192  # 8kB

default_context = {
    # Set the disseminate version
    'version': __version__,

    # The default targets to render. This is a string so that documents
    # can overwrite these values
    'targets': {'html'},

    'paths': [],
    'template': 'default',

    # Entries for navigation
    'prev': '',
    'next': '',
    'srclink': '',
    'txtlink': '',
    'texlink': '',
    'pdflink': '',
    'epublink': '',

    'toc': 'all headings expanded',

    # Options related to links
    'relative_links': True,
    'base_url': '/{target}/{subpath}',
    'media_path': 'media',

    # Process tags for the following entries in a context
    # (see processors/process_context_tags.py)
    'process_context_tags': {body_attr, 'toc', 'prev', 'next',
                             'srclink', 'txtlink', 'texlink', 'pdflink',
                             'epublink'},

    # Process paragraphs for tags with the following names
    # (see tags/paragraphs.py)
    'process_paragraphs': {body_attr, "featurebox"},

    # The following are strings to present labels. They are substituted with
    # values from their respective label and parsed in disseminate format.
    # The label format strings are identified first by the tag that uses
    # the label, then the kind(s) of the label, and finally, and optionally,
    # the target for the rendered document.
    'label_fmts': {
        'document': '@label.title',

        'ref_document': '@label.title',

        # caption tags
        'caption_figure': '@b{Fig. @label.number}. ',
        'caption_table': '@b{Table @label.number}. ',

        'ref_caption_figure': '@b{Fig. @label.number}',
        'ref_caption_table': '@b{Table @label.number}',

        # Headings tags
        'heading': '@label.tree_number. @label.title',
        'heading_title': '@label.title',
        'heading_part': 'Part @label.part_number. @label.title',
        'heading_chapter': 'Chapter @label.chapter_number. @label.title',

        'ref_heading': '@label.title',
        'ref_heading_part': 'Part @label.part_number. @label.title',
        'ref_heading_chapter': 'Chapter @label.chapter_number. @label.title',

        # Citation formats
        # 'citation': '@sup{label.number}',
        #
        # 'citation_ref': '({refs})',
        # 'citation_id': 'citation.number',
        # 'citation_ref_sep': ',',
        #
        # 'citation_journal': '$journal.authors, $journal.title, '
        #                     '@b{$journal.journal}',
        #
        # 'citation_author_sep': ',',
        # 'citation_author_and': True,
        # 'citation_author_initials_point': True,

    },

    'label_resets': {
        # New chapters reset the numbers on sections, subsections,
        # subsubsections
        'part': {'chapter', 'section', 'subsection', 'subsubsection'},
        'chapter': {'section', 'subsection', 'subsubsection', 'figure',
                    'table'},
        'section': {'subsection', 'subsubsection'},
        'subsection': {'subsubsection'},
    },

    # Set the separator between a doc_id and label_id when identifying a label
    'label_sep': '::',

    # The following tags are unavailable. This is a string so that contexts
    # from templates can replace these values. See
    # disseminate.tags.factory.TagFactory.
    'inactive_tags': set(),

    # Target-specific customizations
    'epub': dict(),

    # Macros are string entries that aren't processed into tags and asts.
    # These start with the 'tag_prefix' (e.g. '@')
    # Macros - Isotopes
    '@1H': '@sup{1}H', '@2H': '@sup{2}H', '@13C': '@sup{13}C',
    '@15N': '@sup{15}N', '@19F': '@sup{19}F', '@31P': '@sup{31}P',

    # Macros - Molecules
    '@H2O': 'H@sub{2}O',

    # Macros - Symbols
    '@deg': '@sup{○}',
    '@degC': '@sup{○}C',
    '@times': '@symbol{times}',

    # Macros - Greek
    '@alpha': '@symbol{alpha}', '@beta': '@symbol{beta}',
    '@gamma': '@symbol{gamma}', '@delta': '@symbol{delta}',
    '@epsilon': '@symbol{epsilon}', '@zeta': '@symbol{zeta}',
    '@eta': '@symbol{eta}', '@theta': '@symbol{theta}',
    '@iota': '@symbol{iota}', '@kappa': '@symbol{kappa}',
    '@lambda': '@symbol{lambda}', '@mu': '@symbol{mu}', '@nu': '@symbol{nu}',
    '@xi': '@symbol{xi}', '@omicron': '@symbol{omicron}', '@pi': '@symbol{pi}',
    '@rho': '@symbol{rho}', '@sigma': '@symbol{sigma}', '@tau': '@symbol{tau}',
    '@upsilon': '@symbol{upsilon}', '@phi': '@symbol{phi}',
    '@chi': '@symbol{chi}', '@psi': '@symbol{psi}', '@omega': '@symbol{omega}',
    '@Alpha': '@symbol{Alpha}', '@Beta': '@symbol{Beta}',
    '@Gamma': '@symbol{Gamma}', '@Delta': '@symbol{Delta}',
    '@Epsilon': '@symbol{Epsilon}', '@Zeta': '@symbol{Zeta}',
    '@Eta': '@symbol{Eta}', '@Theta': '@symbol{Theta}',
    '@Iota': '@symbol{Iota}', '@Kappa': '@symbol{Kappa}',
    '@Lambda': '@symbol{Lambda}', '@Mu': '@symbol{Mu}', '@Nu': '@symbol{Nu}',
    '@Xi': '@symbol{Xi}', '@Omicron': '@symbol{Omicron}', '@Pi': '@symbol{Pi}',
    '@Rho': '@symbol{Rho}', '@Sigma': '@symbol{Sigma}', '@Tau': '@symbol{Tau}',
    '@Upsilon': '@symbol{Upsilon}', '@Phi': '@symbol{Phi}',
    '@Chi': '@symbol{Chi}', '@Psi': '@symbol{Psi}', '@Omega': '@symbol{Omega}',

}

#: Template Defaults
#: -----------------

#: default basename for a template file
template_basename = 'template'

#: default filename for additional context files from templates
template_context_filename = 'context.txt'

#: default template starter description file
template_starter_dir = 'starters'
template_starter_desc_filename = 'description.yaml'

#: Use module templates only. If True, user-specified custom templates, which
#: may not be safe, can be used.
module_only = False

#: the paths for templates in disseminate modules
module_template_paths = [pathlib.Path(__file__).parent / 'templates']

#: Builder Defaults
#: -------------------

#: A series of allowed tracked extensions for each target type with information
#: to translate these files to a useable form, if needed.
#: The keys are the targets. The values are lists of valid extensions that
#: can be included for the target, in order of decreasing preference.
tracked_deps = {
    # html targets ca use .css style files, .svg and .png images
    '.html': ['.css', '.svg', '.png'],
    '.xhtml': ['.css', '.svg', '.png'],
    # tex (and pdf) target can use .pdf and .png images
    '.tex': ['.pdf', '.png'],
    # css files can include .css files
    '.css': ['.css', ]}

#: The default decider class
default_decider = 'Md5Decider'

#: The default number of seconds before a subprocess is timedout.
default_timeout = 15

#: Tags
#: ----

empty = tuple()

#: The number of spaces to identify sublist items.
list_level_spaces = 2

#: XHTML targets
#: ~~~~~~~~~~~~

xhtml_namespace = {'epub': 'http://www.idpf.org/2007/ops'}

#: Render XHTML pages with newlines and indentation
xhtml_pretty = True

#: Allowed xhtml tags with required arguments/attributes.
#: This dict will be checked to see if an html tag is allowed.
#: The values are tuples that indicate the order of attributes for tags
xhtml_tag_arguments = {'a': ('href',),
                       'img': ('src',),
                       'link': ('rel',)
                       }

#: Allowed optional arguments/attributes for html tags
#: This dict will be checked to see if an html tag is allowed.
epub_type = "{{{}}}type".format(xhtml_namespace['epub'])
xhtml_tag_optionals = {'a': ('class', 'role', epub_type),
                       'aside': ('class', 'id', epub_type),
                       'blockquote': empty,
                       'br': empty,
                       'code': empty,
                       'caption': ('class', 'id'),
                       'dd': empty,
                       'div': ('class', 'id'),
                       'dl': empty,
                       'dt': empty,
                       'em': empty,
                       'figure': ('id', 'class'),
                       'figcaption': ('id', 'class'),
                       'h1': ('id', 'class'),
                       'h2': ('id', 'class'),
                       'h3': ('id', 'class'),
                       'h4': ('id', 'class'),
                       'h5': ('id', 'class'),
                       'hr': empty,
                       'li': ('class',),
                       'link': ('href', 'media'),
                       'i': empty,
                       'img': ('alt', 'class', 'style'),
                       'ol': ('class',),
                       'p': ('class',),
                       'pre': ('class',),
                       'span': ('class', 'id', 'style'),
                       'strong': empty,
                       'sub': empty,
                       'sup': empty,
                       'table': ('id', 'class',),
                       'tbody': ('class',),
                       'td': ('class',),
                       'th': ('class',),
                       'thead': ('class',),
                       'tr': ('class',),
                       'ul': ('class',),
                       }

#: TEX targets
#: ~~~~~~~~~~~

#: Allowed latex environments and required arguments. If an environment is not
#: listed here or in the tex_env_optionals, it cannot be used.
#: The values are tuples that indicate the order of attributes for environments
#: and commands
tex_env_arguments = {'align': empty,  # no required arguments
                     'align*': empty,
                     'alignat': (IntPositionalValue,),  # \begin{alignat}{3}
                     'alignat*': (IntPositionalValue,),  # \begin{alignat*}{3}
                     'center': empty,
                     'enumerate': empty,

                     'examplebox': empty,
                     'featurebox': empty,
                     'problembox': empty,

                     'itemize': empty,
                     'panel': (StringPositionalValue,),
                     'tabular': (StringPositionalValue,),
                     'table': empty,
                     'table*': empty,
                     'margintable': empty,
                     'toclist': empty,
                     'verbatim': empty,
                     }

tex_env_optionals = {'enumerate': (StringPositionalValue, 'label'),
                     'easylist': (StringPositionalValue,),
                     'figure': (StringPositionalValue,),  # \begin{figure}[h]
                     'figure*': (StringPositionalValue,),
                     'marginfigure': (StringPositionalValue,),
                     }

tex_cmd_arguments = {'textbf': empty,
                     'textit': empty,

                     'part': empty,
                     'chapter': empty,
                     'section': empty,
                     'subsection': empty,
                     'subsubsection': empty,
                     'paragraph': empty,
                     'subparagraph': empty,

                     'part*': empty,
                     'chapter*': empty,
                     'section*': empty,
                     'subsection*': empty,
                     'subsubsection*': empty,

                     'maketitle': empty,
                     'title': empty,
                     'author': empty,
                     'today': empty,

                     'caption': empty,
                     'ensuremath': empty,
                     'marginnote': empty,
                     'marginpar': empty,

                     'item': empty,
                     'setcounter': (StringPositionalValue, IntPositionalValue),
                     'label': empty,
                     'includegraphics': empty,
                     'textcolor': (StringPositionalValue,),
                     'boldsymbol': empty,

                     'toprule': empty,
                     'midrule': empty,
                     'bottomrule': empty,

                     'hfill': empty,
                     'pageref': (StringPositionalValue,),
                     'href': (StringPositionalValue,),

                     'detokenize': empty,
                     }

tex_cmd_optionals = {'includegraphics': ('width', 'height'),
                     }


#: Default text width to rewrap paragraphs. Set to 0 to disable.
# tex_paragraph_width = 80
