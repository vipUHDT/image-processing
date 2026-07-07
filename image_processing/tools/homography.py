"""Homography utilities for mapping pixel coordinates between camera views."""

from typing import Optional

import cv2
import numpy as np


def mapPixelCoordinates(
    pixel_position: tuple[int, int],
    homography_matrix: Optional[np.ndarray] = None,
    homography_points: Optional[tuple[np.ndarray, np.ndarray]] = None,
) -> list[float] | list[None]:
    """
    Map a pixel coordinate from one camera view to another via a homography.

    Either a precomputed homography matrix or a pair of corresponding point
    sets must be provided. When points are given, the homography is estimated
    with RANSAC.

    Parameters
    ----------
    pixel_position : tuple[int, int]
        ``(x, y)`` pixel coordinate in the source view.
    homography_matrix : np.ndarray, optional
        Precomputed 3x3 homography matrix.
    homography_points : tuple[np.ndarray, np.ndarray], optional
        ``(src_points, dst_points)`` corresponding point sets used to
        estimate the homography when no matrix is given.

    Returns
    -------
    list[float] or list[None]
        ``[x, y]`` in the destination view, or ``[None, None]`` if no
        homography could be determined.
    """
    H = homography_matrix
    x, y = pixel_position
    points = np.array([[[float(x), float(y)]]], dtype=np.float64)

    if H is None and homography_points:
        src_points, dst_points = homography_points
        H, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

    if H is not None:
        perspective_transform = cv2.perspectiveTransform(points, H)
        return perspective_transform[0, 0, :].tolist()
    return [None, None]


def cropRGBToMatchIR(
    rgb_img: np.ndarray,
    ir_img: np.ndarray,
    homography_points: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    """
    Crop and resize an RGB image so it covers the same scene as an IR image.

    The IR frame corners are mapped into RGB pixel space with a homography
    estimated from ``homography_points``; the RGB image is cropped to the
    bounding box of the mapped corners (clipped to image bounds) and resized
    to the IR resolution. If both images already have the same shape, the RGB
    image is returned unchanged.

    Parameters
    ----------
    rgb_img : np.ndarray
        RGB image of shape ``(H, W, 3)``.
    ir_img : np.ndarray
        IR image whose footprint and resolution should be matched.
    homography_points : tuple[np.ndarray, np.ndarray]
        ``(ir_points, rgb_points)`` corresponding point sets used to
        estimate the IR->RGB homography.

    Returns
    -------
    np.ndarray
        RGB image cropped and resized to the IR image's dimensions.
    """
    if rgb_img.shape == ir_img.shape:
        return rgb_img

    h_ir, w_ir = ir_img.shape[:2]
    ir_corners = [
        (0, 0),
        (w_ir - 1, 0),
        (w_ir - 1, h_ir - 1),
        (0, h_ir - 1),
    ]

    # Map IR corners into RGB pixel space and take their bounding box.
    mapped_corners = np.array(
        [mapPixelCoordinates(pt, homography_points=homography_points) for pt in ir_corners],
        dtype=np.float32,
    )
    x_min = int(np.floor(mapped_corners[:, 0].min()))
    x_max = int(np.ceil(mapped_corners[:, 0].max()))
    y_min = int(np.floor(mapped_corners[:, 1].min()))
    y_max = int(np.ceil(mapped_corners[:, 1].max()))

    h_rgb, w_rgb = rgb_img.shape[:2]
    x_min, y_min = max(0, x_min), max(0, y_min)
    x_max, y_max = min(w_rgb, x_max), min(h_rgb, y_max)

    cropped_rgb = rgb_img[y_min:y_max, x_min:x_max]
    return cv2.resize(cropped_rgb, (w_ir, h_ir), interpolation=cv2.INTER_LINEAR)


def resizeIRToMatchRGB(ir_img: np.ndarray, cropped_rgb_img: np.ndarray) -> np.ndarray:
    """
    Resize an IR image to the dimensions of a cropped RGB image.

    Parameters
    ----------
    ir_img : np.ndarray
        IR image to resize.
    cropped_rgb_img : np.ndarray
        RGB image whose dimensions should be matched.

    Returns
    -------
    np.ndarray
        IR image resized with bilinear interpolation.
    """
    target_size = (cropped_rgb_img.shape[1], cropped_rgb_img.shape[0])  # (width, height)
    return cv2.resize(ir_img, target_size, interpolation=cv2.INTER_LINEAR)
