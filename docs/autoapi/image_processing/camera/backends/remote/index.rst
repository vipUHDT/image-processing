image_processing.camera.backends.remote
=======================================

.. py:module:: image_processing.camera.backends.remote


Attributes
----------

.. autoapisummary::

   image_processing.camera.backends.remote.LOGGER


Classes
-------

.. autoapisummary::

   image_processing.camera.backends.remote.RemoteCamera


Module Contents
---------------

.. py:data:: LOGGER

.. py:class:: RemoteCamera(client: str | None = None, host: str | None = None, username: str | None = None, password: str | None = None)

   Bases: :py:obj:`image_processing.camera.CameraBackend`


   Helper class that provides a standard way to create an ABC using
   inheritance.


   .. py:attribute:: name
      :value: 'RB5 Backend'



   .. py:attribute:: client
      :value: None



   .. py:attribute:: host
      :value: None



   .. py:attribute:: username
      :value: None



   .. py:attribute:: password
      :value: None



   .. py:attribute:: connection_manager
      :type:  Optional[image_processing.connection.ssh.SSH_Controller] | None
      :value: None



   .. py:method:: setConnection(client: str, host: str, username: str, password: str) -> None


   .. py:method:: connect() -> None


   .. py:method:: initializeStream(pipeline) -> None


   .. py:method:: getProcessID(keyword) -> list[str]


   .. py:method:: setGstreamerPid(gstreamer_pid) -> None


   .. py:method:: terminateProcessID(pid: None | str = None)


   .. py:method:: terminateProcessName(pname: None | str)


   .. py:method:: disconect()


   .. py:method:: initialize() -> None


