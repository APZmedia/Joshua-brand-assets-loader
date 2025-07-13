import torch
import logging
import re
from PIL import Image
import numpy as np
from typing import Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaSolidColor:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "hex_color": ("STRING", {"default": "#FF0000", "multiline": False}),
                "width": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                "height": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
            },
            "optional": {
                "alpha": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("solid_color_image",)

    FUNCTION = "create_solid_color"
    CATEGORY = "apzmedia_brand"

    def create_solid_color(self, hex_color: str, width: int, height: int, alpha: float = 1.0):
        """
        Create a solid color image from hex color value and dimensions.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000", "FF0000", "#FF0000FF")
            width: Image width in pixels
            height: Image height in pixels
            alpha: Alpha/opacity value (0.0 to 1.0)
            
        Returns:
            Solid color image tensor in (1, H, W, 3) format for ComfyUI
        """
        try:
            # Validate and parse hex color
            rgb_values = self._parse_hex_color(hex_color)
            if rgb_values is None:
                logger.error(f"Invalid hex color format: {hex_color}")
                return self._create_error_image(width, height)
            
            r, g, b = rgb_values
            
            # Validate dimensions
            if width <= 0 or height <= 0:
                logger.error(f"Invalid dimensions: width={width}, height={height}")
                return self._create_error_image(512, 512)
            
            # Validate alpha
            alpha = max(0.0, min(1.0, alpha))
            
            logger.info(f"Creating solid color image: hex={hex_color}, rgb=({r},{g},{b}), size={width}x{height}, alpha={alpha}")
            
            # Create solid color image
            # Convert RGB values (0-255) to float (0-1)
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0
            
            # Create tensor with shape (3, H, W) for RGB channels
            color_tensor = torch.zeros(3, height, width, dtype=torch.float32)
            color_tensor[0, :, :] = r_norm  # Red channel
            color_tensor[1, :, :] = g_norm  # Green channel
            color_tensor[2, :, :] = b_norm  # Blue channel
            
            # Apply alpha if less than 1.0
            if alpha < 1.0:
                color_tensor = color_tensor * alpha
            
            # Convert to ComfyUI format (1, H, W, 3)
            result = color_tensor.permute(1, 2, 0).unsqueeze(0)  # (3, H, W) -> (H, W, 3) -> (1, H, W, 3)
            
            logger.info(f"Created solid color image: shape={result.shape}, dtype={result.dtype}")
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to create solid color image: {str(e)}")
            return self._create_error_image(width, height)

    def _parse_hex_color(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Parse hex color string and return RGB values.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000", "FF0000", "#FF0000FF")
            
        Returns:
            Tuple of (R, G, B) values (0-255) or None if invalid
        """
        try:
            # Remove # if present
            hex_color = hex_color.strip().upper()
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            
            # Validate hex format
            if not re.match(r'^[0-9A-F]{6}([0-9A-F]{2})?$', hex_color):
                return None
            
            # Extract RGB values (first 6 characters)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Validate RGB values
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                return None
            
            return (r, g, b)
            
        except Exception as e:
            logger.error(f"Failed to parse hex color '{hex_color}': {str(e)}")
            return None

    def _create_error_image(self, width: int, height: int):
        """
        Create a red error image when something goes wrong.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Red error image tensor in (1, H, W, 3) format
        """
        try:
            # Create red error image
            error_tensor = torch.zeros(3, height, width, dtype=torch.float32)
            error_tensor[0, :, :] = 1.0  # Red channel
            error_tensor[1, :, :] = 0.0  # Green channel
            error_tensor[2, :, :] = 0.0  # Blue channel
            
            # Convert to ComfyUI format
            result = error_tensor.permute(1, 2, 0).unsqueeze(0)
            
            logger.info(f"Created error image: shape={result.shape}")
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to create error image: {str(e)}")
            # Return minimal valid tensor as last resort
            return (torch.zeros(1, 512, 512, 3, dtype=torch.float32),)

# Node class mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaSolidColor": APZmediaSolidColor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaSolidColor": "APZmedia Solid Color"
} 