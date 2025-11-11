image_processing.camera.backends.gstreamer
==========================================

.. py:module:: image_processing.camera.backends.gstreamer


Attributes
----------

.. autoapisummary::

   image_processing.camera.backends.gstreamer.LOGGER
   image_processing.camera.backends.gstreamer.GStreamerRemoteConnection


Classes
-------

.. autoapisummary::

   image_processing.camera.backends.gstreamer.GStreamerCamera
   image_processing.camera.backends.gstreamer.GStreamerManager


Module Contents
---------------

.. py:data:: LOGGER

.. py:type:: GStreamerRemoteConnection
   :canonical: tuple[str, str, str, str]


.. py:class:: GStreamerCamera(name: str, remote_connection: GStreamerRemoteConnection | None = None)

   .. py:attribute:: name


   .. py:attribute:: tx_pipeline
      :value: None



   .. py:attribute:: rx_pipeline
      :value: None



   .. py:attribute:: pid
      :value: None



   .. py:attribute:: remote_connection
      :type:  GStreamerRemoteConnection | None
      :value: None



   .. py:attribute:: remote
      :type:  image_processing.camera.backends.RemoteCamera | None
      :value: None



   .. py:attribute:: connected
      :value: False



   .. py:attribute:: capture
      :value: None



   .. py:attribute:: port
      :value: None



   .. py:method:: setConnection(client, host, username, password)


   .. py:method:: setPort(port)


   .. py:method:: connect()


   .. py:method:: initialize()


   .. py:method:: setTXPipeline(pipeline: string.Template | str)


   .. py:method:: setRXPipeline(pipeline)


   .. py:method:: startRXPipeline()


   .. py:method:: closeRXPipeline()


   .. py:method:: captureFrame()


   .. py:method:: initializeStream(process_ids, pipeline=None)


   .. py:method:: getGstreamerProcessID(process_ids: list[str])


   .. py:method:: terminate()


.. py:class:: GStreamerManager

   .. py:attribute:: cameras
      :type:  dict[str, image_processing.camera.Camera]


   .. py:method:: addCamera(camera: image_processing.camera.Camera, label: str | None = None) -> None


