from typing import Optional
from image_processing.camera import Camera, CameraBackend
from image_processing.camera.backends import RB5Backend

import logging

LOGGER = logging.getLogger(__name__)


class Hadron640R:
    def __init__(self):
        self.rgb: OV64B = OV64B()
        self.infrared: Boson640 = Boson640()
        self.gstreamer_pids = []
        self.gstreamer_pids_dict = {"rgb": None, "infrared": None}

    def initialize(self):
        self.infrared.initialize()
        gst_pid = self.infrared.backend.getGstreamerPID(self.gstreamer_pids)
        self.gstreamer_pids.append(gst_pid)
        self.gstreamer_pids_dict["infrared"] = gst_pid

        self.rgb.initialize()
        gst_pid = self.rgb.backend.getGstreamerPID(self.gstreamer_pids)
        self.gstreamer_pids.append(gst_pid)
        self.gstreamer_pids_dict["rgb"] = gst_pid
    
    def terminateRGB(self):
        self.rgb.backend.terminateGstreamer(self.gstreamer_pids_dict["rgb"])
    
    def terminateInfrared(self):
        self.infrared.backend.terminateGstreamer(self.gstreamer_pids_dict["infrared"])

    def terminateCameras(self):
        self.terminateInfrared()
        self.terminateRGB()
        


class Boson640(Camera):
    def __init__(self):
        super().__init__("BOSON640", "rb5")
        self.gstreamer_pipeline = None
        self.backend = RB5Backend()
        

    def setGstreamerPipeline(self, pipeline: Optional[str] = None):
        if pipeline:
            self.gstreamer_pipeline = pipeline
        else:
            pipeline = f"nohup setsid gst-launch-1.0 -v v4l2src device=/dev/video0 io-mode=2 ! video/x-raw,format=NV12,width=640,height=512,framerate=30/1 ! videoconvert ! video/x-raw,format=I420 ! x264enc tune=zerolatency speed-preset=veryfast bitrate=2500 key-int-max=60 bframes=0 byte-stream=true ! h264parse ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay pt=96 mtu=1200 config-interval=1 ! udpsink host=192.168.2.225 port=5000 sync=false async=false"
            self.gstreamer_pipeline = pipeline

    def initialize(self):
        self.setGstreamerPipeline()
        if self.backend and isinstance(self.backend, RB5Backend):
            self.backend.gstreamer_pipeline = self.gstreamer_pipeline
            self.backend.initialize()
            self.backend.initializeStream()


class OV64B(Camera):
    def __init__(self):
        super().__init__("OV64B", "rb5")
        self.gstreamer_pipeline = None
        self.backend = RB5Backend()

    def setGstreamerPipeline(self, pipeline: Optional[str] = None):
        if pipeline:
            self.gstreamer_pipeline = pipeline
        else:
            pipeline = f"nohup setsid gst-pipeline-app -e qtiqmmfsrc name=qmmf ! video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 ! videoconvert ! video/x-raw,format=I420 ! x264enc tune=zerolatency speed-preset=veryfast bitrate=6000 key-int-max=60 bframes=0 byte-stream=true ! h264parse ! video/x-h264,stream-format=byte-stream,alignment=au ! rtph264pay pt=96 mtu=1200 config-interval=1 ! udpsink host={self.src_addr} port=6000 sync=false async=false"
            self.gstreamer_pipeline = pipeline

    def initialize(self):
        self.setGstreamerPipeline()
        if self.backend and isinstance(self.backend, RB5Backend):
            self.backend.gstreamer_pipeline = self.gstreamer_pipeline
            self.backend.initialize()
            self.backend.initializeStream()


if __name__ == "__main__":
    hadron_instance = Hadron640R()
    hadron_instance.infrared.setConnection(
        "192.168.2.225", "192.168.2.230", "root", "oelinux123"
    )
    hadron_instance.rgb.setConnection(
        "192.168.2.225", "192.168.2.230", "root", "oelinux123"
    )
    hadron_instance.initialize()

