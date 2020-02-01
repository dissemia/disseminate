.. _dependency-manager:

Dependency Manager
==================

The dependency manager tracks which files are needed to render a
target format, and it works with converters to created files in needed
formats or it modifies files as needed.

``html`` targets
----------------

The ``html`` format may include formatting files (``.css`` and
``.js``) and media files (``.png`` and ``.svg``).

+----------+-----------------+-----------+---------------------------------------------------+
| Format   | Used in tags    | Action    | Notes                                             |
+==========+=================+===========+===================================================+
| ``.js``  |                 | copied    |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.css`` |                 | copied &  | Included dependencies to other ``.css`` files are |
|          |                 | modified  | also copied. The paths of ``.css`` dependencies   |
|          |                 |           | are updated for the new ``html`` target directory.|
+----------+-----------------+-----------+---------------------------------------------------+
| ``.png`` |                 | copied    |                                                   |
|          |                 |           |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.svg`` | :ref:`@img      | copied    |                                                   |
|          | <tags-img>`     |           |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.tif`` | :ref:`@img      | converted | Converted to ``.png`` format with the             |
|          | <tags-img>`     |           | :ref:`convert` converter.                         |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.pdf`` | :ref:`@img      | converted | Converted to ``.svg`` format with the             |
|          | <tags-img>`     |           | :ref:`pdf2svg <pdf2svg>` converter.               |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.asy`` | :ref:`@asy      | converted | Converted to ``.svg`` format with the             |
|          | <tags-asy>`     | (inline)  | :ref:`asy2svg <asy2svg>` converter.               |
|          | :ref:`@img      |           |                                                   |
|          | <tags-img>`     |           |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.tex`` | :ref:`@eq       | converted | Converted to ``.svg`` format with the             |
|          | <tags-eq>`      | (inline)  | :ref:`tex2svg <tex2svg>` converter.               |
+----------+-----------------+-----------+---------------------------------------------------+

``tex`` targets
----------------

The ``tex`` format may include formatting files  media files (``.pdf`` and ``.png``).

+----------+-----------------+-----------+---------------------------------------------------+
| Format   | Used in tags    | Action    | Notes                                             |
+==========+=================+===========+===================================================+
| ``.pdf`` | :ref:`@img      | copied    |                                                   |
|          | <tags-img>`     |           |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.png`` | :ref:`@img      | copied    |                                                   |
|          | <tags-img>`     |           |                                                   |
+----------+-----------------+-----------+---------------------------------------------------+
| ``.tif`` | :ref:`@img      | converted | Converted to ``.png`` format with the             |
|          | <tags-img>`     |           | :ref:`convert` converter.                         |
+----------+-----------------+-----------+---------------------------------------------------+