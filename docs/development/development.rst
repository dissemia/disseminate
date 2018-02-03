Design Overview
===============

Paths
-----
Disseminate must translate many paths to generate the desired target files.
Different classes and objects use different paths, and these must be translated
when communicating between them.

The following is a listing of the types of paths.


render_path
~~~~~~~~~~~
This is the path in which the rendering will take place. It is either the
current directory or an absolute path.

The source file path (``src_filepath``) and targets paths (``targets``) for
document objects (:obj:`disseminate.Document`) are in render_paths. These
must be translated using the project_root and target_root from tree objects
(:obj:`disseminate.Tree`). See below.

examples or render_paths:
    - ``'.'``
    - ``'/Users/jlorieau/Documents/Project1'``

project_root
~~~~~~~~~~~~
This is the root (or base) directory for the project's source document
markup files. It may be an absolute path or a path relative to the current
directory (i.e. a ``render_path``). It contains disseminate markup files
(``.dm``) in its directory or subdirectory and, optionally, tree index files
(``index.tree``).

All of the source file paths (``src_filepaths``) for tree objects
(:obj:`Disseminate.Tree`) are *relative* to this project root.

examples of project_roots:
    - ``'src/'``
    - ``'.'``
    - ``'/Users/lorieau/Documents/Project1/src'``

target_root
~~~~~~~~~~~
This is the root (or base) directory for the generated documents. It may be
an absolute path or a path relative to the current directory (i.e. a
``render_path``). Depending on the ``segregate_targets`` option, the final
output path may be placed in a separate sub-directory for each type of
target. By default, ``segregate_targets`` is True.

All of the source file paths (``src_filepaths``) for tree objects
(:obj:`Disseminate.Tree`) are *relative* to this project root.

examples of target_roots:
    - ``'.'``
    - ``'output'``
    - ``'/Users/lorieau/Documents/Project1/output'``

examples of the final output directory for an ``.html`` target:
    - ``'./html'``
    - ``'output/html'``
    - ``'/Users/lorieau/Documents/Project1/output/html'``

media_root
~~~~~~~~~~
This is the directory relative to the project_root in which to find and
place dependency files. It should be a directory named ``media`` in the
project_root. Dependencies are stylesheets (``.css``), images
(``.png``, ``.svg``, ``.pdf``) and other files that a document requires in
order to be rendered. These are managed by the Dependencies object
(``disseminate.dependencies.Dependencies``)

To translate a media_root to a render_path, the tree object must also add the
project root.

example of media_root:
    - ``'media'``

url_root
~~~~~~~~

Rendering Philosophy
--------------------
The objective of output files is that they're self-contained (i.e. they have
everything they need to generate the needed target document) and that they're
independent. For LaTeX files, for example, these are generated so that they
can be compiled alone and only once.

Rendering Steps
---------------