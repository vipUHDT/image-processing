"""
SSH connection controller for remote device interaction.

This module provides :class:`SSH_Controller`, a thin wrapper around
:paramiko:`paramiko.SSHClient` used to establish SSH connections,
execute remote commands, optionally run them in the background, and parse
their output. It is primarily used to manage and interact with remote
systems involved in streaming or processing pipelines.
"""

import paramiko
import logging

LOGGER = logging.getLogger(__name__)

class SSH_Controller():
    """
    Wrapper class for managing SSH connections and command execution.

    This class creates and maintains an SSH session using Paramiko, supports
    remote command execution (foreground or background), and provides helper
    utilities for parsing command output.

    Parameters
    ----------
    remote_addr : str
        Hostname or IP address of the remote machine.
    username : str
        Username used to authenticate to the remote host.
    password : str
        Password or credential used for authentication.

    Attributes
    ----------
    client : paramiko.SSHClient
        Paramiko SSH client instance.
    remote_addr : str
        Remote address of the target machine.
    username : str
        SSH username.
    password : str
        SSH password or credential.
    is_connected : bool
        Indicates whether an active SSH session is open.
    """
    def __init__(self, remote_addr: str, username: str, password: str) -> None:
        self.src_device = None
        self.target_device = None
        self.client = paramiko.SSHClient()
        self.remote_addr = remote_addr
        self.username = username
        self.password = password
        self.is_connected = False


    def connect(self) -> None:
        """Establish an SSH connection to the remote host.

        Attempts to connect using the configured credentials, adding unknown
        host keys automatically. Logs success or failure accordingly.
        """
        try:
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.remote_addr, username=self.username, password=self.password)
            LOGGER.info(f"Successfully connected to {self.remote_addr}")
            self.is_connected = True
        except Exception as e:
            LOGGER.exception(f"Unable to connect to {self.remote_addr}. Encountered error: {e}")
    
    def disconnect(self) -> None:
        """Close the active SSH session, if one exists.

        Logs a message if invoked without an active session.
        """
        if not self.is_connected:
            LOGGER.info(f"{self.src_device} is already connected to {self.target_device} <{self.remote_addr}>")
        else:
            self.client.close()
            self.is_connected = False
        
    def run_cmd(self, cmd: str, background: bool = False) -> tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile] | None:
        """Execute a remote shell command via the SSH session.

        If background mode is requested, the command is wrapped with `nohup`
        and `setsid` to detach it from the current shell.

        Parameters
        ----------
        cmd : str
            The shell command to execute remotely.
        background : bool, optional
            Whether to run the command in the background, by default False.

        Returns
        -------
        tuple or None
            Tuple of `(stdin, stdout, stderr)` from Paramiko if connected,
            otherwise ``None``.
        """
        if (self.is_connected):
            if background:
                cmd = f"nohup setsid {cmd}"
            stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
            return stdin, stdout, stderr
        else:
            LOGGER.warn(f"Unable to execute {cmd}. \n{self.src_device} is not connected to {self.target_device} <{self.remote_addr}>.")
            return None
    
    def parse_cmd_output(self, cmd_output) -> list[str]:
        """Parse standard output results from a command.

        Parameters
        ----------
        cmd_output : tuple
            Tuple returned by :meth:`run_cmd` containing `(stdin, stdout, stderr)`.

        Returns
        -------
        list of str
            A list of output lines with newline characters removed.
        """
        stdin, stdout, stderr = cmd_output
        parsed_output = []
        for line in stdout:  
            line = line.rstrip("\n")
            parsed_output.append(line)

        return parsed_output
    
