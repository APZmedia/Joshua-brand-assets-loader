import os
import torch
from PIL import Image
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaBrandAssetLoader:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_type": ("STRING", {"choices": ["logo", "font", "color"]}),
                "file_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("logo_image", "logo_mask", "font_path_or_url", "color_hex")

    FUNCTION = "load_asset"

    CATEGORY = "apzmedia_brand"

    def load_asset(self, asset_type, file_path):
        """
        Load brand assets from file path with comprehensive error handling and validation.
        
        Args:
            asset_type: Type of asset to load (logo, font, color)
            file_path: Path to the asset file
            
        Returns:
            Tuple of (logo_image, logo_mask, font_path_or_url, color_hex)
        """
        # Input validation
        if not file_path or not file_path.strip():
            logger.warning("File path is empty or invalid")
            return self._return_defaults()
        
        if asset_type not in ["logo", "font", "color"]:
            logger.error(f"Invalid asset type: {asset_type}")
            return self._return_defaults()
        
        # Validate file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return self._return_defaults()
        
        try:
            if asset_type == "logo":
                return self._load_logo_asset(file_path)
            elif asset_type == "font":
                return self._load_font_asset(file_path)
            elif asset_type == "color":
                return self._load_color_asset(file_path)
        except Exception as e:
            logger.error(f"Failed to load {asset_type} asset from '{file_path}': {str(e)}")
            return self._return_defaults()
        
        return self._return_defaults()

    def _load_logo_asset(self, file_path):
        """Load logo asset from file path with error handling."""
        try:
            # Validate file format
            if not self._is_valid_image_file(file_path):
                logger.error(f"Invalid image file format: {file_path}")
                return self._return_defaults()
            
            image = Image.open(file_path).convert("RGBA")
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

    def _load_font_asset(self, file_path):
        """Load font asset from file path with error handling."""
        try:
            # Validate file format
            if not self._is_valid_font_file(file_path):
                logger.error(f"Invalid font file format: {file_path}")
                return self._return_defaults()
            
            # Return the file path for font assets
            return (None, None, file_path, "")
            
        except Exception as e:
            logger.error(f"Failed to load font: {str(e)}")
            return self._return_defaults()

    def _load_color_asset(self, file_path):
        """Load color asset from file path with error handling."""
        try:
            # Validate file format
            if not self._is_valid_color_file(file_path):
                logger.error(f"Invalid color file format: {file_path}")
                return self._return_defaults()
            
            with open(file_path, "r") as f:
                color_hex = f.read().strip()
            
            # Validate hex color format
            if not self._is_valid_hex_color(color_hex):
                logger.warning(f"Invalid hex color format: {color_hex}")
                color_hex = "#000000"  # Default to black
            
            return (None, None, "", color_hex)
            
        except Exception as e:
            logger.error(f"Failed to load color: {str(e)}")
            return self._return_defaults()

    def _is_valid_image_file(self, file_path):
        """Validate if file is a supported image format."""
        supported_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _is_valid_font_file(self, file_path):
        """Validate if file is a supported font format."""
        supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _is_valid_color_file(self, file_path):
        """Validate if file is a supported color format."""
        supported_extensions = [".txt", ".color", ".hex"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

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
