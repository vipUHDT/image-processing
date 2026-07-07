"""Camera backend that controls a remote device (e.g., Qualcomm RB5) over SSH."""

import logging
from typing import Optional

from image_processing.camera import CameraBackend
from image_processing.connection.ssh import SSH_Controller

LOGGER = logging.getLogger(__name__)


class RemoteCamera(CameraBackend):
    """
    Control a camera attached to a remote host over SSH.

    Parameters
    ----------
    client : str, optional
        IP address of the local machine receiving the stream.
    host : str, optional
        IP address of the remote device hosting the camera.
    username, password : str, optional
        SSH credentials for the remote device.
    """

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
        self.connection_manager: Optional[SSH_Controller] = None

    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        """Store the connection parameters for the remote device."""
        self.client = client
        self.host = host
        self.username = username
        self.password = password

    def connect(self) -> None:
        """Open the SSH connection to the remote device."""
        self.connection_manager = SSH_Controller(self.host, self.username, self.password)  # type: ignore
        self.connection_manager.connect()

    def initializeStream(self, pipeline) -> None:
        """Launch a GStreamer pipeline on the remote device in the background."""
        cmd_output = self.connection_manager.run_cmd(pipeline, background=True)  # type: ignore
        self.connection_manager.parse_cmd_output(cmd_output)  # type: ignore

    def getProcessID(self, keyword: str) -> list[str]:
        """Return remote process IDs matching ``keyword`` (via ``pgrep``)."""
        if self.connection_manager:
            cmd_output = self.connection_manager.run_cmd(f"pgrep {keyword}")
            return self.connection_manager.parse_cmd_output(cmd_output)
        return []

    def terminateProcessID(self, pid: None | str = None):
        """Send SIGINT to a remote process by PID."""
        if pid:
            return self.connection_manager.run_cmd(f"kill -INT {pid}")  # type: ignore

    def terminateProcessName(self, pname: None | str):
        """Send SIGINT to remote processes by name (via ``pkill``)."""
        if pname:
            return self.connection_manager.run_cmd(f"pkill -SIGINT {pname}")  # type: ignore

    def cleanLogFiles(self) -> None:
        """Remove ``nohup.out`` left behind by background pipelines."""
        self.connection_manager.run_cmd("rm -rf nohup.out")  # type: ignore

    def disconnect(self) -> None:
        """Close the SSH connection."""
        if self.connection_manager:
            self.connection_manager.disconnect()

    # Backwards-compatible alias for the original misspelled method name.
    disconect = disconnect

    def initialize(self) -> None:
        """Connect to the remote device."""
        self.connect()
