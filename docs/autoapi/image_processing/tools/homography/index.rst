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

   Map a 2D pixel coordinate from one image space to another using a homography transform.

   Either a pre-computed homography matrix (`homography_matrix`) must be provided,
   or a pair of corresponding point sets (`homography_points`) will be used to
   estimate one via RANSAC.

   :param pixel_position: Input pixel coordinate `(x, y)` to be mapped.
   :type pixel_position: tuple[int, int]
   :param homography_matrix: A 3x3 homography matrix. If provided, it is used directly without recomputing.
   :type homography_matrix: cv2.typing.MatLike, optional
   :param homography_points: A tuple `(src_points, dst_points)` where each is an array of corresponding
                             2D points with shape `(N, 2)`, used to estimate the homography via
                             `cv2.findHomography` if `homography_matrix` is not supplied.
   :type homography_points: tuple[np.ndarray, np.ndarray], optional

   :returns: The mapped pixel coordinate as `[x_mapped, y_mapped]` if successful.
             Otherwise returns `[None, None]`.
   :rtype: list[float] | list[None]

   :raises ValueError: If neither `homography_matrix` nor `homography_points` is provided.

   .. rubric:: Notes

   • Output coordinates are floating-point values and not rounded or clipped.
   • If `homography_points` is used, RANSAC with reprojection threshold 5.0 is applied.
   • Returned coordinates are in the same pixel coordinate convention as the input
     (OpenCV uses `(x, y)` = `(col, row)`).


