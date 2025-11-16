image_processing.connection.ssh
===============================

.. py:module:: image_processing.connection.ssh

.. autoapi-nested-parse::

   SSH connection controller for remote device interaction.

   This module provides :class:`SSH_Controller`, a thin wrapper around
   :paramiko:`paramiko.SSHClient` used to establish SSH connections,
   execute remote commands, optionally run them in the background, and parse
   their output. It is primarily used to manage and interact with remote
   systems involved in streaming or processing pipelines.



Attributes
----------

.. autoapisummary::

   image_processing.connection.ssh.LOGGER


Classes
-------

.. autoapisummary::

   image_processing.connection.ssh.SSH_Controller


Module Contents
---------------

.. py:data:: LOGGER

.. py:class:: SSH_Controller(remote_addr: str, username: str, password: str)

   Wrapper class for managing SSH connections and command execution.

   This class creates and maintains an SSH session using Paramiko, supports
   remote command execution (foreground or background), and provides helper
   utilities for parsing command output.

   :param remote_addr: Hostname or IP address of the remote machine.
   :type remote_addr: str
   :param username: Username used to authenticate to the remote host.
   :type username: str
   :param password: Password or credential used for authentication.
   :type password: str

   .. attribute:: client

      Paramiko SSH client instance.

      :type: paramiko.SSHClient

   .. attribute:: remote_addr

      Remote address of the target machine.

      :type: str

   .. attribute:: username

      SSH username.

      :type: str

   .. attribute:: password

      SSH password or credential.

      :type: str

   .. attribute:: is_connected

      Indicates whether an active SSH session is open.

      :type: bool


   .. py:attribute:: src_device
      :value: None



   .. py:attribute:: target_device
      :value: None



   .. py:attribute:: client


   .. py:attribute:: remote_addr


   .. py:attribute:: username


   .. py:attribute:: password


   .. py:attribute:: is_connected
      :value: False



   .. py:method:: connect() -> None

      Establish an SSH connection to the remote host.

      Attempts to connect using the configured credentials, adding unknown
      host keys automatically. Logs success or failure accordingly.



   .. py:method:: disconnect() -> None

      Close the active SSH session, if one exists.

      Logs a message if invoked without an active session.



   .. py:method:: run_cmd(cmd: str, background: bool = False) -> tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile] | None

      Execute a remote shell command via the SSH session.

      If background mode is requested, the command is wrapped with `nohup`
      and `setsid` to detach it from the current shell.

      :param cmd: The shell command to execute remotely.
      :type cmd: str
      :param background: Whether to run the command in the background, by default False.
      :type background: bool, optional

      :returns: Tuple of `(stdin, stdout, stderr)` from Paramiko if connected,
                otherwise ``None``.
      :rtype: tuple or None



   .. py:method:: parse_cmd_output(cmd_output) -> list[str]

      Parse standard output results from a command.

      :param cmd_output: Tuple returned by :meth:`run_cmd` containing `(stdin, stdout, stderr)`.
      :type cmd_output: tuple

      :returns: A list of output lines with newline characters removed.
      :rtype: list of str



