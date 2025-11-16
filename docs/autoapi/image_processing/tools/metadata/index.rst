image_processing.tools.metadata
===============================

.. py:module:: image_processing.tools.metadata


Functions
---------

.. autoapisummary::

   image_processing.tools.metadata.extractMetadata
   image_processing.tools.metadata.execute
   image_processing.tools.metadata.embedMetadata


Module Contents
---------------

.. py:function:: extractMetadata(file_name)

   Extract relevant camera and geospatial metadata using ExifTool.

   :param file_name: Path to the image file to inspect.
   :type file_name: str

   :returns: `(metadata, latitude, longitude, altitude, yaw, pix_width, pix_height, focal_length)`
             or `None` if the file does not contain GPS metadata.
   :rtype: tuple or None

   .. rubric:: Notes

   - EXIF GPS longitude is negated so that West values become negative.
   - `yaw` is parsed from the `File:Comment` field using the format:
     `"pitch: <val> yaw: <val> roll: <val>"`.


.. py:function:: execute(command)

   Run a command with suppressed stdout/stderr.


.. py:function:: embedMetadata(file_name, latitude, longitudate, pitch, yaw, roll)

   Embed geolocation + orientation metadata into an image using ExifTool.

   :param file_name: Path to the output image file (will be modified in-place).
   :type file_name: str
   :param latitude: Decimal latitude (North positive, South negative).
   :type latitude: float
   :param longitude: Decimal longitude (East positive, West negative).
   :type longitude: float
   :param pitch: Pitch angle in degrees.
   :type pitch: float
   :param yaw: Yaw (heading) angle in degrees.
   :type yaw: float
   :param roll: Roll angle in degrees.
   :type roll: float

   .. rubric:: Notes

   - Uses `-overwrite_original`.
   - Commands are launched as separate subprocesses.
   - If running repeatedly consider batching into one call for efficiency.


