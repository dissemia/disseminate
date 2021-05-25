.. _quickstart:

Quickstart
==========

Follow the installation instructions to get disseminate working.

Terminal
--------

**Step 1**: Setup a project
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A disseminate project is a collection of documents that come together to render
into textbooks, books, articles or essays.

The simplest project consists of a single document, typically in its own
directory.

.. raw:: html

    <pre class='terminal'>
      <strong><span class='prompt'>$</span> mkdir MyBook</strong>
      <strong><span class='prompt'>$</span> cd MyBook</strong>
      <strong><span class='prompt'>$</span> mkdir src</strong>
    </pre>

**Step 2**: Create a first document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In your favorite text editor, edit a first document (``src/main.dm``).

.. code:: dm

    ---
    title: My first document
    author: John A. Doe
    targets: html
    ---
    @chapter{This is my first chapter}

    I am @i{here} to show you how this works.

**Step 3**: Build the document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use disseminate to build the document.

.. raw:: html

    <pre class='terminal'>
      <strong><span class='prompt'>$</span> dm build</strong>
      Build: done
      <strong><span class='prompt'>$</span> find . -type f</strong>
      ./html/main.html
      ./html/media/css/bootstrap.min.css
      ./html/media/css/default.css
      ./html/media/css/pygments.css
      ./html/media/css/base.css
      ./html/media/icons/tex_icon.svg
      ./html/media/icons/menu_inactive.svg
      ./html/media/icons/menu_active.svg
      ./html/media/icons/epub_icon.svg
      ./html/media/icons/txt_icon.svg
      ./html/media/icons/pdf_icon.svg
      ./html/media/icons/dm_icon.svg
      ./.cache/md5decider/cache.db-shm
      ./.cache/md5decider/cache.db-wal
      ./.cache/md5decider/cache.db
      ./src/main.dm
    </pre>

**Step 4**: View the document
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the disseminate previewer to view the document website.

.. raw:: html

    <pre class='terminal'>
      <strong><span class='prompt'>$</span> dm preview</strong>
      [2020-11-05 12:44:48 -0600] [56581] [INFO] Goin' Fast @ http://127.0.0.1:8899
      [2020-11-05 12:44:48 -0600] [56581] [INFO] Starting worker [56581]
    </pre>

Use a web browser to visit the webserver on your computer at
**http://127.0.0.1:8899**. This will present the document index for your
project.

.. image:: ../_static/imgs/Disseminate\ Document\ Listing.svg
    :width: 600px

Clicking on the ``html`` link will show the html rendered version of your
document.

.. image:: ../_static/imgs/My\ first\ document.svg
    :width: 600px



