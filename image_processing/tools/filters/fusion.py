import numpy as np
from PIL import Image
import colorsys
from scipy.ndimage import sobel
import os
import matplotlib.pyplot as plt
import cv2
from image_processing.tools.filters.Fuzzy_transform import *
from image_processing.tools.filters.Basis_Function import *
from image_processing.tools.homography import cropRGBToMatchIR, resizeIRToMatchRGB


def FuzzyFusion(eo_img, ir_img, block_size=(8, 8), subblock_resolution=(15, 15), radius=5, output_dir='Fused'):
    M, N = block_size
    m, n = subblock_resolution
    r = radius
    img_rgb = cv2.cvtColor(eo_img, cv2.COLOR_BGR2RGB)
    # Load images (assumes same size and alignment)
    visible_img = Image.fromarray(img_rgb).convert('RGB')
    infrared_img = Image.fromarray(ir_img).convert('L')

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

    A = triangular_basis(M, m, r)
    B = triangular_basis(N, n, r)
      
    fused_V,alpha_map , rgb_weight,ir_weight = fuse_images(V_visible, infrared, M, N, A, B)
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
    return fused_rgb_uint8, rgb_weight, ir_weight

fused_result,weight_rgb,weight_ir = FuzzyFusion(
        eo_img = cv2.imread('cropped_rgb.png'),
        ir_img = cv2.imread('resized_ir.png'),
        block_size=(8, 8),
        subblock_resolution=(15, 15),
        radius=3,
        output_dir=''
        )
print(weight_rgb)
print(weight_ir)
plt.imshow(fused_result)
plt.show()


