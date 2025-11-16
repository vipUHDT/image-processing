image_processing.camera.controllers.Hadron640R
==============================================

.. py:module:: image_processing.camera.controllers.Hadron640R

.. autoapi-nested-parse::

   Controllers for the FLIR Hadron 640R camera system.

   This module defines a high-level controller, :class:`Hadron640R`, that manages
   two underlying camera streams: an infrared Boson 640 sensor and an OV64B RGB
   sensor. Both cameras are accessed via GStreamer-based backends and can be
   initialized and controlled over a remote connection. The helper classes
   :class:`Boson640` and :class:`OV64B` provide concrete :class:`Camera`
   implementations that configure and manage their respective GStreamer
   pipelines.



Attributes
----------

.. autoapisummary::

   image_processing.camera.controllers.Hadron640R.LOGGER


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

   High-level controller for the Hadron 640R RGB–IR camera pair.

   This class coordinates the OV64B (RGB) and Boson 640 (infrared) cameras
   via a :class:`GStreamerManager`. It configures remote connection
   parameters, initializes GStreamer TX/RX pipelines for each camera, and
   provides a simple interface to capture synchronized RGB and infrared
   frames.

   .. attribute:: backendManager

      Manager that holds and orchestrates the individual camera instances.

      :type: GStreamerManager

   .. attribute:: ports

      Mapping from camera name (e.g., ``"BOSON640"``, ``"OV64B"``) to UDP
      ports used for streaming.

      :type: dict of str to int

   .. attribute:: processes

      Internal list used to track process-related information, if needed.

      :type: list

   .. attribute:: client

      Identifier or address of the local client that receives streamed data.

      :type: str

   .. attribute:: host

      Hostname or IP of the remote device running the GStreamer pipelines.

      :type: str

   .. attribute:: username

      Username used for authenticating to the remote host.

      :type: str

   .. attribute:: password

      Password or credential used for authenticating to the remote host.

      :type: str


   .. py:attribute:: backendManager


   .. py:attribute:: ports


   .. py:attribute:: processes
      :value: []



   .. py:method:: getProcessIds()

      Retrieve process IDs for remote GStreamer processes.

      This method connects to the remote camera host, queries for processes
      matching the string ``"gst"`` (e.g., GStreamer pipelines), and returns
      a list of cleaned process identifiers.

      :returns: List of process IDs that match the GStreamer search on the remote
                host. Returns an empty list if connection details are incomplete
                or no matching processes are found.
      :rtype: list of str



   .. py:method:: setConnection(client, host, username, password)

      Set remote connection credentials for the Hadron system.

      :param client: Address or identifier of the client that receives streamed video.
      :type client: str
      :param host: Hostname or IP address of the remote device running the cameras.
      :type host: str
      :param username: Username used to authenticate to the remote host.
      :type username: str
      :param password: Password or credential used to authenticate to the remote host.
      :type password: str



   .. py:method:: initialize()

      Instantiate and configure OV64B and Boson640 camera pipelines.

      This method:
      1. Adds :class:`OV64B` and :class:`Boson640` camera instances to the
         backend manager.
      2. Propagates remote connection information to each camera.
      3. Sets per-camera UDP ports.
      4. Configures TX and RX GStreamer pipelines.
      5. Initializes each camera and its stream.
      6. Starts the RX pipelines so frames can be captured.



   .. py:method:: capture()

      Capture one RGB frame and one infrared frame from the Hadron system.

      :returns: A pair ``(rgb_img, infrared_img)`` where:

                * ``rgb_img`` is a frame from the OV64B RGB camera (typically a
                  BGR NumPy array).
                * ``infrared_img`` is a frame from the Boson 640 infrared camera.
      :rtype: tuple



   .. py:method:: terminate()

      Stop RX pipelines and terminate both camera streams.

      This closes the RX pipelines and tears down the underlying GStreamer
      processes for both the OV64B and Boson 640 cameras.



