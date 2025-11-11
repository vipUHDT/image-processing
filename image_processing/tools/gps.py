from typing import Optional, Tuple, Dict, Any
from ublox_gps import UbloxGps
import serial
import time


class GPSConnectionError(Exception):
    pass


class UbloxGPSController:
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 38400, timeout: int = 1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection: Optional[UbloxGps] = None

    def connect(self, port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool:
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
        flags = self._pvt_flags(pvt)
        gnss_fix_ok = bool(flags & 0x01)
        fix_type = getattr(pvt, "fixType", 0)
        return gnss_fix_ok and fix_type >= 2

    def _latlon_from_pvt(self, pvt: Any) -> Tuple[float, float]:
        lat = pvt.lat if abs(pvt.lat) <= 90 else pvt.lat / 1e7
        lon = pvt.lon if abs(pvt.lon) <= 180 else pvt.lon / 1e7
        return lat, lon

    def _near_zero_latlon(self, lat: float, lon: float, eps: float = 1e-6) -> bool:
        return abs(lat) < eps and abs(lon) < eps

    def getFixInfo(self) -> Optional[Dict[str, Any]]:
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
        if self.connection.hard_port:
            self.connection.hard_port.close()
