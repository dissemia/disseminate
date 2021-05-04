Command-line
============

The command-line interface (CLI) is used to render disseminate documents and to
preview rendered html documents with a built-in web server.

Disseminate is invoked on the command line through the ``dm`` command.

The disseminate main CLI includes the following help option:

.. include:: ../../cmds/dm_help.rst

Disseminate includes a series of sub-commands.

init
----

The ``init`` sub-command initializes and lists template projects to start
a new project in disseminate.

The ``init`` help presents the following options.

.. include:: ../../cmds/dm_init_help.rst

The list of project starter templates can be listed.

.. include:: ../../cmds/dm_init.rst

The template names are listed in red. Detailed information on a project starter
template can be listed with the ``--info`` flag. In the following example,
the detailed information for the ``books/tufte/textbook1`` project starter
template is listed.

.. include:: ../../cmds/dm_init_info.rst

A new project is initialized with the ``init`` command and the template name.


.. include:: ../../cmds/dm_init_template.rst

build
------

The ``build`` sub-command compiles the disseminate source to the target
formats.

The ``build`` help presents the following optional arguments:

.. include:: ../../cmds/dm_build_help.rst


preview
-------

The ``preview`` sub-command runs a web server on the local computer (localhost)
to present the source and target format files of disseminate projects.

The web server is started as follows:

.. include:: ../../cmds/dm_preview.rst

The ``preview`` sub-command help presents the following optional arguments:

.. include:: ../../cmds/dm_preview_help.rst

setup
-----

.. _cli_setup-check:

``--check``
~~~~~~~~~~~

Disseminate uses external software for various conversion and compilation tasks.
The ``--check`` function reports whether these software dependencies are
installed and available to disseminate.

.. include:: ../../cmds/dm_setup_check.rst

.. _cli-setup-list-signals:

``--list-signals``
~~~~~~~~~~~~~~~~~~~

Disseminate uses signals and receivers for modular and decoupled processing of
documents, tags and other objects. The list of signals and attached receivers
can be listed with the following command:

.. include:: ../../cmds/dm_setup_list_signals.rst


