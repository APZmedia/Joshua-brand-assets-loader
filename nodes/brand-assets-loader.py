import os
import torch
from PIL import Image
import numpy as np

# Base path where brand assets are stored locally (changeable)
ASSET_BASE_PATH = "assets/brand_assets"

class APZmediaBrandAssetLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_type": ("STRING", {"choices": ["logo", "font", "color"]}),
                "asset_key": ("STRING", {}),
                "output_format": ("STRING", {"choices": ["local_path", "url"]}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("logo_image", "logo_mask", "font_path_or_url", "color_hex")

    FUNCTION = "load_asset"

    CATEGORY = "apzmedia_brand"

    def load_asset(self, asset_type, asset_key, output_format):
        logo_image = None
        logo_mask = None
        font_path_or_url = ""
        color_hex = ""

        try:
            if asset_type == "logo":
                path = os.path.join(ASSET_BASE_PATH, "logos", f"{asset_key}.png")
                image = Image.open(path).convert("RGBA")
                logo_image = self.image_to_tensor(image)
                mask = image.split()[-1]  # Alpha channel
                logo_mask = self.image_to_tensor(mask, grayscale=True)

            elif asset_type == "font":
                path = os.path.join(ASSET_BASE_PATH, "fonts", f"{asset_key}.ttf")
                font_path_or_url = path if output_format == "local_path" else f"https://your-cloud-url/fonts/{asset_key}.ttf"

            elif asset_type == "color":
                path = os.path.join(ASSET_BASE_PATH, "colors", f"{asset_key}.txt")
                with open(path, "r") as f:
                    color_hex = f.read().strip()

        except Exception as e:
            print(f"[BrandAssetLoader] Warning: Failed to load asset ({asset_type}, {asset_key}). Error: {e}")

        return (logo_image, logo_mask, font_path_or_url, color_hex)

    def image_to_tensor(self, image, grayscale=False):
        if grayscale:
            image = image.convert("L")
            np_image = np.array(image).astype(np.float32) / 255.0
            tensor = torch.from_numpy(np_image).unsqueeze(0)
        else:
            np_image = np.array(image).astype(np.float32) / 255.0
            tensor = torch.from_numpy(np_image).permute(2, 0, 1)
        return tensor

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
}
