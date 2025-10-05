import torch
import torch.nn.functional as F
import logging
import re
import numpy as np
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaGradientOverlay:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "background_image": ("IMAGE", {}),
                "hex_color": ("STRING", {"default": "#0066CC", "multiline": False}),
                "gradient_type": (["linear", "radial", "conical"], {"default": "linear"}),
                "orientation": (["top", "bottom", "left", "right"], {"default": "top"}),
                "start_position": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "end_position": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "start_opacity": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "end_opacity": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.01}),
            },
            "optional": {
                "blend_mode": (["normal", "multiply", "screen", "overlay", "soft_light", "hard_light"], {"default": "normal"}),
                "gradient_center_x": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "gradient_center_y": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "gradient_radius": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("gradient_overlay_image",)

    FUNCTION = "create_gradient_overlay"
    CATEGORY = "apzmedia_brand"

    def create_gradient_overlay(self, background_image, hex_color, gradient_type, orientation, 
                               start_position, end_position, start_opacity, end_opacity, 
                               blend_mode="normal", gradient_center_x=0.5, gradient_center_y=0.5, 
                               gradient_radius=0.5):
        """
        Create a gradient overlay on the background image.
        
        Args:
            background_image: Background image tensor (C, H, W) format with RGB channels
            hex_color: Hex color string for the gradient
            gradient_type: Type of gradient (linear, radial, conical)
            orientation: Direction for linear gradients ("top", "bottom", "left", "right")
            start_position: Starting position for gradient (0.0 to 1.0)
            end_position: Ending position for gradient (0.0 to 1.0)
            start_opacity: Starting opacity value (0.0 = transparent, 1.0 = opaque)
            end_opacity: Ending opacity value (0.0 = transparent, 1.0 = opaque)
            blend_mode: Blending mode for overlay (normal, multiply, screen, overlay, soft_light, hard_light)
            gradient_center_x: Center X position for radial/conical gradients (0.0 to 1.0)
            gradient_center_y: Center Y position for radial/conical gradients (0.0 to 1.0)
            gradient_radius: Radius for radial gradients (0.0 to 2.0)
            
        Returns:
            Image with gradient overlay in (1, H, W, 3) format
        """
        try:
            # Normalize background image shape to (3, H, W)
            background_image = self._normalize_input_shape(background_image)
            
            # Validate inputs
            if not self._validate_inputs(background_image, hex_color):
                logger.error("Invalid inputs")
                return self._create_error_overlay(background_image)

            logger.info(f"[create_gradient_overlay] background_image: shape={background_image.shape}, dtype={background_image.dtype}")

            # Parse hex color
            rgb_values = self._parse_hex_color(hex_color)
            if rgb_values is None:
                logger.error(f"Invalid hex color format: {hex_color}")
                return self._create_error_overlay(background_image)
            
            r, g, b = rgb_values
            logger.info(f"[create_gradient_overlay] hex_color={hex_color}, rgb=({r},{g},{b})")

            # Create gradient mask with opacity interpolation
            gradient_mask = self._create_gradient_mask(
                background_image, gradient_type, orientation, start_position, end_position,
                start_opacity, end_opacity, gradient_center_x, gradient_center_y, gradient_radius
            )
            
            logger.info(f"[create_gradient_overlay] gradient_mask: shape={gradient_mask.shape}, min={gradient_mask.min().item():.3f}, max={gradient_mask.max().item():.3f}")

            # Create solid color tensor
            color_tensor = self._create_color_tensor(background_image, r, g, b)
            logger.info(f"[create_gradient_overlay] color_tensor: shape={color_tensor.shape}")

            # Apply gradient mask to color (opacity is already included in the mask)
            gradient_overlay = color_tensor * gradient_mask.unsqueeze(0)  # Add channel dimension
            logger.info(f"[create_gradient_overlay] gradient_overlay: shape={gradient_overlay.shape}")

            # Blend with background
            result = self._blend_gradient(background_image, gradient_overlay, gradient_mask, blend_mode)
            logger.info(f"[create_gradient_overlay] result: shape={result.shape}, min={result.min().item():.3f}, max={result.max().item():.3f}")

            # Convert result from (3, H, W) to (1, H, W, 3) for ComfyUI
            if result.dim() == 3 and result.shape[0] == 3:
                result = result.permute(1, 2, 0).unsqueeze(0)  # (3, H, W) -> (H, W, 3) -> (1, H, W, 3)
                logger.info(f"[create_gradient_overlay] final output shape: {result.shape}")
            else:
                logger.error(f"[create_gradient_overlay] Unexpected result shape before return: {result.shape}")
            
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to create gradient overlay: {str(e)}")
            return self._create_error_overlay(background_image)

    def _normalize_input_shape(self, background_image):
        """Normalize background image to (3, H, W) format."""
        try:
            if not isinstance(background_image, torch.Tensor):
                logger.error("Background image must be a PyTorch tensor")
                return background_image
            
            logger.info(f"[_normalize_input_shape] input shape: {background_image.shape}")
            
            # Handle different input shapes
            if background_image.dim() == 4:  # (1, H, W, 3) or (1, 3, H, W)
                if background_image.shape[1] == 3:  # (1, 3, H, W)
                    background_image = background_image.squeeze(0)
                elif background_image.shape[3] == 3:  # (1, H, W, 3)
                    background_image = background_image.squeeze(0).permute(2, 0, 1)
                else:
                    logger.error(f"Unexpected 4D tensor shape: {background_image.shape}")
                    return background_image
            elif background_image.dim() == 3:  # (3, H, W) or (H, W, 3)
                if background_image.shape[0] == 3:  # Already (3, H, W)
                    pass
                elif background_image.shape[2] == 3:  # (H, W, 3)
                    background_image = background_image.permute(2, 0, 1)
                else:
                    logger.error(f"Unexpected 3D tensor shape: {background_image.shape}")
                    return background_image
            else:
                logger.error(f"Background image must be 3D or 4D tensor, got {background_image.dim()}D")
                return background_image
            
            logger.info(f"[_normalize_input_shape] normalized shape: {background_image.shape}")
            return background_image
            
        except Exception as e:
            logger.error(f"Failed to normalize input shape: {str(e)}")
            return background_image

    def _validate_inputs(self, background_image, hex_color):
        """Validate input parameters."""
        try:
            # Check background image
            if not isinstance(background_image, torch.Tensor):
                logger.error("Background image must be a PyTorch tensor")
                return False
            if background_image.dim() != 3 or background_image.shape[0] != 3:
                logger.error(f"Background image must be 3D tensor with 3 channels (RGB), got shape {background_image.shape}")
                return False
            
            # Check hex color
            if not hex_color or not isinstance(hex_color, str):
                logger.error("Hex color must be a non-empty string")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            return False

    def _parse_hex_color(self, hex_color: str) -> Optional[Tuple[int, int, int]]:
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

    def _create_gradient_mask(self, background_image, gradient_type, orientation, start_position, 
                             end_position, start_opacity, end_opacity, gradient_center_x, 
                             gradient_center_y, gradient_radius):
        """
        Create gradient mask based on type and parameters.
        
        Returns:
            Gradient mask tensor in (H, W) format with opacity values
        """
        try:
            height, width = background_image.shape[1], background_image.shape[2]
            
            # Create gradient mask based on type
            if gradient_type == "linear":
                return self._create_linear_gradient_mask(
                    height, width, orientation, start_position, end_position, start_opacity, end_opacity
                )
            elif gradient_type == "radial":
                return self._create_radial_gradient_mask(
                    height, width, gradient_center_x, gradient_center_y, gradient_radius, start_opacity, end_opacity
                )
            elif gradient_type == "conical":
                return self._create_conical_gradient_mask(
                    height, width, gradient_center_x, gradient_center_y, start_opacity, end_opacity
                )
            else:
                logger.error(f"Unknown gradient type: {gradient_type}")
                return torch.zeros(height, width, dtype=torch.float32)
                
        except Exception as e:
            logger.error(f"Failed to create gradient mask: {str(e)}")
            return torch.zeros(background_image.shape[1], background_image.shape[2], dtype=torch.float32)

    def _create_linear_gradient_mask(self, height, width, orientation, start_position, 
                                   end_position, start_opacity, end_opacity):
        """Create linear gradient mask with 4 directional options and start/end positions."""
        try:
            # Create coordinate grids
            y_coords, x_coords = torch.meshgrid(
                torch.arange(height, dtype=torch.float32),
                torch.arange(width, dtype=torch.float32),
                indexing='ij'
            )
            
            # Normalize coordinates to 0-1 range
            y_norm = y_coords / (height - 1) if height > 1 else torch.zeros_like(y_coords)
            x_norm = x_coords / (width - 1) if width > 1 else torch.zeros_like(x_coords)
            
            # Calculate gradient based on orientation
            if orientation == "top":
                # Top to bottom gradient (starts at top, ends at bottom)
                gradient = y_norm
            elif orientation == "bottom":
                # Bottom to top gradient (starts at bottom, ends at top)
                gradient = 1.0 - y_norm
            elif orientation == "left":
                # Left to right gradient (starts at left, ends at right) - FIXED: was inverted
                gradient = 1.0 - x_norm
            elif orientation == "right":
                # Right to left gradient (starts at right, ends at left) - FIXED: was inverted
                gradient = x_norm
            else:
                # Default to top
                gradient = y_norm
            
            # Apply start/end positions - these control WHERE the gradient begins and ends
            # start_position = where gradient starts (0.0 = start of direction, 1.0 = end of direction)
            # end_position = where gradient ends (0.0 = start of direction, 1.0 = end of direction)
            
            # Create mask based on position ranges
            if end_position > start_position:
                # Normal case: gradient from start_position to end_position
                # Before start_position: use start_opacity
                # Between start and end: interpolate from start_opacity to end_opacity
                # After end_position: use end_opacity
                
                # Create position-based mask
                before_start = gradient < start_position
                between_start_end = (gradient >= start_position) & (gradient <= end_position)
                after_end = gradient > end_position
                
                # Initialize mask
                mask = torch.zeros_like(gradient)
                
                # Before start: use start_opacity
                mask[before_start] = start_opacity
                
                # After end: use end_opacity
                mask[after_end] = end_opacity
                
                # Between start and end: interpolate
                if torch.any(between_start_end):
                    # Normalize gradient values between start and end to 0-1
                    normalized_gradient = (gradient[between_start_end] - start_position) / (end_position - start_position)
                    # Interpolate opacity
                    mask[between_start_end] = start_opacity + (end_opacity - start_opacity) * normalized_gradient
                    
            elif end_position < start_position:
                # Reversed case: gradient from end_position to start_position
                before_end = gradient < end_position
                between_end_start = (gradient >= end_position) & (gradient <= start_position)
                after_start = gradient > start_position
                
                # Initialize mask
                mask = torch.zeros_like(gradient)
                
                # Before end: use end_opacity
                mask[before_end] = end_opacity
                
                # After start: use start_opacity
                mask[after_start] = start_opacity
                
                # Between end and start: interpolate
                if torch.any(between_end_start):
                    # Normalize gradient values between end and start to 0-1
                    normalized_gradient = (gradient[between_end_start] - end_position) / (start_position - end_position)
                    # Interpolate opacity (reversed direction)
                    mask[between_end_start] = end_opacity + (start_opacity - end_opacity) * normalized_gradient
                    
            else:
                # Same position: solid color
                mask = torch.full_like(gradient, start_opacity)
            
            return mask
            
        except Exception as e:
            logger.error(f"Failed to create linear gradient mask: {str(e)}")
            return torch.zeros(height, width, dtype=torch.float32)

    def _create_radial_gradient_mask(self, height, width, center_x, center_y, radius, start_opacity, end_opacity):
        """Create radial gradient mask."""
        try:
            # Create coordinate grids
            y_coords, x_coords = torch.meshgrid(
                torch.arange(height, dtype=torch.float32),
                torch.arange(width, dtype=torch.float32),
                indexing='ij'
            )
            
            # Normalize coordinates to 0-1 range
            y_norm = y_coords / (height - 1) if height > 1 else torch.zeros_like(y_coords)
            x_norm = x_coords / (width - 1) if width > 1 else torch.zeros_like(x_coords)
            
            # Calculate distance from center
            center_x_px = center_x * (width - 1) if width > 1 else 0
            center_y_px = center_y * (height - 1) if height > 1 else 0
            
            # Calculate distance from each pixel to center
            dx = x_coords - center_x_px
            dy = y_coords - center_y_px
            distance = torch.sqrt(dx**2 + dy**2)
            
            # Normalize distance by radius
            max_distance = radius * min(width, height) / 2
            normalized_distance = torch.clamp(distance / max_distance, 0, 1)
            
            # Invert so center is 1, edges are 0
            gradient = 1 - normalized_distance
            
            # Interpolate between start_opacity and end_opacity
            mask = start_opacity + (end_opacity - start_opacity) * gradient
            
            return mask
            
        except Exception as e:
            logger.error(f"Failed to create radial gradient mask: {str(e)}")
            return torch.zeros(height, width, dtype=torch.float32)

    def _create_conical_gradient_mask(self, height, width, center_x, center_y, start_opacity, end_opacity):
        """Create conical gradient mask."""
        try:
            # Create coordinate grids
            y_coords, x_coords = torch.meshgrid(
                torch.arange(height, dtype=torch.float32),
                torch.arange(width, dtype=torch.float32),
                indexing='ij'
            )
            
            # Calculate center coordinates
            center_x_px = center_x * (width - 1) if width > 1 else 0
            center_y_px = center_y * (height - 1) if height > 1 else 0
            
            # Calculate angle from center
            dx = x_coords - center_x_px
            dy = y_coords - center_y_px
            angle = torch.atan2(dy, dx)
            
            # Convert angle to 0-1 range
            gradient = (angle + torch.pi) / (2 * torch.pi)
            
            # Interpolate between start_opacity and end_opacity
            mask = start_opacity + (end_opacity - start_opacity) * gradient
            
            return mask
            
        except Exception as e:
            logger.error(f"Failed to create conical gradient mask: {str(e)}")
            return torch.zeros(height, width, dtype=torch.float32)


    def _create_color_tensor(self, background_image, r, g, b):
        """Create solid color tensor matching background dimensions."""
        try:
            height, width = background_image.shape[1], background_image.shape[2]
            
            # Convert RGB values (0-255) to float (0-1)
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0
            
            # Create tensor with shape (3, H, W) for RGB channels
            color_tensor = torch.zeros(3, height, width, dtype=torch.float32)
            color_tensor[0, :, :] = r_norm  # Red channel
            color_tensor[1, :, :] = g_norm  # Green channel
            color_tensor[2, :, :] = b_norm  # Blue channel
            
            return color_tensor
            
        except Exception as e:
            logger.error(f"Failed to create color tensor: {str(e)}")
            return torch.zeros(3, background_image.shape[1], background_image.shape[2], dtype=torch.float32)

    def _blend_gradient(self, background_image, gradient_overlay, gradient_mask, blend_mode):
        """Blend gradient overlay with background image using correct mathematical formulas."""
        try:
            # Apply gradient mask to the overlay first
            alpha = gradient_mask.unsqueeze(0)  # Add channel dimension (1, H, W)
            masked_overlay = gradient_overlay * alpha
            
            if blend_mode == "normal":
                # Simple alpha blending: result = base * (1 - alpha) + overlay * alpha
                result = background_image * (1 - alpha) + masked_overlay
            elif blend_mode == "multiply":
                # Multiply: result = base * overlay, then apply alpha for transparency
                multiplied = background_image * gradient_overlay
                result = background_image * (1 - alpha) + multiplied * alpha
            elif blend_mode == "screen":
                # Screen: result = 1 - (1 - base) * (1 - overlay), then apply alpha for transparency
                screened = 1 - (1 - background_image) * (1 - gradient_overlay)
                result = background_image * (1 - alpha) + screened * alpha
            elif blend_mode == "overlay":
                # Overlay: if base < 0.5: 2 * base * overlay, else: 1 - 2 * (1 - base) * (1 - overlay)
                overlaid = torch.where(
                    background_image < 0.5,
                    2 * background_image * gradient_overlay,
                    1 - 2 * (1 - background_image) * (1 - gradient_overlay)
                )
                result = background_image * (1 - alpha) + overlaid * alpha
            elif blend_mode == "soft_light":
                # Soft light: if overlay < 0.5: base - (1 - 2 * overlay) * base * (1 - base)
                # else: base + (2 * overlay - 1) * (sqrt(base) - base)
                soft_lighted = torch.where(
                    gradient_overlay < 0.5,
                    background_image - (1 - 2 * gradient_overlay) * background_image * (1 - background_image),
                    background_image + (2 * gradient_overlay - 1) * (torch.sqrt(background_image) - background_image)
                )
                result = background_image * (1 - alpha) + soft_lighted * alpha
            elif blend_mode == "hard_light":
                # Hard light: if overlay < 0.5: 2 * base * overlay, else: 1 - 2 * (1 - base) * (1 - overlay)
                hard_lighted = torch.where(
                    gradient_overlay < 0.5,
                    2 * background_image * gradient_overlay,
                    1 - 2 * (1 - background_image) * (1 - gradient_overlay)
                )
                result = background_image * (1 - alpha) + hard_lighted * alpha
            else:
                # Default to normal blending
                result = background_image * (1 - alpha) + masked_overlay
            
            # Clamp values to valid range [0, 1]
            result = torch.clamp(result, 0, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to blend gradient: {str(e)}")
            return background_image

    def _create_error_overlay(self, background_image):
        """Create a red error overlay when something goes wrong."""
        try:
            # Create red error overlay
            error_tensor = torch.zeros_like(background_image)
            error_tensor[0, :, :] = 1.0  # Red channel
            error_tensor[1, :, :] = 0.0  # Green channel
            error_tensor[2, :, :] = 0.0  # Blue channel
            
            # Convert to ComfyUI format
            result = error_tensor.permute(1, 2, 0).unsqueeze(0)
            
            logger.info(f"Created error overlay: shape={result.shape}")
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to create error overlay: {str(e)}")
            # Return minimal valid tensor as last resort
            return (torch.zeros(1, 512, 512, 3, dtype=torch.float32),)

# Node class mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaGradientOverlay": APZmediaGradientOverlay
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaGradientOverlay": "APZmedia Gradient Overlay"
} 