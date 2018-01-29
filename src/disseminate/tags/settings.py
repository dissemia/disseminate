#: Tags settings
#: -------------

#: The tag to use for the document in the HTML page
html_root_tag = 'body'

#: Render HTML pages with newlines and indentation
html_pretty = True

#: Only render allowed HTML attributes
html_allowed_attributes = True

#: Excluded tags. These will be rendered as spans.
html_excluded = ["SCRIPT", ]

html_valid_tags = {"a",
                   "b", "blockquote", "body",
                   "caption",
                   "div",
                   "em",
                   "h1", "h2", "h3", "h4","h5", "h6",
                   "li",
                   "i", "img",
                   "ol",
                   "p",
                   "span",
                   "table", "tbody", "td", "th", "thead", "tr",
                   "ul"}