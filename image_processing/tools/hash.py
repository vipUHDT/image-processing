"""File hashing utilities."""

import hashlib


def hashFile(file_path: str, algorithm: str = "md5", chunk_size: int = 8192) -> str:
    """
    Compute the hash digest of a file, reading it in chunks.

    Parameters
    ----------
    file_path : str
        Path to the file to hash.
    algorithm : str, optional
        Any algorithm name accepted by ``hashlib.new`` (default ``"md5"``).
    chunk_size : int, optional
        Read size in bytes (default 8192).

    Returns
    -------
    str
        Hex-encoded digest.
    """
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
