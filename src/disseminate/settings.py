from .utils.types import IntPositionalValue, StringPositionalValue


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

#: A set of extensions that are compiled from other extensions. The keys are
#: the compiled extension and the values are the extensions from which these
#: extensions are compiled.
compiled_exts = {'.pdf': '.tex',
                 }

#: HTTP Server
#: -----------

#: default port on the localhost to listen for http requests
default_port = 8899

#: A list of extensions that will be sent with the 'text/plain' MIME type
text_extensions = ['.tex', ]

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
    'targets': 'html',
    'paths': [],

    # Options related to links
    'relative_links': True,
    'base_url': '/{target}/{subpath}',

    # Process tags for the following entries in a context
    # (see processors/process_context_tags.py)
    'process_context_tags': {body_attr, 'toc'},

    # Process paragraphs for tags with the following names
    # (see tags/paragraphs.py)
    'process_paragraphs': {body_attr},

    # The filename for additional context header files
    'additional_header_filename': 'context.txt',

    # The following are strings to present labels. They are substituted with
    # values from their respective label and parsed in disseminate format.
    # The label format strings are identified first by the tag that uses
    # the label, then the kind(s) of the label, and finally, and optionally,
    # the target for the rendered document.
    'label_fmts': {
        'document': '@label.title',

        # caption tags
        'caption_figure': '@b{Fig. @label.branch_number.@label.number}.',

        'ref_figure': '@b{Fig. @label.branch_number.@label.number}',
        'ref_figure_html': '@a[href="@link"]{'
                           '@b{Fig. @label.branch_number.@label.number}}',
        'ref_figure_tex': '\\hyperref[@label.id]{'
                           '@b{Fig. @label.branch_number.@label.number}}',

        # Headings tags
        'heading': '@label.title',

        # html specific formatting
        'heading_html': '@number{@label.tree_number.} '
                        '@label.title',

        # Ref tags
        'ref_heading_html': '@a[href="@link"]{@label.title}',

        # TOCRef Tags
        'tocref_document_html': '@a[href="@link"]{@label.title}',
        'tocref_document_tex': '\\hyperref[@label.id]'
                               '{@label.title} '
                               '\\hfill \\pageref{@label.id}',
        'tocref_heading_html': '@a[href="@link"]{'
                               '@number{@label.tree_number.} '
                               '@label.title}',
        'tocref_heading_tex': '\\hyperref[@label.id]'
                              '{@label.tree_number. @label.title} '
                              '\\hfill \\pageref{@label.id}',

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

    # The following tags are unavailable. See
    # disseminate.tags.factory.TagFactory
    'inactive_tags': set(),

    # Macros are string entries that aren't processed into tags and asts.
    # These start with the 'tag_prefix' (e.g. '@')
    # Macros - Isotopes
    '@1H': '@sup{1}H', '@2H': '@sup{2}H', '@13C': '@sup{13}C',
    '@15N': '@sup{15}N', '@19F': '@sup{19}F', '@31P': '@sup{31}P',

    # Macros - Molecules
    '@H2O': 'H@sub{2}O',

    # Macros - Symbols
    '@deg': '@sup{○}',

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

#: modifiers for Jinja2 blocks, variables and comments. Parentheses are used
#: instead of the default curly braces to more easily work with latex formats.
template_block_start = '(%'
template_block_end = '%)'
template_variable_start = '(('
template_variable_end = '))'
template_comment_start = '(#'
template_comment_end = '#)'

#: Dependency Defaults
#: -------------------

#: A series of allowed tracked extensions for each target type with information
#: to translate these files to a useable form, if needed.
#: The keys are the targets. The values are lists of valid extensions that
#: can be included for the target, in order of decreasing preference.
tracked_deps = {
    # html targets ca use .css style files, .svg and .png images
    '.html': ['.css', '.svg', '.png'],
    # tex (and pdf) target can use .pdf and .png images
    '.tex': ['.pdf', '.png'],
    # css files can include .css files
    '.css': ['.css', ]
    }

#: Tags
#: ----

default_attrs = {'Toc': "bolded='branch' "
                        "dotted='section subsection subsubsection'"}

toc_listing = 'toclist'
toc_pageref_width = '5ex'
toc_bolded_kinds = ('part', 'chapter')
toc_dotted_kinds = ('section', 'subsection', 'subsubsection')

empty = tuple()

#: HTML Tags
#: ~~~~~~~~~

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Allowed html tags with required arguments/attributes.
#: This dict will be checked to see if an html tag is allowed.
html_tag_arguments = {'a': ('href',),
                      'img': ('src',),
                      'link': ('rel',)
                      }

#: Allowed optional arguments/attributes for html tags
#: This dict will be checked to see if an html tag is allowed.
html_tag_optionals = {'a': ('class', 'role'),
                      'blockquote': empty,
                      'br': empty,
                      'code': empty,
                      'dd': empty,
                      'div': ('class', 'id'),
                      'dl': empty,
                      'dt': empty,
                      'em': empty,
                      'h1': ('id', 'class'),
                      'h2': ('id', 'class'),
                      'h3': ('id', 'class'),
                      'h4': ('id', 'class'),
                      'h5': ('id', 'class'),
                      'hr': empty,
                      'li': ('class',),
                      'link': ('href', 'media'),
                      'i': empty,
                      'img': ('alt', 'class', 'width', 'height'),
                      'ol': ('class',),
                      'p': ('class',),
                      'pre': ('class',),
                      'span': ('class', 'id'),
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

#: TEX Tags
#: ~~~~~~~~

#: Allowed latex environments and required arguments. If an environment is not
#: listed here, it cannot be used.
tex_env_arguments = {'enumerate': empty,  # no required arguments
                     'itemize': empty,
                     'marginfigure': empty,

                     'align': empty,
                     'align*': empty,

                     # ex: \begin{alignat}{3}
                     'alignat': (IntPositionalValue,),
                     # ex: \begin{alignat*}{3}
                     'alignat*': (IntPositionalValue,),

                     'center': empty,
                     'verbatim': empty,
                     'toclist': empty,
                     }

tex_env_optionals = {# ex: \begin{enumerate}[I]
                     'enumerate': (StringPositionalValue, 'label'),

                     # ex: \begin{figure}[h]
                     'figure': (StringPositionalValue,),
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
                     }

tex_cmd_optionals = {'includegraphics': ('width', 'height')}


#: Default text width to rewrap paragraphs. Set to 0 to disable.
# tex_paragraph_width = 80
