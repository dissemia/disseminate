Command-line
============

The command-line interface (CLI) is used to render disseminate documents and to
preview rendered html documents with a built-in web server.

Disseminate is invoked on the command line through the ``dm`` command.

The disseminate main CLI includes the following help option:

.. include:: ../../cmds/rst/dm_help.rst

Disseminate includes a series of sub-commands.

render
------

The ``render`` sub-command compiles the disseminate source to the target
formats.

The ``render`` sub-command help presents the following optional arguments:

.. include:: ../../cmds/rst/dm_render_help.rst


serve
-----

The ``serve`` sub-command runs a web server on the local computer (localhost)
to present the source and target format files of disseminate projects.

The web server is started as follows:

.. only:: html

.. raw:: html

    <div class="highlight console">
    <pre>
    <span class="gp">$</span> dm serve
    <span class="go">Document(src/index.dm) render time 5.1 ms</span>
    <span class="go">INFO     :  Disseminate serving requests on port 8899...</span>
    </pre>
    </div>

The ``serve`` sub-command help presents the following optional arguments:

.. include:: ../../cmds/rst/dm_serve_help.rst
