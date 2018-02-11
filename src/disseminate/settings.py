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
template_basename = 'template'

#: Dependency Defaults
#: -------------------

#: A series of allowed tracked extensions for each target type with information
#: to translate these files to a useable form, if needed.
#: The keys are the targets. The values are lists of valid extensions that
#: can be included for the target, in order of decreasing preference.
tracked_deps = {'.html': ['.css', '.svg'],
                '.tex': ['.pdf', '.png'],
                '.css': ['.css', ]
                }

#: Convert Defaults
#: ----------------

# If True, converted files will be updated only when they're changed. Otherwise
# converted files will always be updated
convert_cache = True

#: If a dependency exists in the target, overwrite it
#overwrite_dependencies = True

#: Any tracked files that are in the target dependency directory ("media") but
#: that are no longer used are deleted.
#delete_unused_tracked_files = True

#media_url_root

#: HTTP Server
#: -----------

#: default port on the localhost to listen for http requests
default_port = 8899

#: A list of extensions that will be sent with the 'text/plain' MIME type
text_extensions = ['.tex', ]
