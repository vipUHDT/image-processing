image_processing.tools.homography
=================================

.. py:module:: image_processing.tools.homography


Functions
---------

.. autoapisummary::

   image_processing.tools.homography.mapPixelCoordinates


Module Contents
---------------

.. py:function:: mapPixelCoordinates(pixel_position: tuple[int, int], homography_matrix: Optional[cv2.typing.MatLike] = None, homography_points: Optional[tuple[numpy.ndarray, numpy.ndarray]] = None) -> list[float] | list[None]

   Map a pixel coordinate (x, y) from one image to another using a homography.
   Returns the mapped coordinate as [x', y'] or None if mapping fails.


