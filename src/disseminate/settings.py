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

#: Context
#: -------

default_context = {
    'targets': 'html',
    'paths': [],
    'base_url': '/{target}'
}

#: Attribute in the context in which the body of a file (the string and AST)
#: is stored in.
body_attr = 'body'

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
tracked_deps = {'.html': ['.css', '.svg', '.png'],
                '.tex': ['.pdf', '.png'],
                '.css': ['.css', ]
                }

#: The root url prepended to dependency file paths
dep_root_url = '/'

#: Convert and Tag Defaults
#: ------------------------

# If True, converted files will be updated only when they're changed. Otherwise
# converted files will always be updated
convert_cache = True

# The location in the target_root to store tempororary cached files
cache_dir ='.cache'

# The directory to store converted media files
media_dir = 'media'

#media_url_root


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

#: Labels

#: Label formats should be formatted as they should appear as references to
#: labels
label_fmt = {'document': '{label.short}',

             'heading': '{label.short}',
             'heading_html': '@number{{{label.tree_number}.}} '
                             '{label.short}',
             'heading_tex': '{label.short}',

             'figure': '@b{{Fig. {label.branch_number}.{label.number}}}',

             # Separator between numbers in a tree number
             'label_sep': '.',

             # Terminator placed after a label.
             'label_term': '.',
             }
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
                   "li",
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
tex_paragraph_width = 80

#: Equation Tags
#: ~~~~~~~~~~~~~

eq_svg_scale = 1.15
eq_svg_crop = True
