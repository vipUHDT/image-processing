import cv2
from typing import Optional
import numpy as np


def mapPixelCoordinates(
    pixel_position: tuple[int, int],
    homography_matrix: Optional[cv2.typing.MatLike] = None,
    homography_points: Optional[tuple[np.ndarray, np.ndarray]] = None,
) -> list[float] | list[None]:
    """
    Map a pixel coordinate (x, y) from one image to another using a homography.
    Returns the mapped coordinate as [x', y'] or None if mapping fails.
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
