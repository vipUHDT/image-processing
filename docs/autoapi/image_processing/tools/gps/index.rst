image_processing.tools.gps
==========================

.. py:module:: image_processing.tools.gps

.. autoapi-nested-parse::

   Helpers for interacting with a u-blox GNSS receiver.

   This module provides a small convenience wrapper around the
   :mod:`ublox_gps` package, handling serial connection setup, fix
   status interpretation, and extraction of latitude/longitude and
   attitude data.

   Typical usage
   -------------

   .. code-block:: python

       from image_processing.tools.gps import UbloxGPSController

       gps = UbloxGPSController(port="/dev/ttyACM0", baudrate=38400)
       gps.connect()
       fix = gps.waitForFix(timeout_s=30.0)
       if fix is not None:
           lon, lat = fix
           print("GPS fix:", lon, lat)

       attitude = gps.getAttitude()
       if attitude is not None:
           roll, pitch, heading = attitude

       gps.disconnect()



Exceptions
----------

.. autoapisummary::

   image_processing.tools.gps.GPSConnectionError


Classes
-------

.. autoapisummary::

   image_processing.tools.gps.UbloxGPSController


Module Contents
---------------

.. py:exception:: GPSConnectionError

   Bases: :py:obj:`Exception`


   Exception raised when a GPS connection cannot be established.

   This is typically thrown by :meth:`UbloxGPSController.connect`
   when the underlying serial port cannot be opened or a lower-level
   error occurs.


.. py:class:: UbloxGPSController(port: str = '/dev/ttyACM0', baudrate: int = 38400, timeout: int = 1)

   Controller for a u-blox GNSS receiver using :mod:`ublox_gps`.

   This class manages:

   - Opening the serial connection to the GPS module.
   - Interpreting PVT (position, velocity, time) messages to determine
     whether a valid fix is available.
   - Extracting latitude/longitude coordinates.
   - Optionally retrieving vehicle attitude (roll, pitch, heading).

   :param port: Serial device path for the GPS receiver (for example,
                ``"/dev/ttyACM0"``), by default ``"/dev/ttyACM0"``.
   :type port: str, optional
   :param baudrate: Serial baud rate, by default ``38400``.
   :type baudrate: int, optional
   :param timeout: Read timeout in seconds for the serial port, by default ``1``.
   :type timeout: int, optional

   .. attribute:: port

      Serial device path used for the connection.

      :type: str

   .. attribute:: baudrate

      Serial baud rate for the connection.

      :type: int

   .. attribute:: timeout

      Serial read timeout in seconds.

      :type: int

   .. attribute:: connection

      Instance of :class:`ublox_gps.UbloxGps` once :meth:`connect`
      succeeds, otherwise None.

      :type: UbloxGps or None


   .. py:attribute:: port
      :value: '/dev/ttyACM0'



   .. py:attribute:: baudrate
      :value: 38400



   .. py:attribute:: timeout
      :value: 1



   .. py:attribute:: connection
      :type:  Optional[UbloxGps]
      :value: None



   .. py:method:: connect(port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool

      Open a serial connection and initialize the u-blox GPS interface.

      :param port: Serial device path to use. If None, uses the controller's
                   configured :attr:`port`.
      :type port: str or None, optional
      :param baudrate: Baud rate to use. If None, uses :attr:`baudrate`.
      :type baudrate: int or None, optional
      :param timeout: Read timeout in seconds. If None, uses :attr:`timeout`.
      :type timeout: int or None, optional

      :returns: True if the connection is successfully established.
      :rtype: bool

      :raises GPSConnectionError: If the serial port cannot be opened or initialization fails.



   .. py:method:: has_fix(pvt: Any) -> bool

      Determine whether a PVT structure represents a valid GNSS fix.

      The fix is considered valid if both:

      - The ``gnssFixOK`` flag bit (bit 0) is set.
      - The fix type is 2D or better (``fixType >= 2``).

      :param pvt: PVT-like structure as returned by :meth:`UbloxGps.geo_coords`.
      :type pvt: Any

      :returns: True if the PVT message indicates a valid fix, otherwise False.
      :rtype: bool



   .. py:method:: getFixInfo() -> Optional[Dict[str, Any]]

      Retrieve a dictionary with detailed fix information.

      This method queries the GPS for a PVT fix and returns a summary
      including:

      - Whether a valid fix is present.
      - Fix type.
      - ``gnssFixOK`` flag.
      - Number of satellites.
      - Latitude and longitude.

      :returns: Dictionary with keys ``"has_fix"``, ``"fix_type"``,
                ``"gnssFixOK"``, ``"num_sv"``, ``"lat"``, and ``"lon"``,
                or None if no connection is available or no PVT message
                can be retrieved.
      :rtype: dict or None



   .. py:method:: getGPS() -> Optional[Tuple[float, float]]

      Get the current GPS position, if a valid fix exists.

      This method returns longitude and latitude in degrees, but only
      when the receiver reports a valid fix and the coordinates are
      not near (0, 0).

      :returns: Tuple ``(lon, lat)`` in degrees if a valid fix is available,
                otherwise None.
      :rtype: tuple of float or None



   .. py:method:: waitForFix(timeout_s: float = 30.0) -> Optional[Tuple[float, float]]

      Wait for a valid GPS fix up to a specified timeout.

      This method repeatedly polls the receiver until:

      - A valid fix is detected via :meth:`has_fix`, and
      - The reported coordinates are not near (0, 0), or
      - The timeout is reached.

      :param timeout_s: Maximum time to wait for a fix in seconds, by default ``30.0``.
      :type timeout_s: float, optional

      :returns: Tuple ``(lon, lat)`` in degrees if a valid fix is acquired
                within the timeout, otherwise None.
      :rtype: tuple of float or None



   .. py:method:: getAttitude() -> Optional[Tuple[float, float, float]]

      Retrieve vehicle attitude from the GPS receiver, if available.

      This method queries the receiver for a ``veh_attitude`` message
      and extracts roll, pitch, and heading if present.

      :returns: Tuple ``(roll, pitch, heading)`` in degrees if attitude
                information is available and complete, otherwise None.
      :rtype: tuple of float or None



   .. py:method:: disconnect()

      Close the underlying serial port, if it is open.

      This does not reset the :attr:`connection` attribute, but ensures
      that the hardware port is closed and resources are released.



