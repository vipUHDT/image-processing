import cv2
from typing import Optional
import numpy as np


def mapPixelCoordinates(
    pixel_position: tuple[int, int],
    homography_matrix: Optional[np.ndarray] = None,
    homography_points: Optional[tuple[np.ndarray, np.ndarray]] = None,
) -> list[float] | list[None]:
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

def cropRGBToMatchIR(rgb_img, ir_img, homography_points):
    h_ir, w_ir = ir_img.shape[:2]

    # Define IR corners
    ir_corners = [
        (0, 0),
        (w_ir - 1, 0),
        (w_ir - 1, h_ir - 1),
        (0, h_ir - 1)
    ]

    # Map IR corners to RGB space
    mapped_corners = [mapPixelCoordinates(pt, homography_points=homography_points) for pt in ir_corners]
    mapped_corners = np.array(mapped_corners, dtype=np.float32)

    # Compute bounding box in RGB image
    x_coords = mapped_corners[:, 0]
    y_coords = mapped_corners[:, 1]
    x_min, x_max = int(np.floor(x_coords.min())), int(np.ceil(x_coords.max()))
    y_min, y_max = int(np.floor(y_coords.min())), int(np.ceil(y_coords.max()))

    # Clip to RGB image bounds
    h_rgb, w_rgb = rgb_img.shape[:2]
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(w_rgb, x_max)
    y_max = min(h_rgb, y_max)

    # Crop
    cropped_rgb = rgb_img[y_min:y_max, x_min:x_max]

    # Resize to match IR dimensions exactly
    resized_rgb = cv2.resize(cropped_rgb, (w_ir, h_ir), interpolation=cv2.INTER_LINEAR)

    return resized_rgb



def resizeIRToMatchRGB(ir_img, cropped_rgb_img):
    # Get target size from cropped RGB
    target_size = (cropped_rgb_img.shape[1], cropped_rgb_img.shape[0])  # (width, height)

    # Resize IR image
    resized_ir = cv2.resize(ir_img, target_size, interpolation=cv2.INTER_LINEAR)

    return resized_ir

eo_img = cv2.imread('RGB-Test/RGB-1.jpg')
ir_img = cv2.imread('IR_Test/IR-1.jpg')

IR_points = np.float32([
    (153,88),(255,68),(269,107),(447,91),(610,311),
    (356,294),(153,459),(156,498),(90,335),(265,427)])

EO_points = np.float32([
    (666,251),(822,229),(844,290),(1117,259),(1369,597),
    (979,566),(670,833),(671,891),(567,628),(839,766)])


cropped_eo_img = cropRGBToMatchIR(
    eo_img,
    ir_img, 
    homography_points=(IR_points, EO_points),)

eo = np.array(cropped_eo_img)
print(eo.shape)