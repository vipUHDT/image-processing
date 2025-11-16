"""
GStreamer-based camera backends and manager utilities.

This module provides :class:`GStreamerCamera`, a helper class that uses a
:class:`RemoteCamera` backend and GStreamer pipelines to transmit and receive
video streams over UDP. It also defines :class:`GStreamerManager`, a simple
registry for organizing multiple :class:`Camera` instances by name or label.
"""

import logging
LOGGER = logging.getLogger(__name__)

from image_processing.camera.backends import RemoteCamera  
from image_processing.camera import Camera

from typing import TypeAlias

import cv2

from string import Template
GStreamerRemoteConnection: TypeAlias = tuple[str, str, str, str]


class GStreamerCamera():
    """
    Camera backend that streams video using GStreamer and OpenCV.

    This class wraps a :class:`RemoteCamera` instance and manages both
    transmit (TX) and receive (RX) GStreamer pipelines. RX pipelines are
    opened using :func:`cv2.VideoCapture` with the GStreamer backend, while
    TX pipelines are launched remotely over SSH via the underlying
    :class:`RemoteCamera`.

    Parameters
    ----------
    name : str
        Logical name of the camera associated with this backend.
    remote_connection : tuple of (str, str, str, str), optional
        Optional tuple ``(client, host, username, password)`` used to
        construct a :class:`RemoteCamera` on initialization if no
        connection has been set explicitly.

    Attributes
    ----------
    name : str
        Name of the camera associated with this backend.
    tx_pipeline : str or None
        GStreamer pipeline string used for transmitting video (remote side).
    rx_pipeline : str or None
        GStreamer pipeline string used for receiving video (local side).
    pid : str or None
        Process ID of the remote streaming process, if known.
    remote : RemoteCamera or None
        Remote backend used to execute streaming commands over SSH.
    connected : bool
        Flag indicating whether a remote connection has been initialized.
    capture : cv2.VideoCapture or None
        OpenCV capture object used for reading frames from the RX pipeline.
    port : int or None
        UDP port on which the RX/TX pipelines operate.
    """

    def __init__(self, name:str, remote_connection: GStreamerRemoteConnection | None = None):
        self.name = name
        self.tx_pipeline = None
        self.rx_pipeline = None
        self.pid = None
        self.remote_connection: GStreamerRemoteConnection | None = remote_connection
        self.remote : RemoteCamera | None = None
        self.connected = False
        self.capture = None
        self.port = None


    def setConnection(self, client, host, username, password):
        """Create a RemoteCamera with the provided connection parameters.

        Parameters
        ----------
        client : str
            Identifier or address of the client receiving video.
        host : str
            Hostname or IP address of the remote camera host.
        username : str
            Username used to authenticate to the remote host.
        password : str
            Password or credential used to authenticate to the remote host.
        """
        self.remote = RemoteCamera(client, host, username, password)
    
    def setPort(self, port):
        """Set the UDP port used for streaming.

        Parameters
        ----------
        port : int
            UDP port number for the GStreamer TX/RX pipelines.
        """
        self.port = port

    def connect(self):
        """Establish the SSH connection to the remote camera host."""
        if self.remote:
            self.remote.connect()

    def initialize(self):
        """Initialize the remote connection based on configured settings.

        If a :class:`RemoteCamera` has already been created, this method
        connects to it. Otherwise, if a ``remote_connection`` tuple was
        provided at construction time, a new :class:`RemoteCamera` is created
        and connected. If neither is available, an error string is returned.

        Returns
        -------
        None or str
            ``None`` if initialization succeeds, otherwise the string
            ``"Invalid connection"`` when no connection parameters are set.
        """
        if self.remote:
            self.connect()
            return None
        
        elif self.remote_connection:
            client, host, username, password = self.remote_connection
            self.remote = RemoteCamera(client, host, username, password)
            self.connect()
            self.connected = True
            return None
        
        else:
            return "Invalid connection"

    def setTXPipeline(self, pipeline: Template | str):
        """Configure the TX (transmit) GStreamer pipeline.

        If a :class:`Template` is provided, the placeholders ``$client`` and
        ``$port`` are substituted using the remote connection and the local
        port before the pipeline is stored.

        Parameters
        ----------
        pipeline : Template or str
            GStreamer pipeline template or string to use for transmission.
        """
        if self.remote:
            client = self.remote.client
            port = self.port
            if not isinstance(pipeline, Template):
                self.tx_pipeline = pipeline
            else:
                self.tx_pipeline = pipeline.substitute(client = client, port = port)

    
    def setRXPipeline(self, pipeline):
        """Configure the RX (receive) GStreamer pipeline.

        If a :class:`Template` is provided, the placeholder ``$port`` is
        substituted using the configured port before the pipeline is stored.

        Parameters
        ----------
        pipeline : Template or str
            GStreamer pipeline template or string to use for reception.
        """
        self.rx_pipeline = pipeline
        if self.remote:
            port = self.port
            if not isinstance(pipeline, Template):
                self.rx_pipeline = pipeline
            else:
                self.rx_pipeline = pipeline.substitute(port = port)

    def startRXPipeline(self):
        """Open the RX pipeline as an OpenCV VideoCapture stream.

        Raises
        ------
        RuntimeError
            If the RX pipeline is set but the stream fails to open.
        """
        if self.rx_pipeline:
            self.capture = cv2.VideoCapture(self.rx_pipeline, cv2.CAP_GSTREAMER)
            if not self.capture.isOpened():
                raise RuntimeError("Failed to open RTP stream")

    
    def closeRXPipeline(self):
        """Release the OpenCV capture associated with the RX pipeline."""
        if self.capture.isOpened():
            self.capture.release()
    
    def captureFrame(self):
        """Capture a single frame from the RX pipeline.

        Returns
        -------
        Any
            The captured frame, typically a NumPy array in BGR format.
            Returns ``None`` if reading fails.
        """
        ret, frame = self.capture.read()
        return frame

    def initializeStream(self, process_ids, pipeline = None):
        """Start the remote TX pipeline and record its process ID.

        Parameters
        ----------
        process_ids : list of str
            Existing process IDs used to filter out already-known GStreamer
            processes when searching for the new one.
        pipeline : str or Template or None, optional
            Optional explicit pipeline command to use instead of the
            previously configured :attr:`tx_pipeline`.
        """
        if pipeline:
            if self.remote:
                self.remote.initializeStream(pipeline)
                self.pid = self.getGstreamerProcessID(process_ids)
        else:
            if self.remote:
                if self.tx_pipeline:
                    print(self.tx_pipeline)
                    self.remote.initializeStream(self.tx_pipeline)
                    self.pid = self.getGstreamerProcessID(process_ids)


    def getGstreamerProcessID(self, process_ids : list[str]):
        """Identify the newly started GStreamer process ID.

        This method queries the remote host for processes matching ``"gst"``
        and returns the first process ID that is not already present in
        the provided ``process_ids`` list.

        Parameters
        ----------
        process_ids : list of str
            List of process IDs known prior to starting the new pipeline.

        Returns
        -------
        str or None
            The newly detected GStreamer process ID, or ``None`` if no
            suitable process is found.
        """
        if self.remote:
            cmd_output = self.remote.getProcessID("gst")
            if len(cmd_output) > 0:
                for output in cmd_output:
                    if output.replace("\n", "").replace("\r", "") in process_ids:
                        continue
                    return output.replace("\n", "").replace("\r", "")
            else:
                return None
    
    
    def terminate(self):
        """Terminate the associated remote GStreamer process, if any.

        This sends a SIGINT to the recorded process ID via the underlying
        :class:`RemoteCamera`, clears the stored PID, and marks the backend
        as disconnected.
        """
        if self.pid and self.remote:
            self.remote.terminateProcessID(self.pid)
            self.pid = None
            self.connected = False



    
    

class GStreamerManager():
    """
    Registry for managing multiple camera instances by name or label.

    This class stores :class:`Camera` instances in a dictionary, keyed either
    by an explicit label or by the camera's :attr:`name` attribute. It is
    primarily used to organize and access multiple camera controllers in a
    larger imaging system.

    Attributes
    ----------
    cameras : dict of str to Camera
        Mapping from label or camera name to the corresponding camera object.
    """

    def __init__(self):
        """Initialize an empty GStreamerManager."""
        self.cameras : dict[str, Camera] = {}
    
    def addCamera(self, camera : Camera, label : str | None = None) -> None:
        """Register a camera instance with an optional label.

        Parameters
        ----------
        camera : Camera
            Camera instance to register in the manager.
        label : str or None, optional
            Optional label to use as the key. If omitted, the camera's
            :attr:`name` attribute is used instead.
        """
        if label:
            self.cameras['label'] = camera
        else:
            self.cameras[camera.name] = camera



