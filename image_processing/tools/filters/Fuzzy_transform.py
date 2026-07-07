"""Discrete fuzzy transform (F-transform) and block-wise image fusion.

Implements the direct and inverse 2-D fuzzy transform with respect to a pair
of basis-function matrices (see ``Basis_Function.triangular_basis``), plus a
variance-weighted fusion of two aligned single-channel images.
"""

import numpy as np


def fuzzy_transform(block: np.ndarray, A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the direct 2-D fuzzy transform of an image block.

    Parameters
    ----------
    block : np.ndarray
        Image block of shape ``(M, N)``.
    A : np.ndarray
        Row basis matrix of shape ``(m, M)``.
    B : np.ndarray
        Column basis matrix of shape ``(n, N)``.

    Returns
    -------
    SB : np.ndarray
        Fuzzy-transform components of shape ``(m, n)`` where
        ``SB[k, l] = sum_ij block[i, j] * A[k, i] * B[l, j] / sum_ij A[k, i] * B[l, j]``.
    weight_block : np.ndarray
        Per-pixel basis coverage of the block, ``(M, N)``, normalized by the
        number of basis-function pairs.
    """
    # numerator[k, l] = sum_ij block[i, j] * A[k, i] * B[l, j]
    numerator = A @ block @ B.T
    denominator = np.outer(A.sum(axis=1), B.sum(axis=1))
    SB = np.divide(numerator, denominator,
                   out=np.zeros_like(numerator), where=denominator != 0)
    # sum_kl block * outer(A[k], B[l]) = block * outer(A.sum(0), B.sum(0))
    weight_block = block * np.outer(A.sum(axis=0), B.sum(axis=0))
    weight_block = weight_block / (A.shape[0] * B.shape[0])
    return SB, weight_block


def inverse_fuzzy(SB: np.ndarray, A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Reconstruct an image block from its fuzzy-transform components.

    Parameters
    ----------
    SB : np.ndarray
        Fuzzy-transform components of shape ``(m, n)``.
    A : np.ndarray
        Row basis matrix of shape ``(m, M)``.
    B : np.ndarray
        Column basis matrix of shape ``(n, N)``.

    Returns
    -------
    np.ndarray
        Reconstructed block of shape ``(M, N)`` where
        ``block[i, j] = sum_kl SB[k, l] * A[k, i] * B[l, j]``.
    """
    return A.T @ SB @ B


def fuse_images(
    img1: np.ndarray,
    img2: np.ndarray,
    M: int,
    N: int,
    A: np.ndarray,
    B: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Fuse two aligned single-channel images block by block in F-transform space.

    Both images are tiled into non-overlapping ``(M, N)`` blocks. Each pair of
    blocks is transformed, blended with a weight ``alpha`` derived from the
    relative variance of their transform components (higher variance means
    more detail, so it receives more weight), and reconstructed.

    Parameters
    ----------
    img1 : np.ndarray
        First image (e.g., visible/EO value channel), shape ``(H, W)``.
    img2 : np.ndarray
        Second image (e.g., infrared), same shape as ``img1``.
    M, N : int
        Block height and width in pixels.
    A : np.ndarray
        Row basis matrix of shape ``(m, M)``.
    B : np.ndarray
        Column basis matrix of shape ``(n, N)``.

    Returns
    -------
    fused : np.ndarray
        Fused image, same shape as the inputs.
    alpha_map : np.ndarray
        Per-pixel blend weight applied to ``img1`` (block-constant).
    weight_map1 : np.ndarray
        Basis coverage of ``img1`` blocks (diagnostic output).
    weight_map2 : np.ndarray
        Basis coverage of ``img2`` blocks (diagnostic output).
    """
    H, W = img1.shape
    fused = np.zeros_like(img1)
    alpha_map = np.zeros_like(img1)
    weight_map1 = np.zeros_like(img1)
    weight_map2 = np.zeros_like(img1)

    for i in range(0, H - M + 1, M):
        for j in range(0, W - N + 1, N):
            block1 = img1[i:i + M, j:j + N]
            block2 = img2[i:i + M, j:j + N]

            SB1, weighted1 = fuzzy_transform(block1, A, B)
            SB2, weighted2 = fuzzy_transform(block2, A, B)

            # Blend weight from relative variance; clip biases toward img2.
            var1 = np.var(SB1)
            var2 = np.var(SB2)
            alpha = var1 / (var1 + var2 + 1e-8)
            alpha = np.clip(alpha, 0.3, 1.0)

            SB_fused = alpha * SB1 + (1 - alpha) * SB2

            fused[i:i + M, j:j + N] = inverse_fuzzy(SB_fused, A, B)
            alpha_map[i:i + M, j:j + N] = alpha
            weight_map1[i:i + M, j:j + N] = weighted1
            weight_map2[i:i + M, j:j + N] = weighted2

    return fused, alpha_map, weight_map1, weight_map2
