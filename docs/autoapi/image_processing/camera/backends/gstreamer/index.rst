image_processing.camera.backends.gstreamer
==========================================

.. py:module:: image_processing.camera.backends.gstreamer

.. autoapi-nested-parse::

   GStreamer-based camera backends and manager utilities.

   This module provides :class:`GStreamerCamera`, a helper class that uses a
   :class:`RemoteCamera` backend and GStreamer pipelines to transmit and receive
   video streams over UDP. It also defines :class:`GStreamerManager`, a simple
   registry for organizing multiple :class:`Camera` instances by name or label.



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

   Camera backend that streams video using GStreamer and OpenCV.

   This class wraps a :class:`RemoteCamera` instance and manages both
   transmit (TX) and receive (RX) GStreamer pipelines. RX pipelines are
   opened using :func:`cv2.VideoCapture` with the GStreamer backend, while
   TX pipelines are launched remotely over SSH via the underlying
   :class:`RemoteCamera`.

   :param name: Logical name of the camera associated with this backend.
   :type name: str
   :param remote_connection: Optional tuple ``(client, host, username, password)`` used to
                             construct a :class:`RemoteCamera` on initialization if no
                             connection has been set explicitly.
   :type remote_connection: tuple of (str, str, str, str), optional

   .. attribute:: name

      Name of the camera associated with this backend.

      :type: str

   .. attribute:: tx_pipeline

      GStreamer pipeline string used for transmitting video (remote side).

      :type: str or None

   .. attribute:: rx_pipeline

      GStreamer pipeline string used for receiving video (local side).

      :type: str or None

   .. attribute:: pid

      Process ID of the remote streaming process, if known.

      :type: str or None

   .. attribute:: remote

      Remote backend used to execute streaming commands over SSH.

      :type: RemoteCamera or None

   .. attribute:: connected

      Flag indicating whether a remote connection has been initialized.

      :type: bool

   .. attribute:: capture

      OpenCV capture object used for reading frames from the RX pipeline.

      :type: cv2.VideoCapture or None

   .. attribute:: port

      UDP port on which the RX/TX pipelines operate.

      :type: int or None


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

      Create a RemoteCamera with the provided connection parameters.

      :param client: Identifier or address of the client receiving video.
      :type client: str
      :param host: Hostname or IP address of the remote camera host.
      :type host: str
      :param username: Username used to authenticate to the remote host.
      :type username: str
      :param password: Password or credential used to authenticate to the remote host.
      :type password: str



   .. py:method:: setPort(port)

      Set the UDP port used for streaming.

      :param port: UDP port number for the GStreamer TX/RX pipelines.
      :type port: int



   .. py:method:: connect()

      Establish the SSH connection to the remote camera host.



   .. py:method:: initialize()

      Initialize the remote connection based on configured settings.

      If a :class:`RemoteCamera` has already been created, this method
      connects to it. Otherwise, if a ``remote_connection`` tuple was
      provided at construction time, a new :class:`RemoteCamera` is created
      and connected. If neither is available, an error string is returned.

      :returns: ``None`` if initialization succeeds, otherwise the string
                ``"Invalid connection"`` when no connection parameters are set.
      :rtype: None or str



   .. py:method:: setTXPipeline(pipeline: string.Template | str)

      Configure the TX (transmit) GStreamer pipeline.

      If a :class:`Template` is provided, the placeholders ``$client`` and
      ``$port`` are substituted using the remote connection and the local
      port before the pipeline is stored.

      :param pipeline: GStreamer pipeline template or string to use for transmission.
      :type pipeline: Template or str



   .. py:method:: setRXPipeline(pipeline)

      Configure the RX (receive) GStreamer pipeline.

      If a :class:`Template` is provided, the placeholder ``$port`` is
      substituted using the configured port before the pipeline is stored.

      :param pipeline: GStreamer pipeline template or string to use for reception.
      :type pipeline: Template or str



   .. py:method:: startRXPipeline()

      Open the RX pipeline as an OpenCV VideoCapture stream.

      :raises RuntimeError: If the RX pipeline is set but the stream fails to open.



   .. py:method:: closeRXPipeline()

      Release the OpenCV capture associated with the RX pipeline.



   .. py:method:: captureFrame()

      Capture a single frame from the RX pipeline.

      :returns: The captured frame, typically a NumPy array in BGR format.
                Returns ``None`` if reading fails.
      :rtype: Any



   .. py:method:: initializeStream(process_ids, pipeline=None)

      Start the remote TX pipeline and record its process ID.

      :param process_ids: Existing process IDs used to filter out already-known GStreamer
                          processes when searching for the new one.
      :type process_ids: list of str
      :param pipeline: Optional explicit pipeline command to use instead of the
                       previously configured :attr:`tx_pipeline`.
      :type pipeline: str or Template or None, optional



   .. py:method:: getGstreamerProcessID(process_ids: list[str])

      Identify the newly started GStreamer process ID.

      This method queries the remote host for processes matching ``"gst"``
      and returns the first process ID that is not already present in
      the provided ``process_ids`` list.

      :param process_ids: List of process IDs known prior to starting the new pipeline.
      :type process_ids: list of str

      :returns: The newly detected GStreamer process ID, or ``None`` if no
                suitable process is found.
      :rtype: str or None



   .. py:method:: terminate()

      Terminate the associated remote GStreamer process, if any.

      This sends a SIGINT to the recorded process ID via the underlying
      :class:`RemoteCamera`, clears the stored PID, and marks the backend
      as disconnected.



.. py:class:: GStreamerManager

   Registry for managing multiple camera instances by name or label.

   This class stores :class:`Camera` instances in a dictionary, keyed either
   by an explicit label or by the camera's :attr:`name` attribute. It is
   primarily used to organize and access multiple camera controllers in a
   larger imaging system.

   .. attribute:: cameras

      Mapping from label or camera name to the corresponding camera object.

      :type: dict of str to Camera


   .. py:attribute:: cameras
      :type:  dict[str, image_processing.camera.Camera]


   .. py:method:: addCamera(camera: image_processing.camera.Camera, label: str | None = None) -> None

      Register a camera instance with an optional label.

      :param camera: Camera instance to register in the manager.
      :type camera: Camera
      :param label: Optional label to use as the key. If omitted, the camera's
                    :attr:`name` attribute is used instead.
      :type label: str or None, optional



