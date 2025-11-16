"""
Controllers for the FLIR Hadron 640R camera system.

This module defines a high-level controller, :class:`Hadron640R`, that manages
two underlying camera streams: an infrared Boson 640 sensor and an OV64B RGB
sensor. Both cameras are accessed via GStreamer-based backends and can be
initialized and controlled over a remote connection. The helper classes
:class:`Boson640` and :class:`OV64B` provide concrete :class:`Camera`
implementations that configure and manage their respective GStreamer
pipelines.
"""

from typing import Optional
from image_processing.camera import Camera, CameraBackend, constructGstreamerPipeline
from image_processing.camera.backends import RemoteCamera, GStreamerManager, GStreamerCamera
import os, glob
from string import Template

from cv2 import VideoCapture, CAP_GSTREAMER


import logging

LOGGER = logging.getLogger(__name__)


class Hadron640R:
    """
    High-level controller for the Hadron 640R RGB–IR camera pair.

    This class coordinates the OV64B (RGB) and Boson 640 (infrared) cameras
    via a :class:`GStreamerManager`. It configures remote connection
    parameters, initializes GStreamer TX/RX pipelines for each camera, and
    provides a simple interface to capture synchronized RGB and infrared
    frames.

    Attributes
    ----------
    backendManager : GStreamerManager
        Manager that holds and orchestrates the individual camera instances.
    ports : dict of str to int
        Mapping from camera name (e.g., ``"BOSON640"``, ``"OV64B"``) to UDP
        ports used for streaming.
    processes : list
        Internal list used to track process-related information, if needed.
    client : str
        Identifier or address of the local client that receives streamed data.
    host : str
        Hostname or IP of the remote device running the GStreamer pipelines.
    username : str
        Username used for authenticating to the remote host.
    password : str
        Password or credential used for authenticating to the remote host.
    """

    def __init__(self):
        """Initialize the Hadron 640R controller and default port mapping."""
        self.backendManager = GStreamerManager()
        self.ports = {
            'BOSON640': 5000,
            'OV64B': 6000
        }
        self.processes = []
    
    def getProcessIds(self):
        """Retrieve process IDs for remote GStreamer processes.

        This method connects to the remote camera host, queries for processes
        matching the string ``"gst"`` (e.g., GStreamer pipelines), and returns
        a list of cleaned process identifiers.

        Returns
        -------
        list of str
            List of process IDs that match the GStreamer search on the remote
            host. Returns an empty list if connection details are incomplete
            or no matching processes are found.
        """
        process_ids = []
        if all((self.client, self.host, self.username, self.password)):
            hadron = RemoteCamera(self.client, self.host, self.username, self.password)
            hadron.connect()
            raw_process_ids = hadron.getProcessID("gst")
            process_ids = [process_id.replace("\n", "").replace("\r", "") for process_id in raw_process_ids]
        return process_ids

    
    def setConnection(self, client, host, username, password):
        """Set remote connection credentials for the Hadron system.

        Parameters
        ----------
        client : str
            Address or identifier of the client that receives streamed video.
        host : str
            Hostname or IP address of the remote device running the cameras.
        username : str
            Username used to authenticate to the remote host.
        password : str
            Password or credential used to authenticate to the remote host.
        """
        self.client = client
        self.host = host
        self.username = username 
        self.password = password



    def initialize(self):
        """Instantiate and configure OV64B and Boson640 camera pipelines.

        This method:
        1. Adds :class:`OV64B` and :class:`Boson640` camera instances to the
           backend manager.
        2. Propagates remote connection information to each camera.
        3. Sets per-camera UDP ports.
        4. Configures TX and RX GStreamer pipelines.
        5. Initializes each camera and its stream.
        6. Starts the RX pipelines so frames can be captured.
        """
        self.backendManager.addCamera(OV64B())
        self.backendManager.addCamera(Boson640())
        
        self.backendManager.cameras["OV64B"].setConnection(self.client, self.host, self.username, self.password)
        self.backendManager.cameras["BOSON640"].setConnection(self.client, self.host, self.username, self.password)
        
        self.backendManager.cameras["OV64B"].setPort(self.ports["OV64B"])
        self.backendManager.cameras["BOSON640"].setPort(self.ports["BOSON640"])
        
        self.backendManager.cameras["OV64B"].setTXPipeline()
        self.backendManager.cameras["BOSON640"].setTXPipeline()

        self.backendManager.cameras["OV64B"].setRXPipeline()
        self.backendManager.cameras["BOSON640"].setRXPipeline()
        
        self.backendManager.cameras["OV64B"].initialize()
        self.backendManager.cameras["OV64B"].initializeStream(self.getProcessIds())

        self.backendManager.cameras["BOSON640"].initialize()
        self.backendManager.cameras["BOSON640"].initializeStream(self.getProcessIds())

        self.backendManager.cameras["OV64B"].startRXPipeline()
        self.backendManager.cameras["BOSON640"].startRXPipeline()


    def capture(self):
        """Capture one RGB frame and one infrared frame from the Hadron system.

        Returns
        -------
        tuple
            A pair ``(rgb_img, infrared_img)`` where:

            * ``rgb_img`` is a frame from the OV64B RGB camera (typically a
              BGR NumPy array).
            * ``infrared_img`` is a frame from the Boson 640 infrared camera.
        """
        rgb_img = self.backendManager.cameras["OV64B"].backend.captureFrame()
        infrared_img = self.backendManager.cameras["BOSON640"].backend.captureFrame()
        return rgb_img, infrared_img
        
    def terminate(self):
        """Stop RX pipelines and terminate both camera streams.

        This closes the RX pipelines and tears down the underlying GStreamer
        processes for both the OV64B and Boson 640 cameras.
        """
        self.backendManager.cameras["OV64B"].closeRXPipeline()
        self.backendManager.cameras["BOSON640"].closeRXPipeline()

        self.backendManager.cameras["OV64B"].terminate()
        self.backendManager.cameras["BOSON640"].terminate()

