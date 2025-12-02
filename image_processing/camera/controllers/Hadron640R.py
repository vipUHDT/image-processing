from typing import Optional
from image_processing.camera import Camera, CameraBackend, constructGstreamerPipeline
from image_processing.camera.backends import (
    RemoteCamera,
    GStreamerManager,
    GStreamerCamera,
)
from image_processing.connection.ssh import SSH_Controller
from image_processing.tools import timestamp
import os, glob
from string import Template

from cv2 import VideoCapture, CAP_GSTREAMER

from time import sleep

import logging

LOGGER = logging.getLogger(__name__)


class Hadron640R:
    def __init__(self):
        self.backendManager = GStreamerManager()
        self.ports = {"BOSON640": 5000, "OV64B": 6000}
        self.processes = []

    def getProcessIds(self):
        process_ids = []
        if all((self.client, self.host, self.username, self.password)):
            hadron = RemoteCamera(self.client, self.host, self.username, self.password)
            hadron.connect()
            raw_process_ids = hadron.getProcessID("gst")
            process_ids = [
                process_id.replace("\n", "").replace("\r", "")
                for process_id in raw_process_ids
            ]
        return process_ids

    def setConnection(self, client, host, username, password):
        self.client = client
        self.host = host
        self.username = username
        self.password = password

    def initialize(self):
        self.backendManager.addCamera(OV64B())
        self.backendManager.addCamera(Boson640())
        
        self.ssh = SSH_Controller(self.host, self.username, self.password)
        self.ssh.connect()
        self.ssh.run_cmd("pkill gst")
        self.ssh.disconnect()

        self.backendManager.cameras["OV64B"].setConnection(
            self.client, self.host, self.username, self.password
        )
        self.backendManager.cameras["BOSON640"].setConnection(
            self.client, self.host, self.username, self.password
        )

        self.backendManager.cameras["OV64B"].setPort(self.ports["OV64B"])
        self.backendManager.cameras["BOSON640"].setPort(self.ports["BOSON640"])

        self.backendManager.cameras["OV64B"].setTXPipeline()
        self.backendManager.cameras["BOSON640"].setTXPipeline()

        self.backendManager.cameras["OV64B"].setRXPipeline()
        self.backendManager.cameras["BOSON640"].setRXPipeline()

        self.backendManager.cameras["OV64B"].initialize()
        self.backendManager.cameras["BOSON640"].initialize()
        
        
        self.backendManager.cameras["OV64B"].initializeStream(self.getProcessIds())
        sleep(5)
        self.backendManager.cameras["BOSON640"].initializeStream(self.getProcessIds())

        self.backendManager.cameras["OV64B"].startRXPipeline()
        self.backendManager.cameras["BOSON640"].startRXPipeline()
        sleep(10)
        
    def capture(self):
        rgb_img = self.backendManager.cameras["OV64B"].backend.captureFrame()
        infrared_img = self.backendManager.cameras["BOSON640"].backend.captureFrame()
        return rgb_img, infrared_img

    def terminate(self):
        self.backendManager.cameras["OV64B"].closeRXPipeline()
        self.backendManager.cameras["BOSON640"].closeRXPipeline()

        self.backendManager.cameras["OV64B"].terminate()
        self.backendManager.cameras["BOSON640"].terminate()
    
    def downloadRemoteVideos(self, eo_save_path, ir_save_path):
        self.backendManager.cameras["OV64B"].downloadRemoteVideo(eo_save_path)
        self.backendManager.cameras["BOSON640"].downloadRemoteVideo(ir_save_path)
        


