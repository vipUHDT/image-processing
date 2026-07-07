"""EO/IR image fusion using the fuzzy transform.

Aligns an electro-optical (RGB) image to an infrared image via a homography,
then fuses the RGB value channel with the IR intensity in F-transform space
so that thermal detail is blended into the visible image.
"""

import os

import cv2
import numpy as np
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
from PIL import Image

from image_processing.tools.filters.Basis_Function import triangular_basis
from image_processing.tools.filters.Fuzzy_transform import fuse_images
from image_processing.tools.filters.homography import cropRGBToMatchIR

# Manually selected point correspondences between the IR and EO sensors of the
# Hadron 640R, used to estimate the default IR->EO homography.
DEFAULT_IR_POINTS = np.float32([
    (153, 88), (255, 68), (269, 107), (447, 91), (610, 311),
    (356, 294), (153, 459), (156, 498), (90, 335), (265, 427),
    (447, 165), (600, 204), (613, 199), (590, 194), (606, 190),
    (585, 180), (600, 180), (585, 164), (620, 182), (598, 164),
    (613, 172), (592, 148), (611, 158), (629, 169),
])

DEFAULT_EO_POINTS = np.float32([
    (666, 251), (822, 229), (844, 290), (1117, 259), (1369, 597),
    (979, 566), (670, 833), (671, 891), (567, 628), (839, 766),
    (1116, 370), (1349, 429), (1372, 422), (1335, 413), (1359, 409),
    (1326, 393), (1348, 391), (1326, 369), (1384, 399), (1348, 368),
    (1373, 382), (1335, 345), (1368, 358), (1398, 375),
])


def FuzzyFusion(
    eo_img: np.ndarray,
    ir_img: np.ndarray,
    block_size: tuple[int, int] = (8, 8),
    subblock_resolution: tuple[int, int] = (15, 15),
    radius: float = 5,
    output_dir: str = "Fused",
    homography_points: tuple[np.ndarray, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Fuse an EO (BGR) image with an IR image using the fuzzy transform.

    The EO image is cropped and resized to match the IR frame using a
    homography, converted to HSV, and its value channel is fused with the
    normalized IR intensity block by block. Hue and saturation are preserved
    from the EO image. A per-block blend-weight map is written to
    ``output_dir/alpha_map.jpg`` as a diagnostic.

    Parameters
    ----------
    eo_img : np.ndarray
        EO image in BGR channel order (as returned by ``cv2.imread``).
    ir_img : np.ndarray
        IR image; converted to grayscale if not already single-channel.
    block_size : tuple[int, int], optional
        Height and width of the fusion blocks in pixels.
    subblock_resolution : tuple[int, int], optional
        Number of fuzzy basis functions per block in each dimension.
    radius : float, optional
        Half-width of the triangular basis functions in pixels.
    output_dir : str, optional
        Directory where the alpha-map diagnostic image is saved. Created if
        it does not exist.
    homography_points : tuple[np.ndarray, np.ndarray], optional
        ``(ir_points, eo_points)`` correspondences used to estimate the
        IR->EO homography. Defaults to the Hadron 640R calibration points.

    Returns
    -------
    fused_rgb : np.ndarray
        Fused image as an ``(H, W, 3)`` uint8 RGB array.
    rgb_weight : np.ndarray
        Basis coverage of the EO value channel (diagnostic output).
    ir_weight : np.ndarray
        Basis coverage of the IR channel (diagnostic output).
    """
    M, N = block_size
    m, n = subblock_resolution

    if homography_points is None:
        homography_points = (DEFAULT_IR_POINTS, DEFAULT_EO_POINTS)

    # Align the EO frame to the IR frame.
    img_rgb = cv2.cvtColor(eo_img, cv2.COLOR_BGR2RGB)
    cropped_eo_img = cropRGBToMatchIR(img_rgb, ir_img, homography_points=homography_points)

    visible_img = Image.fromarray(cropped_eo_img).convert("RGB")
    infrared_img = Image.fromarray(ir_img).convert("L")

    # Fuse the EO value channel with the normalized IR intensity.
    visible_hsv = rgb_to_hsv(np.array(visible_img) / 255.0)
    infrared = np.array(infrared_img) / 255.0

    A = triangular_basis(M, m, radius)
    B = triangular_basis(N, n, radius)
    fused_V, alpha_map, rgb_weight, ir_weight = fuse_images(
        visible_hsv[..., 2], infrared, M, N, A, B
    )

    # Recombine with the original hue and saturation.
    fused_hsv = np.stack([visible_hsv[..., 0], visible_hsv[..., 1], fused_V], axis=-1)
    fused_rgb = np.clip(hsv_to_rgb(fused_hsv), 0, 1)
    fused_rgb_uint8 = (fused_rgb * 255).astype(np.uint8)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    alpha_img = (np.clip(alpha_map, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(alpha_img).save(os.path.join(output_dir, "alpha_map.jpg"))

    return fused_rgb_uint8, rgb_weight, ir_weight
