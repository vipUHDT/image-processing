import paramiko
import logging

LOGGER = logging.getLogger(__name__)

class SSH_Controller():
    def __init__(self, src_device: str, target_device: str, remote_addr: str, username: str, password: str) -> None:
        self.src_device = src_device
        self.target_device = target_device
        self.client = paramiko.SSHClient()
        self.remote_addr = remote_addr
        self.username = username
        self.password = password
        self.is_connected = False


    def connect(self) -> None:
        try:
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.remote_addr, username=self.username, password=self.password)
            LOGGER.info(f"Successfully connected to {self.remote_addr}")
            self.is_connected = True
        except Exception as e:
            LOGGER.exception(f"Unable to connect to {self.remote_addr}. Encountered error: {e}")
    
    def disconnect(self) -> None:
        if not self.is_connected:
            LOGGER.info(f"{self.src_device} is already connected to {self.target_device} <{self.remote_addr}>")
        else:
            self.client.close()
            self.is_connected = False
        
    def run_cmd(self, cmd: str) -> tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile]:
        if (self.is_connected):
            stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
            return stdin, stdout, stderr
        else:
            LOGGER.warn(f"Unable to execute {cmd}. \n{self.src_device} is not connected to {self.target_device} <{self.remote_addr}>.")
    
    def parse_cmd_output(self, cmd_output: tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile]) -> list[str]:
        stdin, stdout, stderr = cmd_output
        parsed_output = []
        for line in iter(stdout.readline, ""):
            parsed_output.append()
        return parsed_output
    
