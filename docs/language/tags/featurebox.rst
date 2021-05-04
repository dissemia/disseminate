.. role:: dm(code)
   :language: dm

Feature Box
===========

Feature boxes are text boxes that present additional, tangential information
to the text. Feature boxes are used to present examples, tips or background on
a subject.

.. rst-class:: dl-parameter

:dm:`@featurebox{...}`
    A general feature box

    .. index::
        single: tags; @featurebox

    :examples:

       .. code-block:: dm

          @featurebox{
             This is a feature box.

             It has 2 paragraphs
          }


:dm:`@examplebox{...}`
    A feature box for presenting examples

    .. index::
        single: tags; @examplebox

    :examples:

       .. code-block:: dm

          @examplebox{
             @b{Problem:} This is an example box. How is it used?

             @b{Answer:} This is how.
          }

:dm:`@problembox{...}`
    A feature box for presenting problem questions

    .. index::
        single: tags; @problembox

    :examples:

       .. code-block:: dm

          @problembox{
             @b{Problem:} This is an example box. How is it used?
          }
