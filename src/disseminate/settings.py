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

#: A dict with tag class names (keys) and tag classes (values) available.
tag_classes = dict()

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

default_context = {
    'targets': 'html',
    'paths': [],

    # Options related to links
    'relative_links': True,
    'base_url': '/{target}/{subpath}',

    # Process tags for the following entries in a context
    # (see processors/process_context_tags.py)
    'process_context_tags': [body_attr],

    # Process paragraphs for tags with the following names
    # (see tags/paragraphs.py)
    'process_paragraphs': [body_attr],

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
    # tex (and pdf) target can use .pdf and .pdf images
    '.tex': ['.pdf', '.png'],
    # css files can include .css files
    '.css': ['.css', ]
    }

#: Macros
#: ------

#: A list of entries in the context that are created into macros
custom_macros = ('title',)

#: Tags
#: ----

default_attrs = {'Toc': "bolded='branch' "
                        "dotted='section subsection subsubsection'"}

toc_listing = 'toclist'
toc_pageref_width = '5ex'
toc_bolded_kinds = ('part', 'chapter')
toc_dotted_kinds = ('section', 'subsection', 'subsubsection')

#: HTML Tags
#: ~~~~~~~~~

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Allowed HTML tags. Tags that don't match these values will be rendered as
#: span tags in html
html_valid_tags = {"a",
                   "b", "blockquote",
                   "code",
                   "dd", "div", "dl", "dt",
                   "em",
                   "h1", "h2", "h3", "h4", "h5", "hr",
                   "li", "link",
                   "i", "img",
                   "ol",
                   "p", "pre",
                   "span", "strong", "sub", "sup",
                   "table", "tbody", "td", "th", "thead", "tr",
                   "ul"}

html_valid_attributes = {'a': {'href', 'class', 'role'},
                         'img': {'src', 'width', 'height', 'alt', 'class'},
                         'ol': {'class'},
                         'ul': {'class'},
                         }

#: TEX Tags
#: ~~~~~~~~

tex_macros = {"caption", "chapter",
              "ensuremath",
              "marginnote", "marginpar",
              "paragraph",
              "setcounter", "section", "subsection", "subsubsection",
              "textbf", "textit"}

tex_commands = {"item"}

tex_environments = {"enumerate",
                    "itemize",
                    "marginfigure"}

tex_valid_attributes = {'img': {'width', 'height',},
                        'marginfig': {'offset'},
                        'caption': {},
                        }

#: Default text width to rewrap paragraphs. Set to 0 to disable.
# tex_paragraph_width = 80
