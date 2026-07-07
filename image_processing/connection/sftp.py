"""SFTP file transfer to and from remote devices."""

import logging
from typing import List, Optional

import paramiko

LOGGER = logging.getLogger(__name__)


class SFTPController:
    """
    Manage an SFTP session for file transfer with a remote device.

    Operations are no-ops (with a warning logged) when not connected, and
    errors are logged rather than raised so a flaky link does not crash the
    calling pipeline.

    Parameters
    ----------
    remote_addr : str
        Hostname or IP address of the remote device.
    username : str
        SFTP username.
    password : str
        SFTP password.
    port : int, optional
        SSH port (default 22).
    """

    def __init__(
        self,
        remote_addr: str,
        username: str,
        password: str,
        port: int = 22,
    ) -> None:
        self.remote_addr = remote_addr
        self.username = username
        self.password = password
        self.port = port

        self.transport: Optional[paramiko.Transport] = None
        self.sftp: Optional[paramiko.SFTPClient] = None
        self.is_connected: bool = False

        self.src_device: Optional[str] = None
        self.target_device: Optional[str] = None

    def connect(self) -> None:
        if self.is_connected:
            LOGGER.info(
                f"SFTP already connected to {self.target_device or ''} <{self.remote_addr}>"
            )
            return

        try:
            self.transport = paramiko.Transport((self.remote_addr, self.port))
            self.transport.connect(
                username=self.username,
                password=self.password,
            )
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.is_connected = True
            LOGGER.info(f"Successfully connected via SFTP to {self.remote_addr}")
        except Exception as e:
            LOGGER.exception(
                f"Unable to establish SFTP connection to {self.remote_addr}. "
                f"Encountered error: {e}"
            )
            self.transport = None
            self.sftp = None
            self.is_connected = False

    def disconnect(self) -> None:
        if not self.is_connected:
            LOGGER.info(
                f"SFTP already disconnected from {self.target_device or ''} "
                f"<{self.remote_addr}>"
            )
            return

        try:
            if self.sftp is not None:
                self.sftp.close()
            if self.transport is not None:
                self.transport.close()
        except Exception as e:
            LOGGER.exception(
                f"Error while closing SFTP connection to {self.remote_addr}: {e}"
            )
        finally:
            self.sftp = None
            self.transport = None
            self.is_connected = False
            LOGGER.info(f"SFTP disconnected from {self.remote_addr}")

    def ensureConnected(self) -> bool:
        if not self.is_connected or self.sftp is None:
            LOGGER.warning(
                f"Unable to perform SFTP operation. "
                f"{self.src_device or 'Source'} is not connected to "
                f"{self.target_device or 'target'} <{self.remote_addr}>."
            )
            return False
        return True

    def uploadFile(self, localPath: str, remotePath: str) -> None:
        if not self.ensureConnected():
            return

        try:
            LOGGER.info(
                f"Uploading file '{localPath}' to '{remotePath}' on {self.remote_addr}"
            )
            self.sftp.put(localPath, remotePath)
        except Exception as e:
            LOGGER.exception(
                f"Failed to upload '{localPath}' to '{remotePath}' on "
                f"{self.remote_addr}: {e}"
            )

    def downloadFile(self, remotePath: str, localPath: str) -> None:
        if not self.ensureConnected():
            return

        try:
            LOGGER.info(
                f"Downloading file '{remotePath}' to '{localPath}' from {self.remote_addr}"
            )
            self.sftp.get(remotePath, localPath)  
        except Exception as e:
            LOGGER.exception(
                f"Failed to download '{remotePath}' to '{localPath}' from "
                f"{self.remote_addr}: {e}"
            )

    def listDir(self, remotePath: str = ".") -> Optional[List[str]]:
        if not self.ensureConnected():
            return None

        try:
            entries = self.sftp.listdir(remotePath)
            LOGGER.info(
                f"Directory listing for '{remotePath}' on {self.remote_addr}: {entries}"
            )
            return entries
        except FileNotFoundError:
            LOGGER.warning(
                f"Remote directory '{remotePath}' not found on {self.remote_addr}"
            )
        except Exception as e:
            LOGGER.exception(
                f"Failed to list directory '{remotePath}' on {self.remote_addr}: {e}"
            )
        return None

    def exists(self, remotePath: str) -> bool:
        if not self.ensureConnected():
            return False

        try:
            self.sftp.stat(remotePath)  
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            LOGGER.exception(
                f"Error while checking existence of '{remotePath}' on "
                f"{self.remote_addr}: {e}"
            )
            return False

    def mkdir(self, remotePath: str, mode: int = 0o777, existOk: bool = True) -> None:
        if not self.ensureConnected():
            return

        if existOk and self.exists(remotePath):
            LOGGER.info(
                f"Remote directory '{remotePath}' already exists on {self.remote_addr}"
            )
            return

        try:
            self.sftp.mkdir(remotePath, mode=mode)  
            LOGGER.info(
                f"Created remote directory '{remotePath}' on {self.remote_addr}"
            )
        except Exception as e:
            LOGGER.exception(
                f"Failed to create remote directory '{remotePath}' on "
                f"{self.remote_addr}: {e}"
            )

    def removeFile(self, remotePath: str) -> None:
        if not self.ensureConnected():
            return

        try:
            self.sftp.remove(remotePath)  
            LOGGER.info(
                f"Removed remote file '{remotePath}' on {self.remote_addr}"
            )
        except FileNotFoundError:
            LOGGER.warning(
                f"Tried to remove non-existent file '{remotePath}' on {self.remote_addr}"
            )
        except Exception as e:
            LOGGER.exception(
                f"Failed to remove remote file '{remotePath}' on "
                f"{self.remote_addr}: {e}"
            )

    def renameFile(self, remoteSrc: str, remoteDst: str) -> None:
        if not self.ensureConnected():
            return

        try:
            self.sftp.rename(remoteSrc, remoteDst) 
            LOGGER.info(
                f"Renamed remote file '{remoteSrc}' to '{remoteDst}' on {self.remote_addr}"
            )
        except Exception as e:
            LOGGER.exception(
                f"Failed to rename '{remoteSrc}' to '{remoteDst}' on "
                f"{self.remote_addr}: {e}"
            )

    def chmod(self, remotePath: str, mode: int) -> None:
        if not self.ensureConnected():
            return

        try:
            self.sftp.chmod(remotePath, mode) 
            LOGGER.info(
                f"Changed permissions for '{remotePath}' to {oct(mode)} "
                f"on {self.remote_addr}"
            )
        except Exception as e:
            LOGGER.exception(
                f"Failed to change permissions for '{remotePath}' on "
                f"{self.remote_addr}: {e}"
            )