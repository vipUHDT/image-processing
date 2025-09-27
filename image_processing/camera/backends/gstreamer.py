import logging
LOGGER = logging.getLogger(__name__)

from image_processing.camera.backends import RemoteCamera  
from image_processing.camera import Camera

from typing import TypeAlias

import cv2

from string import Template
GStreamerRemoteConnection: TypeAlias = tuple[str, str, str, str]


class GStreamerCamera():
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
                self.tx_pipeline = pipeline.substitute(client = client, port = port)

    
    def setRXPipeline(self, pipeline):
        self.rx_pipeline = pipeline
        if self.remote:
            port = self.port
            if not isinstance(pipeline, Template):
                self.rx_pipeline = pipeline
            else:
                self.rx_pipeline = pipeline.substitute(port = port)

    def startRXPipeline(self):
        if self.rx_pipeline:
            self.capture = cv2.VideoCapture(self.rx_pipeline, cv2.CAP_GSTREAMER)
            if not self.capture.isOpened():
                raise RuntimeError("Failed to open RTP stream")

    
    def closeRXPipeline(self):
        if self.capture.isOpened():
            self.capture.release()
    
    def captureFrame(self):
        ret, frame = self.capture.read()
        return frame

    def initializeStream(self, process_ids, pipeline = None):
        if pipeline:
            if self.remote:
                self.remote.initializeStream(pipeline)
                self.pid = self.getGstreamerProcessID(process_ids)
        else:
            if self.remote:
                if self.tx_pipeline:
                    self.remote.initializeStream(self.tx_pipeline)
                    self.pid = self.getGstreamerProcessID(process_ids)


    def getGstreamerProcessID(self, process_ids : list[str]):
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