class Boson640(Camera):
    def __init__(self):
        super().__init__("BOSON640")
        self.backend = GStreamerCamera(self.name)
        self.remote_video_path = f"flights/{timestamp()}-IR.mp4"
        self.RX_TEMPLATE = Template(
            " ! ".join(
                (
                    "udpsrc port=$port "
                    "caps=application/x-rtp,media=video,encoding-name=H264,"
                    "payload=96,clock-rate=90000",
                    "rtpjitterbuffer latency=13 drop-on-late=true",
                    "rtph264depay",
                    "h264parse",
                    "nvv4l2decoder disable-dpb=true",
                    "nvvidconv",
                    "video/x-raw,format=BGRx",
                    "videoconvert",
                    "video/x-raw,format=BGR",
                    "appsink drop=true max-buffers=1 sync=false",
                )
            )
        )
        self.TX_TEMPLATE = Template(
            " ! ".join(
                (
                    "gst-launch-1.0 -e v4l2src device=/dev/v4l/by-id/usb-FLIR_Boson_439955-video-index0 io-mode=2",
                    "video/x-raw,format=NV12,width=640,height=512,framerate=30/1",
                    "x264enc tune=zerolatency speed-preset=veryfast "
                    "bitrate=2500 key-int-max=60 bframes=0 byte-stream=true",
                    "h264parse",
                    (
                        "tee name=t "
                        "t. ! queue ! "
                        "video/x-h264,stream-format=byte-stream,alignment=au ! "
                        "rtph264pay pt=96 mtu=1200 config-interval=1 ! "
                        "udpsink host=$client port=$port sync=false async=false "
                        "t. ! queue ! "
                        "h264parse ! "
                        "video/x-h264,stream-format=avc,alignment=au ! "
                        "mp4mux faststart=true ! "
                        f"filesink location={self.remote_video_path} "
                        "sync=false async=false"
                    ),
                )
            )
        )

    def setPort(self, port):
        self.backend.port = port

    def setTXPipeline(self, pipeline: Template | str | None = None):
        if pipeline:
            self.backend.setTXPipeline(pipeline)
        else:
            self.backend.setTXPipeline(self.TX_TEMPLATE)

    def setRXPipeline(self, pipeline: Template | str | None = None):
        if pipeline:
            self.backend.setRXPipeline(pipeline)
        else:
            self.backend.setRXPipeline(self.RX_TEMPLATE)

    def startRXPipeline(self):
        self.backend.startRXPipeline()

    def captureFrame(self):
        return self.backend.captureFrame()

    def closeRXPipeline(self):
        self.backend.closeRXPipeline()

    def initialize(self):
        self.backend.initialize()

    def initializeStream(self, pids):
        self.backend.initializeStream(pids)

    def terminate(self):
        self.backend.terminate()
        
    def downloadRemoteVideo(self, save_path: str):
        self.backend.downloadRemoteVideo(self.remote_video_path, save_path)


class OV64B(Camera):
    def __init__(self):
        super().__init__("OV64B")
        self.backend = GStreamerCamera(self.name)
        self.remote_video_path = f"flights/{timestamp()}-EO.mp4"
        self.RX_TEMPLATE = Template(
            " ! ".join(
                (
                    "udpsrc port=$port "
                    "caps=application/x-rtp,media=video,encoding-name=H264,payload=96",
                    "rtpjitterbuffer latency=13",
                    "rtph264depay",
                    "h264parse",
                    "nvv4l2decoder disable-dpb=true",
                    "nvvidconv",
                    "video/x-raw,format=NV12",
                    "videoconvert",
                    "video/x-raw,format=BGR",
                    "appsink drop=true max-buffers=1 sync=false",
                )
            )
        )
        
        self.TX_TEMPLATE = Template(
    " ! ".join(
        (
            (
                "gst-launch-1.0 -e "
                "qtiqmmfsrc name=qmmf "
                "camera=0 "
                "scene=action "
                "af-mode=continuous "
                "white-balance-mode=auto "
                "iso-mode=deblur "
                "noise-reduction=fast "
                "sharpness=1"
            ),
            "video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1",
            "queue",
            "x264enc tune=zerolatency speed-preset=superfast bitrate=6000 key-int-max=30",
            "h264parse",
            (
                "tee name=t "
                "t. ! queue max-size-buffers=0 max-size-time=50000000 max-size-bytes=0 leaky=downstream "
                "! video/x-h264,stream-format=byte-stream,alignment=au "
                "! rtph264pay pt=96 mtu=1200 config-interval=1 "
                "! udpsink host=$client port=$port sync=false async=false "
                "t. ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 "
                "! h264parse "
                "! video/x-h264,stream-format=avc,alignment=au "
                "! mp4mux faststart=true "
                f"! filesink location={self.remote_video_path} sync=false async=false"
            ),
        )
    )
)

    def setPort(self, port):
        self.backend.port = port

    def setTXPipeline(self, pipeline: Template | str | None = None):
        if pipeline:
            self.backend.setTXPipeline(pipeline)
        else:
            self.backend.setTXPipeline(self.TX_TEMPLATE)

    def startRXPipeline(self):
        self.backend.startRXPipeline()

    def setRXPipeline(self, pipeline: Template | str | None = None):
        if pipeline:
            self.backend.setRXPipeline(pipeline)
        else:
            self.backend.setRXPipeline(self.RX_TEMPLATE)

    def captureFrame(self):
        return self.backend.captureFrame()

    def closeRXPipeline(self):
        self.backend.closeRXPipeline()

    def initialize(self):
        self.backend.initialize()

    def initializeStream(self, pids):
        self.backend.initializeStream(pids)

    def terminate(self):
        self.backend.terminate()
    
    def downloadRemoteVideo(self, save_path: str):
        self.backend.downloadRemoteVideo(self.remote_video_path, save_path)


if __name__ == "__main__":
    hadrond640 = Hadron640R()
    hadrond640.setConnection("192.168.2.225", "192.168.2.237", "root", "oelinux123")
    hadrond640.initialize()

    img1, img2 = hadrond640.capture()
    import cv2

    cv2.imwrite("image1.jpg", img1)
    cv2.imwrite("image2.jpg", img2)
    hadrond640.terminate()

    # hadrond640.terminate()
