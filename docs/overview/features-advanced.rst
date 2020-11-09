Features: Advanced
==================

.. role:: dm(code)
   :language: dm

1) Document Inheritance
-----------------------

Document headers define how a document and its sub-documents are rendered to
target formats. Document headers are loaded into a context, which is a special
``dict`` in python. Most header values are copied to sub-documents, which may
be overriden.

Consider the following project document tree.

.. code-block::

    src/main.dm
    src/chapters/chap1.dm
    src/chapters/chap2.dm

The project's ``title`` and ``author`` could be specified in the root document.

.. code-block:: dm
    :caption: src/main.dm

    ---
    title: This is my book
    author: Debra Danson
    template: books/novel
    include:
        chapters/chap1.dm
        chapters/chap2.dm
    ---
    @titlepage

The sub-documents carry the values from the parent document.

.. code-block:: dm
    :caption: src/chapters/chap1.dm

    ---
    chapter: My first chapter
    ---
    @chapter
    @author

In this case, the author field from ``src/main.dm`` will be inserted in
``src/chapters/chap.dm``.


2) Target Attributes
--------------------

Tag attributes generally apply to all document target formats. However,
sometimes attributes need to be specified for specific document targets. For
example, this feature can be helpful in customizing the position of images when
the document is rendered on a page with the ``pdf`` document target.

Target attributes are specified by ending an attribute with a period and the
document target.

.. code-block:: dm

    @img[width=80% width.html=40%]{figures/fig1.png}

In this case, the image's width will be 80% of the text width for all document
targets except ``.html``, which will render the image's width to 40%
of the text width.

Target attributes also apply to positional arguments.

.. code-block:: dm
    :emphasize-lines: 1

    @marginfig[id=perfect-vs-ideal-gas-3d -20em.tex]{
        @img[width=100%]{figures/fig1.1.png}
        @caption{Pressure vs. volume and temperature for @CO2 gas
           demonstrates that the real gas pressure is less than the
           perfect gas pressure.}
    }

In this example, the ``-20em.tex`` positional argument offsets the margin
figure's vertical position.

3) Label Formats
----------------

Templates may adopt different formats for the presentation of label references
from :dm:`@ref` tags. These can be customized in the header of the root document
or any of the sub-documents with the ``label_fmts`` entry.

.. code-block:: dm

    ---
    label_fmts:
        heading: "@label.tree_number. @label.title"
        heading_title: "@label.title"
        heading_part: "Part @label.part_number. @label.title"
        heading_chapter: "Chapter @label.chapter_number. @label.title"
        caption_figure: "@b{Fig. @label.number}"
    ---

Label formats are written in disseminate format and, optionally, have access
to the ``@label`` metadata.

For headings in general, they will adopt the most specific label format. In
this case, ``heading_title`` takes precedence over ``heading`` for ``@title``
labels, so all titles will simply present the label's title. However, a
``@section`` heading will use the ``heading`` label format, since a
``header_section`` label format was not specified.

Additionally, target-specific label formats can be presented.

.. code-block:: dm

    ---
    label_fmts:
        heading_title: "Title: @label.title"
        heading_title_html: "My HTML Title: @label.title"
    ---

In this example, the ``heading_title_html`` label format will be used to format
references to ``@title`` headings with ``html`` targets whereas the
``heading_title`` label format will be used for all other targets.

Finally, templates may reset the heading counters for different types of
headings with the ``label_resets`` header entry.

.. code-block:: dm

    ---
    label_resets:
        part: chapter, section, subsection, subsubsection
        chapter: section, subsection, subsubsection, figure, table
    ---

In the above example, the number (counter) for the chapter, section, subsection
and subsubsection are reset every time there is a new :dm:`@part` is
encountered. Likewise, the section, subsection, subsubsection, figure and
table numbers are reset every time a new :dm:`@chapter` is encountered.

4) Signal Processing
--------------------

Disseminate integrates a customized signal dispatch system. The system is
designed similarly to `Blinker <https://pythonhosted.org/blinker/>`_, but it
allows receivers to register an order for processing in sequence.

The processing of documents, tags, labels, building is initiated by a signal
dispatch and handled in a factory pattern with signal receivers. This system
allows new functionality to be easily added, like plug-ins, while decoupling
the various sub-modules of disseminate.

The listing of current signals and receivers can be accessed from the
commandline interface.

