#: Tree Defaults
#: -------------

#: The default filename for index trees
index_filename = 'index.tree'

#: When document (markup source) files are in sub-directories, the
#: project root directory will have these paths stripped.
strip_base_project_path = True

#: A list of the default target formats of rendered files
default_target_list = ['.html', '.tex', '.pdf']

#: If True, rendered target documents will be saved in a subdirectory with
#: the target extension's name (ex: 'html' 'tex')
segregate_targets = True

#: The template base file for rendering the tree.
tree_template_basefilename = "tree"

#: Prepend links with the following
#url_root = "/"

#: Document Defaults
#: -----------------

#: The default extension of markup files
document_extension = '.dm'

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

#: Any tracked files that are in the target dependency directory ("media") but
#: that are no longer used are deleted.
#delete_unused_tracked_files = True

#media_url_root

#: Label settings
#: --------------

label_formats = {'figure_label': 'Fig. {document_number}.{number}.',
                 'figure_ref': 'Fig. {document_number}.{number}',
                 'figure_link_html': '/{filepath}#{id}',
                 'figure_link_tex': '\\hyperlink{{{id}}}{Fig. '
                                    '{{document_number}.{number}}}',
                 'heading_label': '{short}',
                 'heading_ref': '{short}',
                 'heading_link_tex': '\\hyperlink{{{id}}}{{{content}}}',
                 'heading_link_html': '/{filepath}#{id}',
                 'default_label': '{short}',
                 'default_ref': '{short}',
                 'default_link_tex': '\\hyperlink{{{id}}}{{{content}}}',
                 'default_link_html': '/{filepath}'
                 }

#: Default separator for labels. (ex: the period at the end of Fig. 1.)
label_sep = '.'

#: HTTP Server
#: -----------

#: default port on the localhost to listen for http requests
default_port = 8899

#: A list of extensions that will be sent with the 'text/plain' MIME type
text_extensions = ['.tex', ]
