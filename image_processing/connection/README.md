# connection

The connection package is the remote-access layer of `image_processing`. It wraps
[Paramiko](https://www.paramiko.org/) to provide simple, logged controllers for talking
to the remote camera boards (e.g. the RB5 / Hadron) over SSH and SFTP. Nothing in this
package knows about cameras or detections — it only moves commands and files between the
host machine and a remote device.

## What this directory does

- **`ssh.py`** — `SSH_Controller` opens an SSH session to a host and exposes:
  - `connect()` / `disconnect()` — session lifecycle with auto host-key acceptance.
  - `run_cmd(cmd, background=False)` — execute a command; `background=True` wraps it in
    `nohup setsid` so a streaming process keeps running after the call returns.
  - `parse_cmd_output(...)` — normalize stdout into a list of stripped lines.
- **`sftp.py`** — `SFTPController` opens an SFTP session over a Paramiko transport and
  exposes file operations: `uploadFile`, `downloadFile`, `listDir`, `exists`, `mkdir`,
  `removeFile`, `renameFile`, and `chmod`, each guarded by `ensureConnected()`.

Both controllers log success/failure rather than raising on connection errors, so callers
get a stable interface even when the remote device is unreachable.

## How it connects to the rest of the package

- **← [`camera`](../camera/README.md):** this is the package's primary consumer.
  - `RemoteCamera` (camera backend) uses `SSH_Controller` to start, find (`pgrep`), and
    kill (`kill`/`pkill`) the GStreamer process on the remote board, and to clean up log
    files.
  - `GStreamerCamera` uses `SFTPController` to download recorded EO/IR video off the board
    after a flight.
  - The `Hadron640R` controller uses `SSH_Controller` directly to `pkill gst` before
    (re)starting streams.

This package sits at the bottom of the dependency stack — it depends on nothing else in
`image_processing`, which keeps the transport concerns isolated from the imaging logic.
