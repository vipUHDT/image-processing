import cv2
from typing import Optional
import numpy as np


def mapPixelCoordinates(
    pixel_position: tuple[int, int],
    homography_matrix: Optional[cv2.typing.MatLike] = None,
    homography_points: Optional[tuple[np.ndarray, np.ndarray]] = None,
) -> list[float] | list[None]:
    """
    Map a 2D pixel coordinate from one image space to another using a homography transform.

    Either a pre-computed homography matrix (`homography_matrix`) must be provided,
    or a pair of corresponding point sets (`homography_points`) will be used to
    estimate one via RANSAC.

    Parameters
    ----------
    pixel_position : tuple[int, int]
        Input pixel coordinate `(x, y)` to be mapped.
    homography_matrix : cv2.typing.MatLike, optional
        A 3x3 homography matrix. If provided, it is used directly without recomputing.
    homography_points : tuple[np.ndarray, np.ndarray], optional
        A tuple `(src_points, dst_points)` where each is an array of corresponding
        2D points with shape `(N, 2)`, used to estimate the homography via
        `cv2.findHomography` if `homography_matrix` is not supplied.

    Returns
    -------
    list[float] | list[None]
        The mapped pixel coordinate as `[x_mapped, y_mapped]` if successful.
        Otherwise returns `[None, None]`.

    Raises
    ------
    ValueError
        If neither `homography_matrix` nor `homography_points` is provided.

    Notes
    -----
    • Output coordinates are floating-point values and not rounded or clipped.  
    • If `homography_points` is used, RANSAC with reprojection threshold 5.0 is applied.  
    • Returned coordinates are in the same pixel coordinate convention as the input
      (OpenCV uses `(x, y)` = `(col, row)`).
    """
    
    H = homography_matrix
    x, y = pixel_position
    points = np.array([[[float(x), float(y)]]], dtype=np.float64)

    if not H and homography_points:
        src_points, dst_points = homography_points
        H, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

    mapped_pixel_coordinates = [None, None]

    if points and H:
        perspective_transform = cv2.perspectiveTransform(points, H)
        if perspective_transform:
            mapped_pixel_coordinates = perspective_transform[0, 0, :].tolist()
   
    return mapped_pixel_coordinates