.. raw:: html

    <pre class='terminal'>
      <strong><span class='prompt'>$</span> dm setup --list-signals</strong>
    1. <span class='underline'>tag_created</span>
        A signal emitted when a tag is created. Receivers take a tag parameter.

        Receivers:
        a. <span class='cyan'>process_hash</span> - A receiver to create a hash for the contents of tags.
           order: 50
        b. <span class='cyan'>process_macros</span> - A receiver for replacing macros in pre-parsed tag strings.
           order: 100
        c. <span class='cyan'>process_content</span> - A receiver to parse the contents of tags into sub-tags.
           order: 200
        d. <span class='cyan'>process_typography</span> - A receiver to parse the typography of tags.
           order: 300
        e. <span class='cyan'>process_paragraphs</span> - A receiver to parse the paragraphs of tags.
           order: 400

    2. <span class='underline'>add_file</span>
        Add a file dependency to a target builder. Takes parameters, context,
        in_ext, target and use_cache.

        Receivers:
        a. <span class='cyan'>add_file</span> - Add a file to the target builder.
           order: 1000

    3. <span class='underline'>document_onload</span>
        Signal sent when a document is loaded. Receivers take a document or
        document context parameter.

        Receivers:
        a. <span class='cyan'>reset_document</span> - Reset the context and managers for a document on load.
           order: 100
        b. <span class='cyan'>load_document</span> - Load the document text file into the document context.
           order: 200
        c. <span class='cyan'>process_headers</span> - Process header strings for entries in a context by loading
           them into the context.
           order: 1000
        d. <span class='cyan'>reset_label_manager</span> - Reset the label manager in the context on document load.
           order: 1050
        e. <span class='cyan'>process_document_label</span> - A context processor to set the document label in the
           label manager.
           order: 1100
        f. <span class='cyan'>process_tags</span> - Convert context entries into tags for entries listed the
           process_context_tags' context entry.
           order: 10000

    4. <span class='underline'>ref_label_dependencies</span>
        A notification emitter.

        Receivers:
        a. <span class='cyan'>add_ref_labels</span> - Find and add the labels associated with Ref tags for
           all tags in the context.
           order: 1000

    5. <span class='underline'>document_tree_updated</span>
        Signal sent when a root document or one of its sub-documents was re-loaded.
        Takes a root document as a parameter.

        Receivers:
        a. <span class='cyan'>add_target_builders</span> - Add target builders to a document context
           order: 2000
        b. <span class='cyan'>set_navigation_labels</span> - Set the navigation labels in the context
           of all documents in a document tree.
           order: 10000

    6. <span class='underline'>find_builder</span>
        Given a document context and a target, find the corresponding target builder.

        Receivers:
        a. <span class='cyan'>find_builder</span> - Find a target builder in a document context, or
           None if None was found.
           order: 1000

    7. <span class='underline'>document_created</span>
        Signal sent after document creation. Receivers take a document parameter.

    8. <span class='underline'>document_deleted</span>
        Signal sent before a document is deleted. Receivers take a document parameter.

        Receivers:
        a. <span class='cyan'>delete_document</span> - Reset the context and managers for a document on
           document deletion.
           order: 100

    9. <span class='underline'>document_build</span>
        Signal sent when a document's targets are being built to their final
        target files. Receivers take a document parameter.

        Receivers:
        a. <span class='cyan'>build</span> - Build a document tree's targets (and subdocuments) using the target
           builders.
           order: 1000

    10. <span class='underline'>document_build_needed</span>
        Signal sent to evaluate whether a build is needed. Takes a document as
        a parameter and returns True or False

        Receivers:
        a. <span class='cyan'>build_needed</span> - Evaluate whether any of the target builders need to be build
           order: 1000
   </pre>


5) Intelligent Building
-----------------------

In many respects, disseminate is a software construction tool like
`SCons <https://scons.org>`_ or `GNU make <https://www.gnu.org/software/make/manual/make.html>`_:
document source files (``.dm``) are parsed and converted to tags, and external
tools may optionally build some of the dependencies, like images, plots and
diagrams.

The disseminate build system includes a number of features to quickly and
correctly build the target documents:

1. Each document target has its own builder, which comprises of a nested tree
   of sequential and parallel builders.
2. Builders are selected as needed from the specified document target--*e.g.*
   a ``pdf2svg`` builder is added for ``svg`` images when the document is
   rendered to the ``html`` document target, but the ``pdf`` is only added
   (copied) for ``tex`` and ``pdf`` document targets.
3. The build system uses a multithreaded and multiprocessing implementation
   to build documents in parallel to the extent possible. This parallelization
   reduces overall build times from 10s of minutes to 10s of seconds.
4. Intermediate files are cached in a ``.cache`` subdirectory.
5. Like `SCons <https://scons.org>`_, build decisions are made based on the
   hash of files rather than modification times (like
   `GNU make <https://www.gnu.org/software/make/manual/make.html>`_)
6. Additional dependencies like labels hashes are included in the build.
   References to labels that have changed from other documents will trigger a
   new build.
7. The build system is designed to operate transparently to the user.

6) Webserver Preview
--------------------

The CLI includes a webserver based on
`Sanic <https://sanic.readthedocs.io/en/latest/>`_ to present the rendered
documents with the ``html`` document target.

The webserver previewer is started from the command line.

.. raw:: html

    <pre class='terminal'>
      <strong><span class='prompt'>$</span> dm preview</strong>
    </pre>