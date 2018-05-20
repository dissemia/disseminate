#: Tags settings
#: -------------

#: Labels

#: Label formats should be formatted as they should appear as references to
#: labels
label_fmt = {'document': '{label.short}',

             'heading': '{label.short}',
             'heading_html': '@number{{{label.tree_number}.}} '
                             '{label.short}',
             'heading_tex': '{label.short}',

             'figure': '@b{{Fig. {label.chapter_number}.{label.number}}}',

             # Separator between numbers in a tree number
             'label_sep': '.',

             # Terminator placed after a label.
             'label_term': '.',
             }
#: HTML Tags
#: ~~~~~~~~~

#: The tag to use for the document in the HTML page
html_root_tag = 'root'

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Allowed HTML tags. Tags that don't match these values will be rendered as
#: span tags in html
html_valid_tags = {"a",
                   "b", "blockquote", "body",
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
