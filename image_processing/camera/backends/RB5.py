from image_processing.camera import CameraBackend
from image_processing.connection.ssh import SSH_Controller
from typing import Optional, Protocol, runtime_checkable

import logging

LOGGER = logging.getLogger(__name__)

class RB5Backend(CameraBackend):
    def __init__(
        self,
        src_device_addr: str | None = None,
        remote_addr: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.name = "RB5 Backend"
        self.remote_addr = remote_addr
        self.username = username
        self.password = password
        self.connection_manager: Optional[SSH_Controller] | None = None
        self.gstreamer_pid : str | None = None
        self.gstreamer_pipeline: str | None = None
        self.src_device_addr = src_device_addr

    def setConnection(self, remote_addr: str, username: str, password: str) -> None:
        self.remote_addr = remote_addr
        self.username = username
        self.password = password

    def connect(self) -> None:
        self.connection_manager = SSH_Controller(self.remote_addr, self.username, self.password)  # type: ignore
        self.connection_manager.connect()

    def initializeStream(self) -> None:
        cmd_output = self.connection_manager.run_cmd(self.gstreamer_pipeline)  # type: ignore
        parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)  # type: ignore

    def getGstreamerPID(self, active_pids: list[str]) -> str | None:
        cmd = "pgrep gst"
        cmd_output = self.connection_manager.run_cmd(cmd)  # type: ignore
        parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)  # type: ignore
        if len(parsed_cmd_output) > 0:
            for output in parsed_cmd_output:
                if output.replace("\n", "").replace("\r", "") in active_pids:
                    continue
                return output.replace("\n", "").replace("\r", "")
        else:
            return None

    def setGstreamerPid(self, gstreamer_pid) -> None:
        self.gstreamer_pid = gstreamer_pid

    def terminateGstreamer(self, gstreamer_pid: None | str = None):
        if gstreamer_pid == None:
            cmd = "pkill -SIGINT gst"
            cmd_output = self.connection_manager.run_cmd(cmd)  # type: ignore
            return cmd_output
        else:
            cmd = f"kill -SIGINT {gstreamer_pid}"
            cmd_output = self.connection_manager.run_cmd(cmd)
            return cmd_output

    def initialize(self) -> None:
        self.connect()
