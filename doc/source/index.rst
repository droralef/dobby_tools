.. Dobby Tools documentation master file, created by
   sphinx-quickstart on Mon Feb 20 15:35:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dobby Tools documentation!
==========================


dobbyt.stimuli:
---------------

Visual objects.

.. toctree::
   :maxdepth: 2
   :glob:

   stimuli/*


dobbyt.movement:
----------------

.. toctree::
   :maxdepth: 2
   :glob:

   movement/*


dobbyt.validators:
------------------

Perform various validations on mouse/finger movement during the trial.
Typically, you'd call reset() for each validator when the trial starts, and check_xyt() each time you
observe a mouse/finger movement.


.. toctree::
   :maxdepth: 2
   :glob:

   validators/*


dobbyt.misc:
------------

.. toctree::
   :maxdepth: 2
   :glob:

   misc/*


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

