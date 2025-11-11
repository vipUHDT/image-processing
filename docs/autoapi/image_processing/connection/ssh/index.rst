image_processing.connection.ssh
===============================

.. py:module:: image_processing.connection.ssh


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


   .. py:method:: disconnect() -> None


   .. py:method:: run_cmd(cmd: str, background: bool = False) -> tuple[paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile] | None


   .. py:method:: parse_cmd_output(cmd_output) -> list[str]


