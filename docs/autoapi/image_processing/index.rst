image_processing
================

.. py:module:: image_processing


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/image_processing/camera/index
   /autoapi/image_processing/config/index
   /autoapi/image_processing/connection/index
   /autoapi/image_processing/manager/index
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

   .. py:attribute:: image
      :type:  cv2.typing.MatLike


   .. py:attribute:: platform_state
      :type:  PlatformState