class Boson640(Camera):
    """
    Concrete camera wrapper for the Boson 640 infrared sensor.

    This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
    backend to configure and manage TX and RX GStreamer pipelines for the
    Boson 640 stream. It exposes convenience methods for setting ports,
    pipelines, and capturing frames.

    Attributes
    ----------
    backend : GStreamerCamera
        Backend responsible for running the GStreamer pipelines.
    RX_TEMPLATE : Template
        Default GStreamer RX pipeline template used to receive H.264 video
        over UDP and convert it into a BGR stream.
    TX_TEMPLATE : Template
        Default GStreamer TX pipeline template used to stream video from
        ``/dev/video0`` over UDP to the client.
    """

    def __init__(self):
        """Initialize the Boson 640 camera wrapper and default pipelines."""
        super().__init__("BOSON640")
        self.backend = GStreamerCamera(self.name)
        self.RX_TEMPLATE = Template(" ! ".join((
            "udpsrc port=$port caps=application/x-rtp,media=video,encoding-name=H264,payload=96",
            "rtph264depay",
            "avdec_h264",
            "videoconvert",
            "video/x-raw,format=BGR",
            "appsink drop=true max-buffers=1 sync=false"
        )))
        self.TX_TEMPLATE = Template(" ! ".join((
            "gst-launch-1.0 v4l2src device=/dev/video0 io-mode=2",
            "video/x-raw,format=NV12,width=640,height=512,framerate=30/1",
            "videoconvert ! video/x-raw,format=I420",
            "x264enc tune=zerolatency speed-preset=veryfast bitrate=2500 key-int-max=60 bframes=0 byte-stream=true",
            "h264parse",
            "video/x-h264,stream-format=byte-stream,alignment=au",
             "rtph264pay pt=96 mtu=1200 config-interval=1",
             "udpsink host=$client port=$port sync=false async=false"
        )))
    
    
    def setPort(self, port):
        """Set the UDP port used by the Boson 640 backend.

        Parameters
        ----------
        port : int
            UDP port number on which to send or receive the Boson 640 stream.
        """
        self.backend.port = port

    def setTXPipeline(self, pipeline: Template | str | None = None):
        """Configure the TX (transmit) pipeline for the Boson 640 stream.

        Parameters
        ----------
        pipeline : Template or str or None, optional
            Custom TX pipeline to use. If ``None``, the default
            :attr:`TX_TEMPLATE` is applied.
        """
        if pipeline:
            self.backend.setTXPipeline(pipeline)
        else:
            self.backend.setTXPipeline(self.TX_TEMPLATE)

       

    def setRXPipeline(self, pipeline: Template | str | None = None):
        """Configure the RX (receive) pipeline for the Boson 640 stream.

        Parameters
        ----------
        pipeline : Template or str or None, optional
            Custom RX pipeline to use. If ``None``, the default
            :attr:`RX_TEMPLATE` is applied.
        """
        if pipeline:
            self.backend.setRXPipeline(pipeline)
        else:
            self.backend.setRXPipeline(self.RX_TEMPLATE)
    
    def startRXPipeline(self):
        """Start the RX pipeline so that frames can be received."""
        self.backend.startRXPipeline()

    def captureFrame(self):
       """Capture a single infrared frame from the Boson 640 stream.

        Returns
        -------
        Any
            The captured frame, typically a BGR NumPy array produced by the
            GStreamer pipeline.
        """
       return self.backend.captureFrame()

    def closeRXPipeline(self):
        """Stop and close the RX pipeline for the Boson 640 stream."""
        self.backend.closeRXPipeline()
       

    def initialize(self):
        """Initialize the Boson 640 backend and allocate required resources."""
        self.backend.initialize()
    
    def initializeStream(self, pids):
        """Initialize the Boson 640 stream, optionally using process IDs.

        Parameters
        ----------
        pids : list
            List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
            used by the backend to manage or attach to running pipelines.
        """
        self.backend.initializeStream(pids)

    def terminate(self):
        """Terminate the Boson 640 backend and clean up resources."""
        self.backend.terminate()

    
       


