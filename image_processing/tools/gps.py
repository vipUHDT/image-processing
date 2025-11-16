"""
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
"""

from typing import Optional, Tuple, Dict, Any
import serial
import time


class GPSConnectionError(Exception):
    """
    Exception raised when a GPS connection cannot be established.

    This is typically thrown by :meth:`UbloxGPSController.connect`
    when the underlying serial port cannot be opened or a lower-level
    error occurs.
    """
    pass


class UbloxGPSController:
    """
    Controller for a u-blox GNSS receiver using :mod:`ublox_gps`.

    This class manages:

    - Opening the serial connection to the GPS module.
    - Interpreting PVT (position, velocity, time) messages to determine
      whether a valid fix is available.
    - Extracting latitude/longitude coordinates.
    - Optionally retrieving vehicle attitude (roll, pitch, heading).

    Parameters
    ----------
    port : str, optional
        Serial device path for the GPS receiver (for example,
        ``"/dev/ttyACM0"``), by default ``"/dev/ttyACM0"``.
    baudrate : int, optional
        Serial baud rate, by default ``38400``.
    timeout : int, optional
        Read timeout in seconds for the serial port, by default ``1``.

    Attributes
    ----------
    port : str
        Serial device path used for the connection.
    baudrate : int
        Serial baud rate for the connection.
    timeout : int
        Serial read timeout in seconds.
    connection : UbloxGps or None
        Instance of :class:`ublox_gps.UbloxGps` once :meth:`connect`
        succeeds, otherwise None.
    """

    from ublox_gps import UbloxGps
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 38400, timeout: int = 1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection: Optional[UbloxGps] = None

    def connect(self, port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool:
        """
        Open a serial connection and initialize the u-blox GPS interface.

        Parameters
        ----------
        port : str or None, optional
            Serial device path to use. If None, uses the controller's
            configured :attr:`port`.
        baudrate : int or None, optional
            Baud rate to use. If None, uses :attr:`baudrate`.
        timeout : int or None, optional
            Read timeout in seconds. If None, uses :attr:`timeout`.

        Returns
        -------
        bool
            True if the connection is successfully established.

        Raises
        ------
        GPSConnectionError
            If the serial port cannot be opened or initialization fails.
        """
        try:
            ser = serial.Serial(
                port=port or self.port,
                baudrate=baudrate or self.baudrate,
                timeout=timeout if timeout is not None else self.timeout,
            )
            self.connection = UbloxGps(ser)
            return True
        except (serial.SerialException, Exception) as e:
            raise GPSConnectionError(f"Unable to connect to GPS on {port or self.port}: {e}") from e


    def _pvt_flags(self, pvt: Any) -> int:
        """
        Extract a flags field from a PVT structure and normalize to an int.

        The underlying :mod:`ublox_gps` PVT object may expose flags in a
        variety of forms (integer, bytes, namedtuple, string). This
        helper attempts to interpret those representations and returns
        a best-effort integer value.

        Parameters
        ----------
        pvt : Any
            PVT-like structure as returned by :meth:`UbloxGps.geo_coords`.

        Returns
        -------
        int
            Flags value decoded to an integer. Returns 0 if the flags
            cannot be interpreted.
        """
        flags = getattr(pvt, "flags", getattr(pvt, "flags2", 0))


        if isinstance(flags, int):
            return flags

        if isinstance(flags, (bytes, bytearray)):
            return int.from_bytes(flags, "little")

        if hasattr(flags, "_asdict"):
            vals = [v for v in flags._asdict().values() if isinstance(v, int)]
            return vals[0] if vals else 0

        if isinstance(flags, str):
            try:
                return int(flags, 0)
            except ValueError:
                return 0

        return 0

    def has_fix(self, pvt: Any) -> bool:
        """
        Determine whether a PVT structure represents a valid GNSS fix.

        The fix is considered valid if both:

        - The ``gnssFixOK`` flag bit (bit 0) is set.
        - The fix type is 2D or better (``fixType >= 2``).

        Parameters
        ----------
        pvt : Any
            PVT-like structure as returned by :meth:`UbloxGps.geo_coords`.

        Returns
        -------
        bool
            True if the PVT message indicates a valid fix, otherwise False.
        """
        flags = self._pvt_flags(pvt)
        gnss_fix_ok = bool(flags & 0x01)
        fix_type = getattr(pvt, "fixType", 0)
        return gnss_fix_ok and fix_type >= 2

    def _latlon_from_pvt(self, pvt: Any) -> Tuple[float, float]:
        """
        Extract latitude and longitude from a PVT message.

        Some u-blox message formats report latitude and longitude in
        scaled integer units (for example, degrees * :math:`1e7`).
        This method detects those cases and rescales them back to
        degrees.

        Parameters
        ----------
        pvt : Any
            PVT-like structure as returned by :meth:`UbloxGps.geo_coords`.

        Returns
        -------
        tuple of float
            Tuple ``(lat, lon)`` in degrees.
        """
        lat = pvt.lat if abs(pvt.lat) <= 90 else pvt.lat / 1e7
        lon = pvt.lon if abs(pvt.lon) <= 180 else pvt.lon / 1e7
        return lat, lon

    def _near_zero_latlon(self, lat: float, lon: float, eps: float = 1e-6) -> bool:
        """
        Check whether a latitude/longitude pair is close to (0, 0).

        This is useful for filtering out invalid default coordinates that
        may be reported before the receiver acquires a real fix.

        Parameters
        ----------
        lat : float
            Latitude in degrees.
        lon : float
            Longitude in degrees.
        eps : float, optional
            Tolerance for treating the value as zero, by default ``1e-6``.

        Returns
        -------
        bool
            True if both |lat| and |lon| are below ``eps``, otherwise False.
        """
        return abs(lat) < eps and abs(lon) < eps

    def getFixInfo(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve a dictionary with detailed fix information.

        This method queries the GPS for a PVT fix and returns a summary
        including:

        - Whether a valid fix is present.
        - Fix type.
        - ``gnssFixOK`` flag.
        - Number of satellites.
        - Latitude and longitude.

        Returns
        -------
        dict or None
            Dictionary with keys ``"has_fix"``, ``"fix_type"``,
            ``"gnssFixOK"``, ``"num_sv"``, ``"lat"``, and ``"lon"``,
            or None if no connection is available or no PVT message
            can be retrieved.
        """
        if not self.connection:
            return None
        pvt = self.connection.geo_coords()
        if pvt is None:
            return None

        flags = self._pvt_flags(pvt)
        fix_type = getattr(pvt, "fixType", 0)
        num_sv = getattr(pvt, "numSV", getattr(pvt, "numSvs", None))
        lat, lon = self._latlon_from_pvt(pvt)

        return {
            "has_fix": self._has_fix(pvt),
            "fix_type": fix_type,
            "gnssFixOK": bool(flags & 0x01),
            "num_sv": num_sv,
            "lat": lat,
            "lon": lon,
        }

    def getGPS(self) -> Optional[Tuple[float, float]]:
        """
        Get the current GPS position, if a valid fix exists.

        This method returns longitude and latitude in degrees, but only
        when the receiver reports a valid fix and the coordinates are
        not near (0, 0).

        Returns
        -------
        tuple of float or None
            Tuple ``(lon, lat)`` in degrees if a valid fix is available,
            otherwise None.
        """
        if not self.connection:
            return None
        pvt = self.connection.geo_coords()
        if pvt is None or not self._has_fix(pvt):
            return None
        lat, lon = self._latlon_from_pvt(pvt)
        if self._near_zero_latlon(lat, lon):
            return None
        return (lon, lat)

    def waitForFix(self, timeout_s: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        Wait for a valid GPS fix up to a specified timeout.

        This method repeatedly polls the receiver until:

        - A valid fix is detected via :meth:`has_fix`, and
        - The reported coordinates are not near (0, 0), or
        - The timeout is reached.

        Parameters
        ----------
        timeout_s : float, optional
            Maximum time to wait for a fix in seconds, by default ``30.0``.

        Returns
        -------
        tuple of float or None
            Tuple ``(lon, lat)`` in degrees if a valid fix is acquired
            within the timeout, otherwise None.
        """
        if not self.connection:
            return None
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            pvt = self.connection.geo_coords()
            if pvt and self.has_fix(pvt):
                lat, lon = self._latlon_from_pvt(pvt)
                if not self._near_zero_latlon(lat, lon):
                    return (lon, lat)
            time.sleep(0.1)
        return None

    def getAttitude(self) -> Optional[Tuple[float, float, float]]:
        """
        Retrieve vehicle attitude from the GPS receiver, if available.

        This method queries the receiver for a ``veh_attitude`` message
        and extracts roll, pitch, and heading if present.

        Returns
        -------
        tuple of float or None
            Tuple ``(roll, pitch, heading)`` in degrees if attitude
            information is available and complete, otherwise None.
        """
        if not self.connection:
            return None
        att = self.connection.veh_attitude()
        if att is None:
            return None
        roll = getattr(att, "roll", None)
        pitch = getattr(att, "pitch", None)
        heading = getattr(att, "heading", None)
        if roll is None or pitch is None or heading is None:
            return None
        return (roll, pitch, heading)
    
    def disconnect(self):
        """
        Close the underlying serial port, if it is open.

        This does not reset the :attr:`connection` attribute, but ensures
        that the hardware port is closed and resources are released.
        """
        if self.connection.hard_port:
            self.connection.hard_port.close()
