image_processing.tools.gps
==========================

.. py:module:: image_processing.tools.gps


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


   Common base class for all non-exit exceptions.


.. py:class:: UbloxGPSController(port: str = '/dev/ttyACM0', baudrate: int = 38400, timeout: int = 1)

   .. py:attribute:: port
      :value: '/dev/ttyACM0'



   .. py:attribute:: baudrate
      :value: 38400



   .. py:attribute:: timeout
      :value: 1



   .. py:attribute:: connection
      :type:  Optional[ublox_gps.UbloxGps]
      :value: None



   .. py:method:: connect(port: Optional[str] = None, baudrate: Optional[int] = None, timeout: Optional[int] = None) -> bool


   .. py:method:: has_fix(pvt: Any) -> bool


   .. py:method:: getFixInfo() -> Optional[Dict[str, Any]]


   .. py:method:: getGPS() -> Optional[Tuple[float, float]]


   .. py:method:: waitForFix(timeout_s: float = 30.0) -> Optional[Tuple[float, float]]


   .. py:method:: getAttitude() -> Optional[Tuple[float, float, float]]


   .. py:method:: disconnect()


