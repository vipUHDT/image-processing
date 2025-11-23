import numpy as np



# Fuzzy transform
def fuzzy_transform(block, A, B):
    m, n = A.shape[0], B.shape[0]
    SB = np.zeros((m, n))
    weight_block = np.zeros((8,8))
    for k in range(m):
        for l in range(n):
            weights = np.outer(A[k], B[l])
            numerator = np.sum(block * weights)
            denominator = np.sum(weights)
            SB[k, l] = numerator / denominator if denominator != 0 else 0
            weight_block += block*weights
    weight_block = weight_block/225
    return SB,weight_block