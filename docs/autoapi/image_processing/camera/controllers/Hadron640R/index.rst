image_processing.camera.controllers.Hadron640R
==============================================

.. py:module:: image_processing.camera.controllers.Hadron640R


Attributes
----------

.. autoapisummary::

   image_processing.camera.controllers.Hadron640R.LOGGER
   image_processing.camera.controllers.Hadron640R.hadrond640


Classes
-------

.. autoapisummary::

   image_processing.camera.controllers.Hadron640R.Hadron640R
   image_processing.camera.controllers.Hadron640R.Boson640
   image_processing.camera.controllers.Hadron640R.OV64B


Module Contents
---------------

.. py:data:: LOGGER

.. py:class:: Hadron640R

   .. py:attribute:: backendManager


   .. py:attribute:: ports


   .. py:attribute:: processes
      :value: []



   .. py:method:: getProcessIds()


   .. py:method:: setConnection(client, host, username, password)


   .. py:method:: initialize()


   .. py:method:: capture()


   .. py:method:: terminate()


.. py:class:: Boson640

   Bases: :py:obj:`image_processing.camera.Camera`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)


   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: startRXPipeline()


   .. py:method:: captureFrame()


   .. py:method:: closeRXPipeline()


   .. py:method:: initialize()


   .. py:method:: initializeStream(pids)


   .. py:method:: terminate()


.. py:class:: OV64B

   Bases: :py:obj:`image_processing.camera.Camera`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)


   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: startRXPipeline()


   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)


   .. py:method:: captureFrame()


   .. py:method:: closeRXPipeline()


   .. py:method:: initialize()


   .. py:method:: initializeStream(pids)


   .. py:method:: terminate()


.. py:data:: hadrond640