.. py:class:: Boson640

   Bases: :py:obj:`image_processing.camera.Camera`


   Concrete camera wrapper for the Boson 640 infrared sensor.

   This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
   backend to configure and manage TX and RX GStreamer pipelines for the
   Boson 640 stream. It exposes convenience methods for setting ports,
   pipelines, and capturing frames.

   .. attribute:: backend

      Backend responsible for running the GStreamer pipelines.

      :type: GStreamerCamera

   .. attribute:: RX_TEMPLATE

      Default GStreamer RX pipeline template used to receive H.264 video
      over UDP and convert it into a BGR stream.

      :type: Template

   .. attribute:: TX_TEMPLATE

      Default GStreamer TX pipeline template used to stream video from
      ``/dev/video0`` over UDP to the client.

      :type: Template


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)

      Set the UDP port used by the Boson 640 backend.

      :param port: UDP port number on which to send or receive the Boson 640 stream.
      :type port: int



   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)

      Configure the TX (transmit) pipeline for the Boson 640 stream.

      :param pipeline: Custom TX pipeline to use. If ``None``, the default
                       :attr:`TX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)

      Configure the RX (receive) pipeline for the Boson 640 stream.

      :param pipeline: Custom RX pipeline to use. If ``None``, the default
                       :attr:`RX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: startRXPipeline()

      Start the RX pipeline so that frames can be received.



   .. py:method:: captureFrame()

      Capture a single infrared frame from the Boson 640 stream.

      :returns: The captured frame, typically a BGR NumPy array produced by the
                GStreamer pipeline.
      :rtype: Any



   .. py:method:: closeRXPipeline()

      Stop and close the RX pipeline for the Boson 640 stream.



   .. py:method:: initialize()

      Initialize the Boson 640 backend and allocate required resources.



   .. py:method:: initializeStream(pids)

      Initialize the Boson 640 stream, optionally using process IDs.

      :param pids: List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
                   used by the backend to manage or attach to running pipelines.
      :type pids: list



   .. py:method:: terminate()

      Terminate the Boson 640 backend and clean up resources.



.. py:class:: OV64B

   Bases: :py:obj:`image_processing.camera.Camera`


   Concrete camera wrapper for the OV64B RGB sensor.

   This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
   backend to configure and manage TX and RX GStreamer pipelines for the
   OV64B RGB stream. It exposes convenience methods for setting ports,
   pipelines, and capturing frames.

   .. attribute:: backend

      Backend responsible for running the GStreamer pipelines.

      :type: GStreamerCamera

   .. attribute:: RX_TEMPLATE

      Default GStreamer RX pipeline template used to receive H.264 video
      over UDP and convert it into a BGR stream.

      :type: Template

   .. attribute:: TX_TEMPLATE

      Default GStreamer TX pipeline template used to stream video from
      the OV64B source over UDP to the client.

      :type: Template


   .. py:attribute:: backend


   .. py:attribute:: RX_TEMPLATE


   .. py:attribute:: TX_TEMPLATE


   .. py:method:: setPort(port)

      Set the UDP port used by the OV64B backend.

      :param port: UDP port number on which to send or receive the OV64B stream.
      :type port: int



   .. py:method:: setTXPipeline(pipeline: string.Template | str | None = None)

      Configure the TX (transmit) pipeline for the OV64B stream.

      :param pipeline: Custom TX pipeline to use. If ``None``, the default
                       :attr:`TX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: startRXPipeline()

      Start the RX pipeline so that frames can be received.



   .. py:method:: setRXPipeline(pipeline: string.Template | str | None = None)

      Configure the RX (receive) pipeline for the OV64B stream.

      :param pipeline: Custom RX pipeline to use. If ``None``, the default
                       :attr:`RX_TEMPLATE` is applied.
      :type pipeline: Template or str or None, optional



   .. py:method:: captureFrame()

      Capture a single RGB frame from the OV64B stream.

      :returns: The captured frame, typically a BGR NumPy array produced by the
                GStreamer pipeline.
      :rtype: Any



   .. py:method:: closeRXPipeline()

      Stop and close the RX pipeline for the OV64B stream.



   .. py:method:: initialize()

      Initialize the OV64B backend and allocate required resources.



   .. py:method:: initializeStream(pids)

      Initialize the OV64B stream, optionally using process IDs.

      :param pids: List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
                   used by the backend to manage or attach to running pipelines.
      :type pids: list



   .. py:method:: terminate()

      Terminate the OV64B backend and clean up resources.



