#: Document Defaults
#: -----------------

#: The default extension of markup files
document_extension = '.dm'

#: Maximum file size
document_max_size = 204800  # 200kB

#: If True, only target files that don't exist or are older than the source
#: files will be rendered.
update_only = True

#: If True, directories for target files will be created, if they not already
#: exist
create_dirs = True

#: Tree Defaults
#: -------------

#: The default filename for index trees
index_filename = 'index.tree'

#: When document (markup source) files are in sub-directories, the
#: project root directory will have these paths stripped.
strip_base_project_path = True

#: A list of the default target formats of rendered files
default_target_list = ['.html', '.tex']

#: If True, rendered target documents will be saved in a subdirectory with
#: the target extension's name (ex: 'html' 'tex')
segregate_targets = True

#: The template base file for rendering the tree.
tree_template_basefilename = "tree"

#: AST Processing
#: --------------

#: The maximum depth of the AST
ast_max_depth = 30


#: HTML Rendering
#: --------------

#: The tag to use for the document in the HTML page
html_root_tag = 'body'

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Only render allowed HTML tags
html_allowed_tags = True

#: Only render allowed HTML attributes
html_allowed_attributes = True

#: HTTP Server

#: default port on the localhost to listen for http requests
default_port = 8899
