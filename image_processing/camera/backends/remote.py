"""
Remote camera backend implementation using SSH-based control.

This module provides :class:`RemoteCamera`, a :class:`CameraBackend`
implementation that interacts with a remote device over an SSH connection.
It supports establishing connections, launching remote commands related
to camera streaming (e.g., GStreamer pipelines), retrieving remote process
IDs, and terminating running streaming processes.
"""

from image_processing.camera import CameraBackend
from image_processing.connection.ssh import SSH_Controller
from typing import Optional, Protocol, runtime_checkable

import logging

LOGGER = logging.getLogger(__name__)

class RemoteCamera(CameraBackend):
    """
    Backend that communicates with a remote camera host using SSH.

    This backend is intended for camera systems that do not run locally
    and require remote command execution to configure, initialize, or
    manage streaming pipelines (e.g., via GStreamer). It assumes that
    the remote endpoint supports process management and allows launching
    background commands over SSH.

    Parameters
    ----------
    client : str or None, optional
        Identifier for the client receiving streamed data (e.g., its hostname or IP).
    host : str or None, optional
        Hostname or IP address of the remote device where camera processes run.
    username : str or None, optional
        Username for SSH authentication.
    password : str or None, optional
        Password or credential used for SSH authentication.

    Attributes
    ----------
    name : str
        Identifier for the backend, default is ``"RB5 Backend"``.
    connection_manager : SSH_Controller or None
        Active SSH connection wrapper once :meth:`connect` is called.
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
        self.connection_manager: Optional[SSH_Controller] | None = None


    def setConnection(self, client: str, host: str, username: str, password: str) -> None:
        """Update SSH connection credentials.

        Parameters
        ----------
        client : str
            Identifier of the local client receiving video.
        host : str
            Hostname or IP of the remote SSH device.
        username : str
            Username used for authentication.
        password : str
            Password or credential used for authentication.
        """
        self.client = client
        self.host = host
        self.username = username
        self.password = password

    def connect(self) -> None:
        """Create and open an SSH connection to the remote camera host."""
        self.connection_manager = SSH_Controller(self.host, self.username, self.password)  # type: ignore
        self.connection_manager.connect()

    def initializeStream(self, pipeline) -> None:
        """Launch a streaming pipeline remotely in the background.

        Parameters
        ----------
        pipeline : str
            Command or pipeline string to execute remotely, such as
            a GStreamer launch command. Executed in background mode.
        """
        cmd_output = self.connection_manager.run_cmd(pipeline, background=True)  # type: ignore
        parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)  # type: ignore

    
    def getProcessID(self, keyword) -> list[str]:
        """Query remote process IDs that match a given keyword.

        Parameters
        ----------
        keyword : str
            Search term used with ``pgrep`` to filter process names.

        Returns
        -------
        list of str
            List of matching process IDs returned by the remote host.
            Returns an empty list if no connection is active.
        """
        cmd = f"pgrep {keyword}"
        if self.connection_manager:
            cmd_output = self.connection_manager.run_cmd(cmd)
            parsed_cmd_output = self.connection_manager.parse_cmd_output(cmd_output)
            return parsed_cmd_output
        return []

    def setGstreamerPid(self, gstreamer_pid) -> None:
        """Store a process ID associated with a remote GStreamer pipeline.

        Parameters
        ----------
        gstreamer_pid : str or None
            Process ID to be stored for later termination or tracking.
        """
        self.gstreamer_pid = gstreamer_pid
        
    def terminateProcessID(self, pid: None | str = None):
        """Terminate a remote process by PID using SIGINT.

        Parameters
        ----------
        pid : str or None
            Remote PID to terminate. If ``None``, no action is taken.

        Returns
        -------
        Any
            Output from the remote command, if executed.
        """
        if pid:
            cmd = f"kill -SIGINT {pid}"
            cmd_output = self.connection_manager.run_cmd(cmd)  # type: ignore 
            return cmd_output
        
    def terminateProcessName(self, pname: None | str ):
        """Terminate remote processes that match a process name.

        Parameters
        ----------
        pname : str or None
            Name used with ``pkill`` to terminate matching processes.

        Returns
        -------
        Any
            Output from the remote command, if executed.
        """
        if pname:
            cmd = f"pkill -SIGINT {pname}"
            cmd_output = self.connection_manager.run_cmd(cmd) # type: ignore 
            return cmd_output
    
    def disconnect(self):
        """Disconnect the active SSH session."""
        self.connection_manager.disconnect()

    def initialize(self) -> None:
        """Initialize the backend by establishing the SSH connection."""
        self.connect()