class OV64B(Camera):
    """
    Concrete camera wrapper for the OV64B RGB sensor.

    This class subclasses :class:`Camera` and uses a :class:`GStreamerCamera`
    backend to configure and manage TX and RX GStreamer pipelines for the
    OV64B RGB stream. It exposes convenience methods for setting ports,
    pipelines, and capturing frames.

    Attributes
    ----------
    backend : GStreamerCamera
        Backend responsible for running the GStreamer pipelines.
    RX_TEMPLATE : Template
        Default GStreamer RX pipeline template used to receive H.264 video
        over UDP and convert it into a BGR stream.
    TX_TEMPLATE : Template
        Default GStreamer TX pipeline template used to stream video from
        the OV64B source over UDP to the client.
    """

    def __init__(self):
        """Initialize the OV64B camera wrapper and default pipelines."""
        super().__init__("OV64B")
        self.backend = GStreamerCamera(self.name)
        self.RX_TEMPLATE = Template(" ! ".join((
            "udpsrc port=$port caps=application/x-rtp,media=video,encoding-name=H264,payload=96",
            "rtph264depay",
            "avdec_h264",
            "videoconvert",
            "video/x-raw,format=BGR",
            "appsink drop=true max-buffers=1 sync=false"
        )))
        self.TX_TEMPLATE = Template(" ! ".join((
            "gst-pipeline-app -e qtiqmmfsrc name=qmmf",
             "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1",
            "videoconvert",
            "video/x-raw,format=I420",
            "x264enc tune=zerolatency speed-preset=veryfast bitrate=6000 key-int-max=60 bframes=0 byte-stream=true",
            "h264parse",
            "video/x-h264,stream-format=byte-stream,alignment=au",
            "rtph264pay pt=96 mtu=1200 config-interval=1",
            "udpsink host=$client port=$port sync=false async=false"
        )))
    
    
    def setPort(self, port):
        """Set the UDP port used by the OV64B backend.

        Parameters
        ----------
        port : int
            UDP port number on which to send or receive the OV64B stream.
        """
        self.backend.port = port

    def setTXPipeline(self, pipeline: Template | str | None = None):
        """Configure the TX (transmit) pipeline for the OV64B stream.

        Parameters
        ----------
        pipeline : Template or str or None, optional
            Custom TX pipeline to use. If ``None``, the default
            :attr:`TX_TEMPLATE` is applied.
        """
        if pipeline:
            self.backend.setTXPipeline(pipeline)
        else:
            self.backend.setTXPipeline(self.TX_TEMPLATE)

    
    def startRXPipeline(self):
        """Start the RX pipeline so that frames can be received."""
        self.backend.startRXPipeline()

    def setRXPipeline(self, pipeline: Template | str | None = None):
        """Configure the RX (receive) pipeline for the OV64B stream.

        Parameters
        ----------
        pipeline : Template or str or None, optional
            Custom RX pipeline to use. If ``None``, the default
            :attr:`RX_TEMPLATE` is applied.
        """
        if pipeline:
            self.backend.setRXPipeline(pipeline)
        else:
            self.backend.setRXPipeline(self.RX_TEMPLATE)

    def captureFrame(self):
       """Capture a single RGB frame from the OV64B stream.

        Returns
        -------
        Any
            The captured frame, typically a BGR NumPy array produced by the
            GStreamer pipeline.
        """
       return self.backend.captureFrame()

    def closeRXPipeline(self):
        """Stop and close the RX pipeline for the OV64B stream."""
        self.backend.closeRXPipeline()
       

    def initialize(self):
        """Initialize the OV64B backend and allocate required resources."""
        self.backend.initialize()
    
    def initializeStream(self, pids):
        """Initialize the OV64B stream, optionally using process IDs.

        Parameters
        ----------
        pids : list
            List of process identifiers (e.g., from :meth:`Hadron640R.getProcessIds`)
            used by the backend to manage or attach to running pipelines.
        """
        self.backend.initializeStream(pids)

    def terminate(self):
        """Terminate the OV64B backend and clean up resources."""
        self.backend.terminate()