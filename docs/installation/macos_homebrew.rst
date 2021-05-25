.. _installation_macos_homebrew:

MacOS (Homebrew)
================

`Homebrew <https://brew.sh/>`_ is a package manager for MacOS.

Install the Disseminate homebrew package.

.. raw:: html

  <pre class='terminal'>
     <strong><span class='prompt'>$</span> brew install dissemia/dissemia/disseminate</strong>
  </pre>

TeX Live
--------

*(Optional)* For building PDFs, a LaTeX installation is needed. The ``basictex``
package can be installed with Homebrew.

.. raw:: html

  <pre class='terminal'>
     <strong><span class='prompt'>$</span> brew install --cask basictex</strong>
     <strong><span class='prompt'>$</span> bash --login</strong>
  </pre>

.. include:: texlive.rst
