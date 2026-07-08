"""Basis functions used by the fuzzy transform."""

import numpy as np


def triangular_basis(domain_size: int, num_centers: int, radius: float) -> np.ndarray:
    """
    Build a set of triangular (hat) basis functions over a discrete domain.

    Each basis function is centered on one of ``num_centers`` evenly spaced
    points in ``[0, domain_size - 1]`` and decreases linearly from 1 at its
    center to 0 at ``radius`` pixels away.

    Parameters
    ----------
    domain_size : int
        Number of samples in the domain (e.g., block width or height).
    num_centers : int
        Number of basis functions to generate.
    radius : float
        Half-width of each triangular function in samples. A radius of 0 is
        replaced with a small epsilon to avoid division by zero.

    Returns
    -------
    np.ndarray
        Array of shape ``(num_centers, domain_size)`` where row ``k`` is the
        k-th basis function evaluated over the domain.
    """
    centers = np.linspace(0, domain_size - 1, num_centers)
    denom = radius if radius != 0 else 1e-10
    dist = np.abs(np.arange(domain_size) - centers[:, None])
    return np.maximum(1 - dist / denom, 0)
