Release Notes
=============

0.13 beta
---------

1. *Documentation*. Unify documentation using Sphinx in the project.
2. *Sphinx*. Clean-up css and API documentation for new functions and classes
3. *Sphinx*. Add release notes.
4. *BaseContext*. Implement updating, shallow copies and deep copies
5. *Document*. Refactor the setting of the document label in the
   DocumentContext, cleanup loading of documents and fix partial loading
   errors, rename the `load_document` method to `load`. Fix document numbering
   in the `render_tree_html` utility function.
6. *DocumentContext*. Refactor to implement shallow/deep copy functionality from
   BaseContext and the Document id (doc_id).
7. *Header*. Refactor the process_header function to use the new str_to_dict
   string utility function.
8. *Labels*. Major refactoring to include labels of differents types--
   ContentLabel and HeadlingLabel--and include curation functions to clean-up
   labels
9. *Paths*. Implement __copy__ and __deepcopy__ methods
10. *Settings*. Refactor the default_context to use the BaseContext and include
    the label formats in the default_context.
11. *Tags*. Refactor to use the updates to the label manager.
12. *Templates*. CSS updates to the Tufte book template.
13. *Utils*. Add general utilities for classes, dicts, lists and strings.
14. *Tests*. Updates to tests to work with new APIs and refactorings.
15. *TagFactory*. Refactor into a submodule and separate documentation
16. *Substitution*. Create a new Substitution tag for placing the contents of a
    macro in a tag.
17. *AST*. Make the parsing of tags with content optional.
18. *Context*. Make the context weakref-able so that tags only need to store a
    weakref to contexts.
19. *Context*. Added a utility function for setting the 'content' attribute of
    asts and other objects.
20. *LabelManager*. Converted the root_context attribute to a weakref
21. *Tag*. Converted the context attribute to a weakref
22. *Tag utils*. Added a repl_tags utility function for changing all tags of a
    specified class in an AST element or tag to a replacement string. Included
    tests.
23. *Substitution*. Implement the substitution tag.