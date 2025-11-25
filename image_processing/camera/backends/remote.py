from image_processing.camera import CameraBackend
from image_processing.connection.ssh import SSH_Controller
from typing import Optional, Protocol, runtime_checkable

import logging

LOGGER = logging.getLogger(__name__)

class RemoteCamera(CameraBackend):
    def __init__(
        self,
        client: str | None = None,
        host: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.name = "RB5 Backend"
        self.client = client
        self.host = host
        self.username = username
        self.password = password
        self.connection_manager: Optional[SSH_Controller] | None = None


    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        self.client = client
        self.host = host
        self.username = username
        self.password = password

    def connect(self) -> None:
        self.connection_manager = SSH_Controller(self.host, self.username, self.password)  # type: ignore
        self.connection_manager.connect()

    def initializeStream(self, pipeline) -> None:
        cmd_output = self.connection_manager.run_cmd(pipeline, background=True)  # type: ignore
        parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)  # type: ignore

    
    def getProcessID(self, keyword) -> list[str]:
        cmd = f"pgrep {keyword}"
        if self.connection_manager:
            cmd_output = self.connection_manager.run_cmd(cmd)
            parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)
            return parsed_cmd_output
        return []

    def setGstreamerPid(self, gstreamer_pid) -> None:
        self.gstreamer_pid = gstreamer_pid
        
    def terminateProcessID(self, pid: None | str = None):
        if pid:
            cmd = f"kill -INT {pid}"
            cmd_output = self.connection_manager.run_cmd(cmd)  # type: ignore 
            return cmd_output
        
    def terminateProcessName(self, pname: None | str ):
        if pname:
            cmd = f"pkill -SIGINT {pname}"
            cmd_output = self.connection_manager.run_cmd(cmd) # type: ignore 
            return cmd_output
        
    def cleanLogFiles(self):
        self.connection_manager.run_cmd("rm -rf nohup.out")
    
    def disconect(self):
        self.connection_manager.disconnect()

    def initialize(self) -> None:
        self.connect()
