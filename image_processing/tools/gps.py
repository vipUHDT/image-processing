"""Controller for u-blox GPS receivers connected over a serial port.

Hardware dependencies (``pyserial``, ``ublox_gps``) are imported lazily in
``connect`` so this module can be imported on machines without them.
"""

import time
from typing import Any, Dict, Optional, Tuple


class GPSConnectionError(Exception):
    """Raised when a connection to the GPS receiver cannot be established."""


class UbloxGPSController:
    """
    Thin wrapper around ``ublox_gps.UbloxGps`` for position and attitude reads.

    Parameters
    ----------
    port : str, optional
        Serial device path (default ``/dev/ttyACM0``).
    baudrate : int, optional
        Serial baud rate (default 38400).
    timeout : int, optional
        Serial read timeout in seconds (default 1).
    """

    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 38400, timeout: int = 1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Open the serial port and initialize the u-blox driver.

        Arguments override the values given at construction time. Raises
        ``GPSConnectionError`` if the port cannot be opened.
        """
        import serial
        from ublox_gps import UbloxGps

        try:
            ser = serial.Serial(
                port=port or self.port,
                baudrate=baudrate or self.baudrate,
                timeout=timeout if timeout is not None else self.timeout,
            )
            self.connection = UbloxGps(ser)
            return True
        except Exception as e:
            raise GPSConnectionError(
                f"Unable to connect to GPS on {port or self.port}: {e}"
            ) from e

    def _pvt_flags(self, pvt: Any) -> int:
        """Extract the NAV-PVT flags field as an int, tolerating driver variations."""
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
        """Return True if the NAV-PVT solution reports a valid 2D/3D fix."""
        flags = self._pvt_flags(pvt)
        gnss_fix_ok = bool(flags & 0x01)
        fix_type = getattr(pvt, "fixType", 0)
        return gnss_fix_ok and fix_type >= 2

    def _latlon_from_pvt(self, pvt: Any) -> Tuple[float, float]:
        """Return (lat, lon) in degrees, scaling raw 1e-7 values if needed."""
        lat = pvt.lat if abs(pvt.lat) <= 90 else pvt.lat / 1e7
        lon = pvt.lon if abs(pvt.lon) <= 180 else pvt.lon / 1e7
        return lat, lon

    def _near_zero_latlon(self, lat: float, lon: float, eps: float = 1e-6) -> bool:
        """Return True for the (0, 0) placeholder coordinates some receivers emit."""
        return abs(lat) < eps and abs(lon) < eps

    def getFixInfo(self) -> Optional[Dict[str, Any]]:
        """
        Return a summary of the current fix, or None if not connected or no data.

        The dict contains ``has_fix``, ``fix_type``, ``gnssFixOK``, ``num_sv``,
        ``lat``, and ``lon``.
        """
        if not self.connection:
            return None
        pvt = self.connection.geo_coords()
        if pvt is None:
            return None

        flags = self._pvt_flags(pvt)
        lat, lon = self._latlon_from_pvt(pvt)
        return {
            "has_fix": self.has_fix(pvt),
            "fix_type": getattr(pvt, "fixType", 0),
            "gnssFixOK": bool(flags & 0x01),
            "num_sv": getattr(pvt, "numSV", getattr(pvt, "numSvs", None)),
            "lat": lat,
            "lon": lon,
        }

    def getGPS(self) -> Optional[Tuple[float, float]]:
        """Return the current position as ``(lon, lat)``, or None without a valid fix."""
        if not self.connection:
            return None
        pvt = self.connection.geo_coords()
        if pvt is None or not self.has_fix(pvt):
            return None
        lat, lon = self._latlon_from_pvt(pvt)
        if self._near_zero_latlon(lat, lon):
            return None
        return (lon, lat)

    def waitForFix(self, timeout_s: float = 30.0) -> Optional[Tuple[float, float]]:
        """
        Poll until a valid fix is acquired or ``timeout_s`` elapses.

        Returns the position as ``(lon, lat)``, or None on timeout or if not
        connected.
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
        """Return vehicle attitude as ``(roll, pitch, heading)``, or None if unavailable."""
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

    def disconnect(self) -> None:
        """Close the underlying serial port if connected."""
        if self.connection and self.connection.hard_port:
            self.connection.hard_port.close()
        self.connection = None
