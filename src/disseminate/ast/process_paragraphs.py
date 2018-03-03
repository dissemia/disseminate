"""
Functions for processing paragraphs in Abstract Syntax Trees (ASTs).
"""


import regex

from ..tags import TagFactory, Tag
from ..tags.headings import Heading


re_para = regex.compile(r'(\n{2,}|^)')


def process_paragraphs(ast=None, local_context=None, global_context=None,
                       src_filepath=None, level=1):
    """Process the paragraphs for an AST.

    .. note:: This function should be run after process_ast.

    Parameters
    ----------
    ast : list
        An optional AST to build from or a list of strings.
    local_context : dict, optional
        The context with values for the current document. (local)
    global_context : dict, optional
        The context with values for all documents in a project. (global)
    src_filepath : str, optional
        The path for the document (source markup) file being processed.
    level : int, optional
        The current level of the ast.

    Returns
    -------
    ast : :obj:`disseminate.Tag`
        The AST is a root tag with a content comprising a list of tags or
        strings.
    """
    # Setup the parsing
    factory = TagFactory()

    # Format ast into a list
    if isinstance(ast, list):
        pass
    elif isinstance(ast, Tag):
        ast = ast.content if isinstance(ast.content, list) else [ast.content]
    else:
        ast = []

    # Create a new ast. This will be populated with the processed ast and
    # returned
    new_ast = []

    # Break the strings in this ast by paragraph newlines -- i.e. 2 or more
    # consecutive newlines. The split_ast will be a list of strings (text
    # strings and strings with newlines ('\n\n') as well as Tag objects
    split_ast = []
    for i in ast:
        if isinstance(i, str):
            split_ast += re_para.split(i)
        else:
            split_ast.append(i)

    # Collect items in the current paragraph
    cur_para = []
    for i in split_ast:

        if isinstance(i, str):
            # Process a string item. It can either be a string with text or a
            # string with new lines.

            if i.strip('\n') == '':
                # If it's a string with just newlines, then this is the end of a
                # paragraph. Process the collected items in cur_para, if there
                # are items in it, and reset the cur_para. Otherwise, just skip
                # this item.

                if cur_para:
                    # Wrap the cur_para in a paragraph tag if the following
                    # applies:
                    #    1. cur_para has many items
                    #    2. cur_para has only one item and its a string.
                    #
                    # If cur_par has one item and it's not a string (i.e. it's a
                    # tag), then don't wrap it in a paragraph. This is to avoid
                    # wrapping tags like '@section' in a paragraph.

                    if len(cur_para) > 1 or isinstance(cur_para[0], str):
                        p = factory.tag(tag_name='p',
                                        tag_content=cur_para,
                                        tag_attributes=None,
                                        local_context=local_context,
                                        global_context=global_context)
                        new_ast.append(p)
                    else:
                        new_ast.append(cur_para[0])

                    # reset the current paragraph
                    cur_para = []

            else:
                # Otherwise it's just a string with text. Just add it to the
                # current paragraph

                cur_para.append(i.strip('\n'))

        elif isinstance(i, Tag) and i.include_paragraphs:
            # Process a Tag item.
            # Only process the contents of a tag if the tag's
            # include_paragraphs attribute is True

            # The contents need to be converted to an ast to be processed
            # by this function. This means that if the contents are a string,
            # wrap it in a list, otherwise just pass this tag's contents
            content = [i.content] if isinstance(i.content, str) else i.content
            content = process_paragraphs(content, local_context,
                                         global_context, src_filepath,
                                         level=1+level)

            # The processed content is now set as this tag's content. At this
            # point, it is a list. Now, add the tag to the cur_para.
            i.content = content
            cur_para.append(i)
        else:
            # If the item is a tag that should not be processed or something
            # else, just add it to the paragraph.
            cur_para.append(i)

    # After going through the split_ast, there may still be items in the
    # cur_para. Add these to the new_ast
    if cur_para:
        if len(cur_para) > 1 or isinstance(cur_para[0], str):
            p = factory.tag(tag_name='p',
                            tag_content=cur_para,
                            tag_attributes=None,
                            local_context=local_context,
                            global_context=global_context)
            new_ast.append(p)
        else:
            new_ast.append(cur_para[0])

    # Now remove paragraphs for paragraphs that have items that are headings
    # Headings should not be wrapped in paragraphs
    reprocessed_ast = []
    for i in new_ast:
        if (getattr(i, 'name', None) == 'p' and
           isinstance(i.content, list) and
           any(isinstance(j, Heading) for j in i.content)):
            # See if it's a paragraph whose contents contains Heading elements.
            # If so, remove the paragraph.
            reprocessed_ast.append(i.content)
        else:
            reprocessed_ast.append(i)
    new_ast = reprocessed_ast

    # If this is the root ast, then wrap the new_ast in a root tag.
    if level == 1:  # root level
        root = factory.tag(tag_name='root',
                           tag_content=new_ast,
                           tag_attributes=None,
                           local_context=local_context,
                           global_context=global_context)
        return root
    else:
        return new_ast
