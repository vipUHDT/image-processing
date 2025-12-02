from typing import Union

import numpy as np


def pixelToTemperature(
    pixel_value: Union[int, float],
    t_min: float,
    t_max: float,
) -> float:
    """
    Convert an 8-bit pixel value (0–255) to temperature, assuming a linear mapping.

    Parameters
    ----------
    pixel_value : int or float
        8-bit pixel value in [0, 255].
    t_min : float
        Temperature corresponding to pixel value 0.
    t_max : float
        Temperature corresponding to pixel value 255.

    Returns
    -------
    float
        Temperature in the same units as t_min/t_max (e.g., degrees Celsius).
    """
    v = max(0.0, min(255.0, float(pixel_value)))
    return t_min + (v / 255.0) * (t_max - t_min)


def imageToTemperature(
    image_8bit: np.ndarray,
    t_min: float,
    t_max: float,
    dtype=np.float32,
) -> np.ndarray:
    """
    Convert an 8-bit image (H×W or H×W×1) to a temperature map, assuming linear mapping.

    Parameters
    ----------
    image_8bit : np.ndarray
        8-bit image with dtype uint8 and values in [0, 255].
    t_min : float
        Temperature corresponding to value 0.
    t_max : float
        Temperature corresponding to value 255.
    dtype : np.dtype, optional
        Floating dtype for the temperature output (default: np.float32).

    Returns
    -------
    np.ndarray
        Temperature map with same shape as input and dtype `dtype`.
    """
    if image_8bit.dtype != np.uint8:
        raise ValueError(f"Expected image_8bit.dtype == np.uint8, got {image_8bit.dtype}")

    img_f = image_8bit.astype(dtype)
    scale = (t_max - t_min) / 255.0
    temp = t_min + img_f * scale
    return temp

def temperature_to_pixel(
    temperature: Union[float, np.ndarray],
    t_min: float,
    t_max: float,
) -> Union[int, np.ndarray]:
    """
    Convert temperature value(s) to 8-bit pixels, assuming linear mapping.

    Parameters
    ----------
    temperature : float or np.ndarray
        Temperature(s) to convert.
    t_min : float
        Temperature corresponding to pixel value 0.
    t_max : float
        Temperature corresponding to pixel value 255.

    Returns
    -------
    int or np.ndarray
        8-bit pixel value(s) in [0, 255] with dtype uint8.
    """
    temp = np.asarray(temperature, dtype=np.float32)
    
    norm = (temp - t_min) / (t_max - t_min)

    v = np.round(norm * 255.0)
    v = np.clip(v, 0, 255).astype(np.uint8)
    if np.isscalar(temperature):
        return int(v.item())
    return v