image_processing.tools.hash
===========================

.. py:module:: image_processing.tools.hash


Functions
---------

.. autoapisummary::

   image_processing.tools.hash.hashFile


Module Contents
---------------

.. py:function:: hashFile(file_path: str, algorithm: str = 'md5', chunk_size: int = 8192) -> str

   Compute a cryptographic hash of a file using streaming (chunked) reads.

   :param file_path: Path to the file to hash.
   :type file_path: str
   :param algorithm: Hash algorithm to use. Must be supported by `hashlib.new`
                     (e.g., "md5", "sha1", "sha256", "sha512"). Default is "md5".
   :type algorithm: str, optional
   :param chunk_size: Number of bytes to read per iteration. Larger values improve
                      performance for large files but use more memory. Default is 8192.
   :type chunk_size: int, optional

   :returns: Hexadecimal digest string representing the computed hash.
   :rtype: str

   :raises ValueError: If an unsupported hashing algorithm is provided.
   :raises FileNotFoundError: If the target file does not exist.
   :raises PermissionError: If the file cannot be opened or read.

   .. rubric:: Notes

   - File contents are processed in a memory-efficient streaming manner.
   - The returned digest is deterministic for a given `algorithm`.


