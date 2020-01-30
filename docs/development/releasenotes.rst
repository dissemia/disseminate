Release Notes
=============

0.17
-----

Converters
~~~~~~~~~~

1. *Imagemagick*. Implemented a ``.tif``/``.tiff`` converter to ``.png``

Bug Fixes
~~~~~~~~~
1. Wrap filenames and paths in curly braces for LaTeX ``\includegraphics``
   command. This is needed to deal with filenames that include special
   characters, like periods.

0.16
----

Backend
~~~~~~~

1. *Webserver*. Implement sanic for preview server.
2. *Heritable tags*. Allow tags to be copied and inherited between documents.
   This enables ``@toc`` tags and navigation tags to be shared between a
   document and its subdocuments.
3. *Navigation tags*. Add navigations tags ``@prev`` and ``@next`` to add html
   links for the previous or next page. These are available as the ``prev`` and
   ``next`` entries in the context.

0.15
----

Interfaces
~~~~~~~~~~

1. *Click*. Implemented Click for the CLI
2. *Flask*. Removed the server interface from the project

0.14
----

Interfaces
~~~~~~~~~~

1. *Flask*. Implement Flask web server for viewing the document list and
   rendered products.

Backend
~~~~~~~

1. *BaseContext*. Refactor to copy values from parent_context, rather than use
   a ChainMap implementation. This significantly speeds up look ups and loading
   of documents.
2. *BaseContext*. Create shallow copies of mutables from the parent_context
   so that these aren't modified directly. This is only done for mutables that
   have ``copy`` methods so that some mutables, like the ``LabelManager`` and
   ``DependencyManager``, can be preserved by all contexts and documents in a
   project
3. *ProcessContextHeader*. Refactor to use the new implementation of the
   BaseContext. The ``ProcessContextHeader`` now does the work of loading
   templates and loading additional context headers.
4. *Renderers*. Simplify the API.

0.13 beta
---------

Backend
~~~~~~~

1. *Documentation*. Update documentation to use sphinx.
2. *Context*. Rewrote context to work like a ChainMapping with inherited entries
   from a parent_context.
3. *Paths*. Allow relative links and urls.
4. *TemplateStrings*. Eliminated the TemplateString class with a replace_macro
   function.
5. *Equation Tags*. Implement a new pdf cropping converter to more cleanly crop
   equation images in targets like ``.html``.
6. *Attributes*. Refactored tag attributes to use an ordered dict instead of
   tuples. The Attributes class now includes useful utility functions, like
   filter and exclude.
7. *Formats*. Refactor the formatting of targets for tags with a new formats
   sub-module. This module now checks for allowed tags in the settings. The
   formats submodule also isolates the dependency of external packages, like
   lxml, to one place instead of multiple places.
8. *Processors*. Created a ProcessorABC abstract base class as a chain of
   command class for objects like tags and context. Included a simple listing
   of processors in the CLI.
9. *Tags*. Eliminate the ast submodule and replaced with a TagProcessor.
10. *Document*. Moved context processors to the document submodule and refactor
    to use the ProcessorABC.
11. *Label Manager*. Refactored to simplify the assignment of labels, the
    resetting of label counters and to minimize the dependency of labels for
    tags. Also added a set of label processors based on the ProcessorABC.

