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