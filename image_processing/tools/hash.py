import hashlib
from typing import Optional

def hashFile(file_path: str, algorithm: str ="md5", chunk_size: int = 8192) -> str:
    """
    Compute a cryptographic hash of a file using streaming (chunked) reads.

    Parameters
    ----------
    file_path : str
        Path to the file to hash.
    algorithm : str, optional
        Hash algorithm to use. Must be supported by `hashlib.new`
        (e.g., "md5", "sha1", "sha256", "sha512"). Default is "md5".
    chunk_size : int, optional
        Number of bytes to read per iteration. Larger values improve
        performance for large files but use more memory. Default is 8192.

    Returns
    -------
    str
        Hexadecimal digest string representing the computed hash.

    Raises
    ------
    ValueError
        If an unsupported hashing algorithm is provided.
    FileNotFoundError
        If the target file does not exist.
    PermissionError
        If the file cannot be opened or read.

    Notes
    -----
    - File contents are processed in a memory-efficient streaming manner.
    - The returned digest is deterministic for a given `algorithm`.
    """
    h = hashlib.new(algorithm)

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            h.update(chunk)

    return h.hexdigest()

if __name__ == "__main__":
    print(hashFile("/Users/plegaspi/Documents/Programming/UHDT/image-processing-validation/yolo11n.pt"))