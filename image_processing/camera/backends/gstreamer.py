import logging
LOGGER = logging.getLogger(__name__)

from image_processing.camera.backends import RemoteCamera  
from image_processing.camera import Camera

from typing import TypeAlias

import cv2

from string import Template
GStreamerRemoteConnection: TypeAlias = tuple[str, str, str, str]


class GStreamerCamera():
    def __init__(self, name: str,
                 remote_connection: GStreamerRemoteConnection | None = None):
        self.name = name
        self.tx_pipeline = None
        self.rx_pipeline = None
        self.pid = None
        self.remote_connection: GStreamerRemoteConnection | None = remote_connection
        self.remote: RemoteCamera | None = None
        self.connected = False
        self.capture: BufferlessVideoCapture | None = None
        self.port = None

    def setConnection(self, client, host, username, password):
        self.remote = RemoteCamera(client, host, username, password)
    
    def setPort(self, port):
        self.port = port

    def connect(self):
        if self.remote:
            self.remote.connect()

    def initialize(self):
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
        if self.remote:
            client = self.remote.client
            port = self.port
            if not isinstance(pipeline, Template):
                self.tx_pipeline = pipeline
            else:
                self.tx_pipeline = pipeline.substitute(client=client, port=port)

    def setRXPipeline(self, pipeline):
        self.rx_pipeline = pipeline
        if self.remote:
            client = self.remote.client
            port = self.port
            if not isinstance(pipeline, Template):
                self.rx_pipeline = pipeline
            else:
                self.rx_pipeline = pipeline.substitute(client=client, port=port)

    def startRXPipeline(self):
        """Start receiving frames via GStreamer, using a bufferless capture."""
        if not self.rx_pipeline:
            raise RuntimeError("RX pipeline not set")

        print(self.rx_pipeline)

        # Use CAP_GSTREAMER so OpenCV treats the string as a GStreamer pipeline
        self.capture = BufferlessVideoCapture(
            self.rx_pipeline,
            api_preference=cv2.CAP_GSTREAMER
        )

        if not self.capture.isOpened():
            self.capture = None
            raise RuntimeError("Failed to open RTP stream")

    def closeRXPipeline(self):
        """Stop receiving frames and release the capture."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def captureFrame(self, timeout=None):
        """
        Return the latest frame from the stream.

        timeout:
          - None: block until a frame is available
          - float: max seconds to wait (queue.Empty is raised if no frame)
        """
        if self.capture is None:
            raise RuntimeError("RX pipeline not started")

        try:
            frame = self.capture.read(timeout=timeout)
        except queue.Empty:
            # No frame available within timeout; up to you what to return
            return None

        return frame

    def initializeStream(self, process_ids, pipeline=None):
        if pipeline:
            if self.remote:
                self.remote.initializeStream(pipeline)
                self.pid = self.getGstreamerProcessID(process_ids)
        else:
            if self.remote and self.tx_pipeline:
                print(self.tx_pipeline)
                self.remote.initializeStream(self.tx_pipeline)
                self.pid = self.getGstreamerProcessID(process_ids)

    def getGstreamerProcessID(self, process_ids: list[str]):
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
        if self.pid and self.remote:
            self.remote.terminateProcessID(self.pid)
            self.remote.cleanLogFiles()
            self.pid = None
            self.connected = False



    
    

class GStreamerManager():
    def __init__(self):
        self.cameras : dict[str, Camera] = {}
    
    def addCamera(self, camera : Camera, label : str | None = None) -> None:
        if label:
            self.cameras['label'] = camera
        else:
            self.cameras[camera.name] = camera


import cv2
import queue
import threading

class BufferlessVideoCapture:

    def __init__(self, src, api_preference=cv2.CAP_ANY):
        self.cap = cv2.VideoCapture(src, api_preference)
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open video source")

        self.q: queue.Queue = queue.Queue()
        self._stopped = False

        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def _reader(self):
        while not self._stopped:
            ret, frame = self.cap.read()
            if not ret:
                break


            if not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    pass

            self.q.put(frame)

 
        self._stopped = True

    def read(self, timeout=None):
    
        return self.q.get(timeout=timeout)

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self._stopped = True
        if self.cap.isOpened():
            self.cap.release()

        # Clear any buffered frame
        with self.q.mutex:
            self.q.queue.clear()


