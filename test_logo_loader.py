import torch
from PIL import Image
import numpy as np
from nodes.brand_asset_loader import APZmediaBrandAssetLoader

# Path to your test image
TEST_IMAGE_PATH = "assets/brand_assets/logos/4Agri-logo-V.png"

# Instantiate the loader
loader = APZmediaBrandAssetLoader()

# Use the loader's method
rgb_tensor, alpha_tensor = loader._load_logo_from_path(TEST_IMAGE_PATH)

print("RGB tensor shape:", rgb_tensor.shape)
print("RGB tensor min/max:", rgb_tensor.min().item(), rgb_tensor.max().item())
print("Alpha tensor shape:", alpha_tensor.shape)
print("Alpha tensor min/max:", alpha_tensor.min().item(), alpha_tensor.max().item())

# Convert tensor back to image and save for visual inspection
def tensor_to_pil(tensor):
    arr = (tensor.clamp(0, 1).numpy() * 255).astype(np.uint8)
    if arr.shape[0] == 3:
        arr = np.transpose(arr, (1, 2, 0))
        return Image.fromarray(arr, mode="RGB")
    elif arr.shape[0] == 1:
        arr = arr[0]
        return Image.fromarray(arr, mode="L")
    else:
        raise ValueError("Unexpected tensor shape")

rgb_image = tensor_to_pil(rgb_tensor)
rgb_image.save("test_rgb_output.png")
print("Saved RGB image as test_rgb_output.png")

alpha_image = tensor_to_pil(alpha_tensor)
alpha_image.save("test_alpha_output.png")
print("Saved alpha mask as test_alpha_output.png") 