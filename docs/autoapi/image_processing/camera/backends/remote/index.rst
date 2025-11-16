image_processing.camera.backends.remote
=======================================

.. py:module:: image_processing.camera.backends.remote

.. autoapi-nested-parse::

   Remote camera backend implementation using SSH-based control.

   This module provides :class:`RemoteCamera`, a :class:`CameraBackend`
   implementation that interacts with a remote device over an SSH connection.
   It supports establishing connections, launching remote commands related
   to camera streaming (e.g., GStreamer pipelines), retrieving remote process
   IDs, and terminating running streaming processes.



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


   Backend that communicates with a remote camera host using SSH.

   This backend is intended for camera systems that do not run locally
   and require remote command execution to configure, initialize, or
   manage streaming pipelines (e.g., via GStreamer). It assumes that
   the remote endpoint supports process management and allows launching
   background commands over SSH.

   :param client: Identifier for the client receiving streamed data (e.g., its hostname or IP).
   :type client: str or None, optional
   :param host: Hostname or IP address of the remote device where camera processes run.
   :type host: str or None, optional
   :param username: Username for SSH authentication.
   :type username: str or None, optional
   :param password: Password or credential used for SSH authentication.
   :type password: str or None, optional

   .. attribute:: name

      Identifier for the backend, default is ``"RB5 Backend"``.

      :type: str

   .. attribute:: connection_manager

      Active SSH connection wrapper once :meth:`connect` is called.

      :type: SSH_Controller or None


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

      Update SSH connection credentials.

      :param client: Identifier of the local client receiving video.
      :type client: str
      :param host: Hostname or IP of the remote SSH device.
      :type host: str
      :param username: Username used for authentication.
      :type username: str
      :param password: Password or credential used for authentication.
      :type password: str



   .. py:method:: connect() -> None

      Create and open an SSH connection to the remote camera host.



   .. py:method:: initializeStream(pipeline) -> None

      Launch a streaming pipeline remotely in the background.

      :param pipeline: Command or pipeline string to execute remotely, such as
                       a GStreamer launch command. Executed in background mode.
      :type pipeline: str



   .. py:method:: getProcessID(keyword) -> list[str]

      Query remote process IDs that match a given keyword.

      :param keyword: Search term used with ``pgrep`` to filter process names.
      :type keyword: str

      :returns: List of matching process IDs returned by the remote host.
                Returns an empty list if no connection is active.
      :rtype: list of str



   .. py:method:: setGstreamerPid(gstreamer_pid) -> None

      Store a process ID associated with a remote GStreamer pipeline.

      :param gstreamer_pid: Process ID to be stored for later termination or tracking.
      :type gstreamer_pid: str or None



   .. py:method:: terminateProcessID(pid: None | str = None)

      Terminate a remote process by PID using SIGINT.

      :param pid: Remote PID to terminate. If ``None``, no action is taken.
      :type pid: str or None

      :returns: Output from the remote command, if executed.
      :rtype: Any



   .. py:method:: terminateProcessName(pname: None | str)

      Terminate remote processes that match a process name.

      :param pname: Name used with ``pkill`` to terminate matching processes.
      :type pname: str or None

      :returns: Output from the remote command, if executed.
      :rtype: Any



   .. py:method:: disconnect()

      Disconnect the active SSH session.



   .. py:method:: initialize() -> None

      Initialize the backend by establishing the SSH connection.



