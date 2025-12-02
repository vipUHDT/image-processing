import numpy as np
from PIL import Image
import colorsys
from scipy.ndimage import sobel
import os
import matplotlib.pyplot as plt
import cv2
from image_processing.tools.filters.Basis_Function import *
from image_processing.tools.filters.Fuzzy_transform import *
from image_processing.tools.filters.homography import cropRGBToMatchIR


def FuzzyFusion(eo_img, ir_img, block_size=(8, 8), subblock_resolution=(15, 15), radius=5, output_dir='Fused'):
    M, N = block_size
    m, n = subblock_resolution
    r = radius
    
    img_rgb = cv2.cvtColor(eo_img, cv2.COLOR_BGR2RGB)
    # Load images (assumes same size and alignment)
    IR_points = np.float32([
    (153,88),(255,68),(269,107),(447,91),(610,311),
    (356,294),(153,459),(156,498),(90,335),(265,427),
    (447,165),(600,204),(613,199),(590,194),(606,190),
    (585,180),(600,180),(585,164),(620,182),(598,164),
    (613,172),(592,148),(611,158),(629,169)])

    EO_points = np.float32([
    (666,251),(822,229),(844,290),(1117,259),(1369,597),
    (979,566),(670,833),(671,891),(567,628),(839,766),
    (1116,370),(1349,429),(1372,422),(1335,413),(1359,409),
    (1326,393),(1348,391),(1326,369),(1384,399),(1348,368),
    (1373,382),(1335,345),(1368,358),(1398,375)])

    cropped_eo_img = cropRGBToMatchIR(
    img_rgb,
    ir_img, 
    homography_points=(IR_points, EO_points),)
    plt.imshow(cropped_eo_img)
    target_size = cropped_eo_img.size

    visible_img = Image.fromarray(cropped_eo_img).convert('RGB')
    infared_img = Image.fromarray(ir_img).convert('L')
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
    infrared = np.array(infared_img) / 255.0

    A = triangular_basis(M, m, r)
    B = triangular_basis(N, n, r)
      
    fused_V,alpha_map , rgb_weight,ir_weight = fuse_images(V_visible, infrared, M, N, A, B)
    # Slightly boost brightness in IR-dominant areas
    #ir_strength_mask = infrared > 0.3  # Adjust threshold as needed

    '''
    testing size
    print("cropped_eo_img.shape:", cropped_eo_img.shape)
    print("visible_np.shape:", visible_np.shape)
    print("infrared.shape:", infrared.shape)
    print("fused_V.shape:", fused_V.shape)
    '''

    #fused_V[ir_strength_mask] = np.clip(fused_V[ir_strength_mask] * 1.15, 0, 1)
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
'''
if __name__ == "__main__":
    fused_result,weight_rgb,weight_ir = FuzzyFusion(
            eo_img = cv2.imread('RGB-Test/4_1.png'),
            ir_img = cv2.imread('IR_Test/4_1.png'),
            block_size=(16,16),
            subblock_resolution=(20, 20),
            radius=8,
            output_dir=''
            )
    print(weight_rgb)
    print(weight_rgb.shape)
    plt.imshow(fused_result)
    plt.show()
'''


