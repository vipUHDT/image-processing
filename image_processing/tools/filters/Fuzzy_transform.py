import numpy as np


# Fuzzy transform
def fuzzy_transform(block, A, B):
    m, n = A.shape[0], B.shape[0]
    SB = np.zeros((m, n))
    weight_block = np.zeros((10,10))
    for k in range(m):
        for l in range(n):
            weights = np.outer(A[k], B[l])
            numerator = np.sum(block * weights)
            denominator = np.sum(weights)
            SB[k, l] = numerator / denominator if denominator != 0 else 0
            weight_block += block*weights
    weight_block = weight_block/225
    return SB,weight_block

def inverse_fuzzy(SB, A, B):
        M, N = A.shape[1], B.shape[1]
        block = np.zeros((M, N))
        for i in range(M):
            for j in range(N):
                block[i, j] = np.sum(SB * np.outer(A[:, i], B[:, j]))
        return block

def fuse_images(img1, img2, M, N, A, B):
    H, W = img1.shape
    fused = np.zeros_like(img1)
    alpha_map = np.zeros_like(img1)
    total_w =[]
    expand_rgb = np.zeros_like(img1)
    expand_ir = np.zeros_like(img1)
    for i in range(0, H - M + 1, M):
        for j in range(0, W - N + 1, N):
            Bx = img1[i:i+M, j:j+N]
            By = img2[i:i+M, j:j+N]

            if Bx.shape != (M, N) or By.shape != (M, N):
                continue

            SBx, weighted_rgb = fuzzy_transform(Bx, A, B)
            SBy, weighted_ir = fuzzy_transform(By, A, B)
            
            w_rgb = np
            var_x = np.var(SBx)
            var_y = np.var(SBy)

            # Compute fusion weight based on relative variance
            #alpha = var_x / (var_x + var_y + 1e-8)  # Avoid divide-by-zero
            #alpha = np.clip(alpha, 0.3, 1.0)        # Optional: bias toward IR
            
            # Blend fuzzy transforms
            #SBz = alpha * SBx + (1 - alpha) * SBy
            if var_x>var_y:
                SBz =SBx
            else:
                SBz =SBy
            # Collect block weights
            expand_rgb[i:i+M, j:j+N]= weighted_rgb
            # Reconstruct fused block
            Bz = inverse_fuzzy(SBz, A, B)
            fused[i:i+M, j:j+N] = Bz
            
            # Fill alpha maps
            #alpha_block = np.full((M, N), alpha)
            #alpha_map[i:i+M, j:j+N] = alpha_block
    return fused, alpha_map, expand_rgb,expand_ir