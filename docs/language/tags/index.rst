Tags
====

Tags can add meaning to a block of text. In disseminate, all tags are
allowed. Tags start with an :code:`@` character, followed by a letter
and one ore more letters or numbers. Tags may have contents, which are
contained within curly braces. The following list shows valid tags:

::

  @example{...}
  @h1{...}
  @abhängigkeit{...}
  @friendship
  
.. rubric:: Attributes

Additionally, tags may contain attributes. Attributes are added with
square brackets before the contents.

::
   
   @h1[id="Intro"]{Introduction}
   @asy[scale=1.0]{dot((20,0));}
   @eq[env=alignat* 2]{y &= x}

Tag contents dictate *what* to present, and tag attributes dictate *how*
the contents are presented.

*Target-specific Attributes*. Attributes for specific targets can be
passed to the processor by appending the target's name to the
attribute:

::
   
  @img[width.tex=300 width.html=150 id=figure-1]{...}

The customization of specific targets is typically reserved for the final
stages of publication so that the targets have the final desired appearance.

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Tag Contents

   preamble
   heading
   text
   image
   equation
   code
   asy
   figs
   caption
   toc
   navigation
   featurebox
   table
   data
   collection
