import os
import torch
from PIL import Image
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurable base path with fallback options
DEFAULT_ASSET_BASE_PATH = "assets/brand_assets"
ASSET_BASE_PATH = os.getenv("APZMEDIA_ASSET_PATH", DEFAULT_ASSET_BASE_PATH)

# Supported file formats
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]
SUPPORTED_FONT_FORMATS = [".ttf", ".otf", ".woff", ".woff2"]

class APZmediaBrandAssetLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_type": ("STRING", {"choices": ["logo", "font", "color"]}),
                "asset_key": ("STRING", {"default": "default"}),
                "output_format": ("STRING", {"choices": ["local_path", "url"]}),
            },
            "optional": {
                "custom_asset_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("logo_image", "logo_mask", "font_path_or_url", "color_hex")

    FUNCTION = "load_asset"

    CATEGORY = "apzmedia_brand"

    def load_asset(self, asset_type, asset_key, output_format, custom_asset_path=""):
        """
        Load brand assets with comprehensive error handling and validation.
        
        Args:
            asset_type: Type of asset to load (logo, font, color)
            asset_key: Key/name of the asset
            output_format: Output format preference (local_path, url)
            custom_asset_path: Optional custom path override
            
        Returns:
            Tuple of (logo_image, logo_mask, font_path_or_url, color_hex)
        """
        # Input validation
        if not asset_key or not asset_key.strip():
            logger.warning("Asset key is empty or invalid")
            return self._return_defaults()
        
        if asset_type not in ["logo", "font", "color"]:
            logger.error(f"Invalid asset type: {asset_type}")
            return self._return_defaults()
        
        # Determine asset path
        asset_path = self._get_asset_path(asset_type, asset_key, custom_asset_path)
        
        try:
            if asset_type == "logo":
                return self._load_logo_asset(asset_path, asset_key)
            elif asset_type == "font":
                return self._load_font_asset(asset_path, asset_key, output_format)
            elif asset_type == "color":
                return self._load_color_asset(asset_path, asset_key)
        except Exception as e:
            logger.error(f"Failed to load {asset_type} asset '{asset_key}': {str(e)}")
            return self._return_defaults()
        
        return self._return_defaults()

    def _get_asset_path(self, asset_type, asset_key, custom_path=""):
        """Get the appropriate asset path with fallback options."""
        base_path = custom_path if custom_path else ASSET_BASE_PATH
        
        if asset_type == "logo":
            # Try multiple image formats
            for ext in SUPPORTED_IMAGE_FORMATS:
                path = os.path.join(base_path, "logos", f"{asset_key}{ext}")
                if os.path.exists(path):
                    return path
            # Fallback to default path
            return os.path.join(base_path, "logos", f"{asset_key}.png")
        
        elif asset_type == "font":
            # Try multiple font formats
            for ext in SUPPORTED_FONT_FORMATS:
                path = os.path.join(base_path, "fonts", f"{asset_key}{ext}")
                if os.path.exists(path):
                    return path
            # Fallback to default path
            return os.path.join(base_path, "fonts", f"{asset_key}.ttf")
        
        elif asset_type == "color":
            return os.path.join(base_path, "colors", f"{asset_key}.txt")
        
        return ""

    def _load_logo_asset(self, asset_path, asset_key):
        """Load logo asset with error handling."""
        if not os.path.exists(asset_path):
            logger.warning(f"Logo file not found: {asset_path}")
            return self._return_defaults()
        
        try:
            image = Image.open(asset_path).convert("RGBA")
            logo_image = self.image_to_tensor(image)
            
            # Extract alpha channel for mask
            if image.mode == "RGBA":
                mask = image.split()[-1]  # Alpha channel
                logo_mask = self.image_to_tensor(mask, grayscale=True)
            else:
                # Create white mask if no alpha channel
                logo_mask = torch.ones((1, image.height, image.width))
            
            return (logo_image, logo_mask, "", "")
            
        except Exception as e:
            logger.error(f"Failed to load logo image: {str(e)}")
            return self._return_defaults()

    def _load_font_asset(self, asset_path, asset_key, output_format):
        """Load font asset with error handling."""
        if not os.path.exists(asset_path):
            logger.warning(f"Font file not found: {asset_path}")
            return self._return_defaults()
        
        try:
            if output_format == "local_path":
                font_path_or_url = asset_path
            else:
                # Generate URL (this would need to be configured for your setup)
                font_path_or_url = f"https://your-cloud-url/fonts/{asset_key}{os.path.splitext(asset_path)[1]}"
            
            return (None, None, font_path_or_url, "")
            
        except Exception as e:
            logger.error(f"Failed to load font: {str(e)}")
            return self._return_defaults()

    def _load_color_asset(self, asset_path, asset_key):
        """Load color asset with error handling."""
        if not os.path.exists(asset_path):
            logger.warning(f"Color file not found: {asset_path}")
            return self._return_defaults()
        
        try:
            with open(asset_path, "r") as f:
                color_hex = f.read().strip()
            
            # Validate hex color format
            if not self._is_valid_hex_color(color_hex):
                logger.warning(f"Invalid hex color format: {color_hex}")
                color_hex = "#000000"  # Default to black
            
            return (None, None, "", color_hex)
            
        except Exception as e:
            logger.error(f"Failed to load color: {str(e)}")
            return self._return_defaults()

    def _is_valid_hex_color(self, color_hex):
        """Validate hex color format."""
        if not color_hex.startswith("#"):
            return False
        if len(color_hex) not in [4, 7, 9]:  # #RGB, #RRGGBB, #RRGGBBAA
            return False
        try:
            int(color_hex[1:], 16)
            return True
        except ValueError:
            return False

    def _return_defaults(self):
        """Return default values when asset loading fails."""
        return (None, None, "", "")

    def image_to_tensor(self, image, grayscale=False):
        """Convert PIL image to PyTorch tensor with error handling."""
        try:
            if grayscale:
                image = image.convert("L")
                np_image = np.array(image).astype(np.float32) / 255.0
                tensor = torch.from_numpy(np_image).unsqueeze(0)
            else:
                np_image = np.array(image).astype(np.float32) / 255.0
                tensor = torch.from_numpy(np_image).permute(2, 0, 1)
            return tensor
        except Exception as e:
            logger.error(f"Failed to convert image to tensor: {str(e)}")
            # Return a default tensor
            if grayscale:
                return torch.zeros((1, 64, 64))
            else:
                return torch.zeros((3, 64, 64))

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
}
