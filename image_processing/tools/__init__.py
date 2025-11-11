from .hash import *
from .homography import *
from .metadata import *
from .gps import UbloxGPSController
from .mission_planning import *
from datetime import datetime

def timestamp(format: str ="%d_%m_%Y_%H_%M_%S") -> str:
    """
    Generate a timestamp string based on the current time.

    Parameters
    ----------
    fmt : str, optional
        The desired timestamp format string following `datetime.strftime` directives.
        Default is "%d_%m_%Y_%H_%M_%S".

        Common format codes include:
        ----------------------------
        %Y : Year with century (e.g., 2025)
        %y : Year without century (00–99)
        %m : Month as a zero-padded decimal number (01–12)
        %B : Full month name (e.g., November)
        %b : Abbreviated month name (e.g., Nov)
        %d : Day of the month as a zero-padded decimal number (01–31)
        %A : Full weekday name (e.g., Tuesday)
        %a : Abbreviated weekday name (e.g., Tue)
        %H : Hour (24-hour clock, 00–23)
        %I : Hour (12-hour clock, 01–12)
        %p : AM or PM
        %M : Minute (00–59)
        %S : Second (00–59)
        %f : Microsecond (000000–999999)
        %z : UTC offset (e.g., +0000)
        %Z : Time zone name
        %j : Day of the year (001–366)
        %U : Week number (Sunday as first day of week)
        %W : Week number (Monday as first day of week)

    Returns
    -------
    str
        The formatted timestamp string.
    """
    return datetime.now().strftime(format)