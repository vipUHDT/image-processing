import numpy as np
from PIL import Image
import colorsys
from scipy.ndimage import sobel
import os
import matplotlib.pyplot as plt
import cv2

def FuzzyFusion(eo_img, ir_img, block_size=(8, 8), subblock_resolution=(15, 15), radius=5, output_dir='Fused'):
    M, N = block_size
    m, n = subblock_resolution
    r = radius
    img_rgb = cv2.cvtColor(eo_img, cv2.COLOR_BGR2RGB)
    # Load images (assumes same size and alignment)
    visible_img = Image.fromarray(img_rgb).convert('RGB')
    infrared_img = Image.fromarray(ir_img).convert('L')

    #if visible_img.size != infrared_img.size:
        #raise ValueError("RGB and IR images must be the same size")

    target_size = visible_img.size

    # Convert visible image to HSV
    visible_np = np.array(visible_img) / 255.0
    H_channel = np.zeros(target_size[::-1])
    S_channel = np.zeros(target_size[::-1])
    V_visible = np.zeros(target_size[::-1])
    for i in range(target_size[1]):
        for j in range(target_size[0]):
            r, g, b = visible_np[i, j]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            H_channel[i, j] = h
            S_channel[i, j] = s
            V_visible[i, j] = v

    # Normalize infrared image
    infrared = np.array(infrared_img) / 255.0

    # Triangular fuzzy basis
    def triangular_basis(domain_size, num_centers, radius):
        centers = np.linspace(0, domain_size - 1, num_centers)
        basis = np.zeros((num_centers, domain_size))
        for k, c in enumerate(centers):
            for i in range(domain_size):
                dist = abs(i - c)
                denom = radius if radius != 0 else 1e-10
                basis[k, i] = max(1 - dist / denom, 0)
        return basis

    A = triangular_basis(M, m, r)
    B = triangular_basis(N, n, r)

    # Fuzzy transform
    def fuzzy_transform(block, A, B):
        m, n = A.shape[0], B.shape[0]
        SB = np.zeros((m, n))
        for k in range(m):
            for l in range(n):
                weights = np.outer(A[k], B[l])
                numerator = np.sum(block * weights)
                denominator = np.sum(weights)
                SB[k, l] = numerator / denominator if denominator != 0 else 0
        return SB

    # Inverse fuzzy transform
    def inverse_fuzzy(SB, A, B):
        M, N = A.shape[1], B.shape[1]
        block = np.zeros((M, N))
        for i in range(M):
            for j in range(N):
                block[i, j] = np.sum(SB * np.outer(A[:, i], B[:, j]))
        return block

    # Fusion
    def fuse_images(img1, img2, M, N, A, B):
        H, W = img1.shape
        fused = np.zeros_like(img1)
        alpha_map = np.zeros_like(img1)
        for i in range(0, H-M+1, M):
            for j in range(0, W-N+1, N):
                Bx = img1[i:i+M, j:j+N]
                By = img2[i:i+M, j:j+N]
                if Bx.shape != (M, N) or By.shape != (M, N):
                    continue

                SBx = fuzzy_transform(Bx, A, B)
                SBy = fuzzy_transform(By, A, B)

                var_x = np.var(SBx)
                var_y = np.var(SBy)
                # Compute fusion weight based on relative variance
                alpha = var_x / (var_x + var_y + 1e-8)  # Avoid divide-by-zero
                alpha = np.clip(alpha, 0.3, 1.0)        # Optional: bias toward IR by lowering min alpha

                # Blend fuzzy transforms
                SBz = alpha * SBx + (1 - alpha) * SBy


                Bz = inverse_fuzzy(SBz, A, B)
                fused[i:i+M, j:j+N] = Bz
                alpha_map[i:i+M, j:j+N] = alpha
                alpha_block = np.full((M, N), alpha)
                alpha_map[i:i+M, j:j+N] = alpha_block

        return fused, alpha_map
    fused_V,alpha_map = fuse_images(V_visible, infrared, M, N, A, B)
    # Slightly boost brightness in IR-dominant areas
    ir_strength_mask = infrared > 0.3  # Adjust threshold as needed
    fused_V[ir_strength_mask] = np.clip(fused_V[ir_strength_mask] * 1.15, 0, 1)
    # Recombine HSV
    H,W =H_channel.shape
    fused_rgb = np.zeros((H , W , 3), dtype=np.float32)
    for i in range(H ):
        for j in range(W):
            h = H_channel[i, j]
            s = S_channel[i, j]
            v = fused_V[i, j]
            r_val, g_val, b_val = colorsys.hsv_to_rgb(h, s, v)
            fused_rgb[i, j] = np.clip([r_val, g_val, b_val], 0, 1)

    fused_rgb_uint8 = (fused_rgb * 255).astype(np.uint8)
    fused_img = Image.fromarray(fused_rgb_uint8)
    alpha_img = (np.clip(alpha_map, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(alpha_img).save(os.path.join(output_dir, 'alpha_map.jpg'))
    return fused_rgb_uint8


fused_result = FuzzyFusion(
        eo_img = cv2.imread('cropped_rgb.png'),
        ir_img = cv2.imread('resized_ir.png'),
        block_size=(8, 8),
        subblock_resolution=(15, 15),
        radius=3,
        output_dir=''
        )
plt.imshow(fused_result)
plt.show()
'''
# Objective metrics
def entropy(img):
    hist = np.histogram(img.flatten(), bins=256, range=(0, 1))[0]
    hist = hist / np.sum(hist)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))

def standard_deviation(img):
    return np.std(img)

def edge_strength(fused, vis, ir):
    def gradient(img):
        gx = sobel(img, axis=0)
        gy = sobel(img, axis=1)
        return np.hypot(gx, gy)
    Gf = gradient(fused)
    Gv = gradient(vis)
    Gi = gradient(ir)
    Qv = np.sum(Gf * Gv) / (np.sum(Gv) + 1e-8)
    Qi = np.sum(Gf * Gi) / (np.sum(Gi) + 1e-8)
    return Qv + Qi

def fusion_loss(fused, vis, ir):
    return entropy(vis) + entropy(ir) - entropy(fused)

def fusion_artifact(fused, vis, ir):
    diff_v = np.abs(fused - vis)
    diff_i = np.abs(fused - ir)
    return entropy(diff_v) + entropy(diff_i)
'''
