"""SSH connection management for remote devices."""

import logging

import paramiko

LOGGER = logging.getLogger(__name__)


class SSH_Controller:
    """
    Manage an SSH connection to a remote device and run commands over it.

    Parameters
    ----------
    remote_addr : str
        Hostname or IP address of the remote device.
    username : str
        SSH username.
    password : str, optional
        SSH password. May be omitted when ``key_filename`` is provided.
    key_filename : str, optional
        Path to a private key file to authenticate with instead of (or in
        addition to) the password.
    """

    def __init__(
        self,
        remote_addr: str,
        username: str,
        password: str | None = None,
        key_filename: str | None = None,
    ) -> None:
        self.src_device = None
        self.target_device = None
        self.client = paramiko.SSHClient()
        self.remote_addr = remote_addr
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.is_connected = False

    def connect(self) -> bool:
        """Open the SSH connection, accepting unknown host keys automatically.

        Returns True on success, False otherwise (the failure is logged).
        """
        try:
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.remote_addr,
                username=self.username,
                password=self.password,
                key_filename=self.key_filename,
            )
            LOGGER.info(f"Successfully connected to {self.remote_addr}")
            self.is_connected = True
        except Exception as e:
            LOGGER.exception(f"Unable to connect to {self.remote_addr}. Encountered error: {e}")
            self.is_connected = False
        return self.is_connected

    def disconnect(self) -> None:
        """Close the SSH connection if it is open."""
        if not self.is_connected:
            LOGGER.info(f"Already disconnected from {self.remote_addr}")
        else:
            self.client.close()
            self.is_connected = False

    def run_cmd(
        self, cmd: str, background: bool = False
    ) -> tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile] | None:
        """
        Execute a command on the remote device.

        Parameters
        ----------
        cmd : str
            Command line to run.
        background : bool, optional
            If True, run the command detached (``nohup setsid``) so it
            survives the SSH session.

        Returns
        -------
        tuple or None
            ``(stdin, stdout, stderr)`` channel files, or None if not connected.
        """
        if self.is_connected:
            if background:
                cmd = f"nohup setsid {cmd}"
            stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
            return stdin, stdout, stderr
        LOGGER.warning(
            f"Unable to execute {cmd}. Not connected to {self.remote_addr}."
        )
        return None

    def parse_cmd_output(self, cmd_output) -> list[str]:
        """Return the stdout of a ``run_cmd`` result as a list of lines without newlines."""
        stdin, stdout, stderr = cmd_output
        return [line.rstrip("\n") for line in stdout]
