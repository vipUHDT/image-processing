image_processing.odcl.Localize
==============================

.. py:module:: image_processing.odcl.Localize


Classes
-------

.. autoapisummary::

   image_processing.odcl.Localize.Georeference_Engine


Functions
---------

.. autoapisummary::

   image_processing.odcl.Localize.georeference_utm
   image_processing.odcl.Localize.georeference_enu
   image_processing.odcl.Localize.georeference_aeqd
   image_processing.odcl.Localize.georeference_manual
   image_processing.odcl.Localize.haversine


Module Contents
---------------

.. py:class:: Georeference_Engine(backend, altitude_offset=0)

   .. py:attribute:: camera_metadata
      :value: None



   .. py:attribute:: backend


   .. py:attribute:: altitude_offset
      :value: 0



   .. py:method:: getBackends(backend)


   .. py:method:: georeference(target_pixel_coordinates: tuple[int, int], platform_state: image_processing.PlatformState, camera_metadata: image_processing.camera.CameraMetadata, altitude_offset=0)


.. py:function:: georeference_utm(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_enu(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_aeqd(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: georeference_manual(target_pixel_coordinates, drone_latitude, drone_longitude, drone_altitude, altitude_offset, drone_yaw, sensor_w, sensor_h, pix_width, pix_height, focal_length)

.. py:function:: haversine(lat1, lon1, lat2, lon2)

