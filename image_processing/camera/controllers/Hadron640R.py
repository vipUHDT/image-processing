from typing import Optional
from image_processing.camera import Camera, CameraBackend, constructGstreamerPipeline
from image_processing.camera.backends import (
    RemoteCamera,
    GStreamerManager,
    GStreamerCamera,
)
from image_processing.tools import timestamp
import os, glob
from string import Template

from cv2 import VideoCapture, CAP_GSTREAMER


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
        self.backendManager.cameras["OV64B"].initializeStream(self.getProcessIds())

        self.backendManager.cameras["BOSON640"].initialize()
        self.backendManager.cameras["BOSON640"].initializeStream(self.getProcessIds())

        self.backendManager.cameras["OV64B"].startRXPipeline()
        self.backendManager.cameras["BOSON640"].startRXPipeline()

    def capture(self):
        rgb_img = self.backendManager.cameras["OV64B"].backend.captureFrame()
        infrared_img = self.backendManager.cameras["BOSON640"].backend.captureFrame()
        return rgb_img, infrared_img

    def terminate(self):
        self.backendManager.cameras["OV64B"].closeRXPipeline()
        self.backendManager.cameras["BOSON640"].closeRXPipeline()

        self.backendManager.cameras["OV64B"].terminate()
        self.backendManager.cameras["BOSON640"].terminate()


class Boson640(Camera):
    def __init__(self):
        super().__init__("BOSON640")
        self.backend = GStreamerCamera(self.name)
        self.RX_TEMPLATE = Template(
            " ! ".join(
                (
                    "udpsrc port=$port "
                    "caps=application/x-rtp,media=video,encoding-name=H264,"
                    "payload=96,clock-rate=90000",
                    "rtpjitterbuffer latency=10 drop-on-late=true",
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
            "gst-launch-1.0 -e v4l2src device=/dev/video0 io-mode=2",
            "video/x-raw,format=NV12,width=640,height=512,framerate=30/1",
            "videoconvert",
            "video/x-raw,format=I420",

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
                f"filesink location={timestamp()}-USBcam-h264.mp4 "
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


class OV64B(Camera):
    def __init__(self):
        super().__init__("OV64B")
        self.backend = GStreamerCamera(self.name)
        self.RX_TEMPLATE = Template(
            " ! ".join(
                (
                    "udpsrc port=$port caps=application/x-rtp,media=video,encoding-name=H265,payload=96",
                    "rtpjitterbuffer latency=1 do-lost=true",
                    "rtph265depay",
                    "h265parse",
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
                        "sharpness=1 "
                        "video_0::framerate=30 "
                        "video_0::bitrate=20000000 "
                        "video_0::bitrate-control=maxbitrate "
                        "video_0::idr-interval=1"
                    ),
                    "video/x-h265,profile=main,width=1920,height=1080,framerate=30/1",
                    "h265parse",
                    "tee name=t",
                    "queue",
                    "video/x-h265,stream-format=byte-stream,alignment=au",
                    "rtph265pay pt=96 mtu=1200 config-interval=1",
                    (
                        "udpsink host=$client port=$port sync=false async=false "
                        "t. ! queue ! h265parse ! "
                        "video/x-h265,stream-format=hvc1,alignment=au "
                        f"! mp4mux faststart=true ! filesink "
                        f"location={timestamp()}-OV64B.mp4 sync=false async=false"
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
