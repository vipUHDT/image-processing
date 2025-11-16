image_processing
================

.. py:module:: image_processing

.. autoapi-nested-parse::

   Core shared data structures and initialization helpers for the
   ``image_processing`` package.

   This module provides lightweight data containers used throughout the
   camera, ODCL (object detection, classification, localization), and data
   management subsystems:

   - :class:`PlatformState` — Represents the telemetry and attitude state
     of the sensing platform (e.g., UAV, rover, robot) at the moment an
     image is acquired.
   - :class:`QueuedImage` — Couples a captured image with the associated
     platform state for downstream processing (e.g., detection, geolocation).

   Logging is configured using a ``NullHandler`` to avoid forcing default
   logging behavior on user applications.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/index
   /autoapi/image_processing/config/index
   /autoapi/image_processing/connection/index
   /autoapi/image_processing/data/index
   /autoapi/image_processing/odcl/index
   /autoapi/image_processing/results/index
   /autoapi/image_processing/tools/index


Classes
-------

.. autoapisummary::

   image_processing.PlatformState
   image_processing.QueuedImage


Package Contents
----------------

.. py:class:: PlatformState

   Platform telemetry and attitude state associated with an image capture
   event or detection cycle.

   This structure is intended to be populated from onboard sensors
   (e.g., GNSS, IMU) or log data, and used by geolocation functions to
   project pixel detections into Earth-referenced coordinates.

   :param altitude: Platform altitude above ground level in meters.
   :type altitude: float, optional
   :param latitude: Geographic latitude (positive north) in decimal degrees.
   :type latitude: float, optional
   :param longitude: Geographic longitude (positive east) in decimal degrees.
   :type longitude: float, optional
   :param pitch: Platform pitch angle in degrees (positive nose-up).
   :type pitch: float, optional
   :param yaw: Platform yaw/heading angle in degrees (0° = North, +CW).
   :type yaw: float, optional
   :param roll: Platform roll angle in degrees (positive right-wing-down).
   :type roll: float, optional


   .. py:attribute:: altitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: latitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: longitude
      :type:  Optional[float]
      :value: None



   .. py:attribute:: pitch
      :type:  Optional[float]
      :value: None



   .. py:attribute:: yaw
      :type:  Optional[float]
      :value: None



   .. py:attribute:: roll
      :type:  Optional[float]
      :value: None



.. py:class:: QueuedImage

   Container for an image paired with the corresponding platform state,
   used for asynchronous or batched image processing pipelines.

   :param image: The captured image frame (BGR or grayscale), typically originating
                 from a live stream or logged dataset.
   :type image: cv2.typing.MatLike
   :param platform_state: The telemetry and attitude state at the time of image acquisition.
   :type platform_state: PlatformState

   .. rubric:: Notes

   Instances of this type are typically passed into worker queues inside
   :class:`~image_processing.odcl.detection.DetectionManager`.


   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


