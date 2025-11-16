image_processing.results
========================

.. py:module:: image_processing.results

.. autoapi-nested-parse::

   Base result types for model outputs.

   This module defines :class:`ModelResult`, an abstract base class that
   stores common metadata about a model used to generate a result, such as
   its name and a hash or version identifier. Task-specific result types
   (e.g., detection results, classification summaries) can subclass this
   base to attach additional fields while preserving a consistent metadata
   interface.



Classes
-------

.. autoapisummary::

   image_processing.results.ModelResult


Package Contents
----------------

.. py:class:: ModelResult(model_name: Optional[str] = None, model_hash: Optional[str] = None)

   Bases: :py:obj:`abc.ABC`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: model_name
      :value: None



   .. py:attribute:: model_hash
      :value: None



