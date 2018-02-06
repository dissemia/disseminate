#: Tags settings
#: -------------

#: HTML Tags
#: ~~~~~~~~~

#: The tag to use for the document in the HTML page
html_root_tag = 'root'

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Only render allowed HTML attributes
html_allowed_attributes = True

#: Allowed HTML tags. Tags that don't match these values will be rendered as
#: span tags in html
html_valid_tags = {"a",
                   "b", "blockquote", "body",
                   "caption",
                   "div",
                   "em",
                   "h1", "h2", "h3", "h4", "h5",
                   "li",
                   "i", "img",
                   "ol",
                   "p",
                   "span", "strong", "sub", "sup",
                   "table", "tbody", "td", "th", "thead", "tr",
                   "ul"}

#: TEX Tags
#: ~~~~~~~~

tex_macros = {"chapter",
              "ensuremath",
              "paragraph",
              "section", "subsection", "subsubsection",
              "textbf", "textit"}

tex_commands = {"item"}

tex_environments = {"enumerate",
                    "itemize"}
