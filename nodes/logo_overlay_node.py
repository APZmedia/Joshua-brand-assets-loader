import torch
import torch.nn.functional as F
import logging
import os
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaLogoOverlay:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "background_image": ("IMAGE", {}),
                "logo_file_path": ("STRING", {"default": "", "multiline": False}),
                "logo_type": ("STRING", {"choices": ["vertical", "horizontal", "auto"]}),
                "position": ("STRING", {"choices": [
                    "top-left", "top-center", "top-right",
                    "center-left", "center", "center-right",
                    "bottom-left", "bottom-center", "bottom-right"
                ]}),
                "scale_percentage": ("FLOAT", {"default": 15.0, "min": 1.0, "max": 100.0, "step": 0.5}),
                "padding_percentage": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 50.0, "step": 0.5}),
                "rotation_degrees": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0}),
                "offset_x": ("INT", {"default": 0, "min": -1000, "max": 1000}),
                "offset_y": ("INT", {"default": 0, "min": -1000, "max": 1000}),
            },
            "optional": {
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blend_mode": ("STRING", {"choices": ["normal", "multiply", "screen", "overlay"], "default": "normal"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("overlaid_image",)

    FUNCTION = "overlay_logo"

    CATEGORY = "apzmedia_brand"

    def overlay_logo(self, background_image, logo_file_path, logo_type, position, scale_percentage, 
                    padding_percentage, rotation_degrees, offset_x, offset_y, opacity=1.0, blend_mode="normal"):
        """
        Overlay logo on background image with comprehensive positioning and scaling.
        
        Args:
            background_image: Background image tensor (C, H, W) format with RGB channels
            logo_file_path: Path to logo file
            logo_type: Logo orientation (vertical, horizontal, auto)
            position: Logo position on background
            scale_percentage: Logo size as percentage of background
            padding_percentage: Padding from borders as percentage
            rotation_degrees: Logo rotation in degrees
            offset_x: Horizontal offset in pixels
            offset_y: Vertical offset in pixels
            opacity: Logo opacity
            blend_mode: Blending mode
            
        Returns:
            Image with logo overlaid in (C, H, W) format
        """
        try:
            # Input validation
            if not self._validate_inputs(background_image, logo_file_path):
                logger.error("Invalid inputs")
                return self._create_error_overlay(background_image)
            
            # Load and process logo
            logo_tensor, has_alpha = self._load_logo(logo_file_path)
            if logo_tensor is None:
                logger.error(f"Failed to load logo from: {logo_file_path}")
                return self._create_error_overlay(background_image)
            
            # Determine logo orientation
            if logo_type == "auto":
                logo_type = self._detect_logo_orientation(logo_tensor)
            
            # Scale logo based on orientation and percentage
            scaled_logo = self._scale_logo_by_percentage(logo_tensor, background_image, logo_type, scale_percentage)
            
            # Apply rotation
            if rotation_degrees != 0:
                scaled_logo = self._rotate_logo(scaled_logo, rotation_degrees)
            
            # Calculate position with padding and offset
            x, y = self._calculate_position_with_padding(
                background_image, scaled_logo, position, padding_percentage, offset_x, offset_y
            )
            
            # Apply opacity
            scaled_logo = scaled_logo * opacity
            
            # Blend logo into background
            result = self._blend_logo(background_image, scaled_logo, x, y, blend_mode, has_alpha)
            
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to overlay logo: {str(e)}")
            return self._create_error_overlay(background_image)

    def _validate_inputs(self, background_image, logo_file_path):
        """Validate input parameters."""
        try:
            # Check background image
            if not isinstance(background_image, torch.Tensor):
                logger.error("Background image must be a PyTorch tensor")
                return False
            
            if background_image.dim() != 3 or background_image.shape[0] != 3:
                logger.error("Background image must be 3D tensor with 3 channels (RGB)")
                return False
            
            # Check logo file path
            if not logo_file_path or not logo_file_path.strip():
                logger.error("Logo file path is empty")
                return False
            
            if not os.path.exists(logo_file_path):
                logger.error(f"Logo file not found: {logo_file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            return False

    def _load_logo(self, logo_file_path):
        """Load logo from file path and detect alpha channel."""
        try:
            # Check file format
            if not self._is_valid_image_file(logo_file_path):
                logger.error(f"Invalid image file format: {logo_file_path}")
                return None, False
            
            # Load image
            image = Image.open(logo_file_path)
            
            # Check if image has alpha channel
            has_alpha = image.mode == "RGBA"
            
            # Convert to RGBA if not already
            if not has_alpha:
                image = image.convert("RGBA")
            
            # Convert to tensor - ensure RGB order (C, H, W)
            np_image = np.array(image).astype(np.float32) / 255.0
            tensor = torch.from_numpy(np_image).permute(2, 0, 1)  # (C, H, W)
            
            return tensor, has_alpha
            
        except Exception as e:
            logger.error(f"Failed to load logo: {str(e)}")
            return None, False

    def _is_valid_image_file(self, file_path):
        """Validate if file is a supported image format."""
        supported_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _detect_logo_orientation(self, logo_tensor):
        """Auto-detect if logo is vertical or horizontal."""
        height, width = logo_tensor.shape[1], logo_tensor.shape[2]
        aspect_ratio = height / width
        
        if aspect_ratio > 1.2:  # Height is significantly larger
            return "vertical"
        elif aspect_ratio < 0.8:  # Width is significantly larger
            return "horizontal"
        else:  # Roughly square
            return "horizontal"  # Default to horizontal for square logos

    def _scale_logo_by_percentage(self, logo_tensor, background_image, logo_type, scale_percentage):
        """Scale logo based on percentage of background image."""
        try:
            bg_height, bg_width = background_image.shape[1], background_image.shape[2]
            logo_height, logo_width = logo_tensor.shape[1], logo_tensor.shape[2]
            
            # Calculate target size based on logo type and percentage
            if logo_type == "vertical":
                # Scale based on height percentage
                target_height = int(bg_height * (scale_percentage / 100.0))
                aspect_ratio = logo_width / logo_height
                target_width = int(target_height * aspect_ratio)
            else:  # horizontal
                # Scale based on width percentage
                target_width = int(bg_width * (scale_percentage / 100.0))
                aspect_ratio = logo_height / logo_width
                target_height = int(target_width * aspect_ratio)
            
            # Ensure minimum size
            target_width = max(target_width, 1)
            target_height = max(target_height, 1)
            
            # Scale logo - maintain (C, H, W) format
            scaled_logo = F.interpolate(
                logo_tensor.unsqueeze(0),
                size=(target_height, target_width),
                mode="bilinear",
                align_corners=False
            ).squeeze(0)
            
            return scaled_logo
            
        except Exception as e:
            logger.error(f"Failed to scale logo: {str(e)}")
            return logo_tensor

    def _rotate_logo(self, logo_tensor, rotation_degrees):
        """Rotate logo by specified degrees."""
        try:
            if rotation_degrees == 0:
                return logo_tensor
            
            # Convert degrees to radians
            angle_rad = torch.tensor(rotation_degrees * (3.14159 / 180.0))
            
            # Create rotation matrix
            cos_a = torch.cos(angle_rad)
            sin_a = torch.sin(angle_rad)
            
            # Apply rotation using grid_sample - maintain (C, H, W) format
            grid = self._create_rotation_grid(logo_tensor.shape[1], logo_tensor.shape[2], cos_a, sin_a)
            
            rotated = F.grid_sample(
                logo_tensor.unsqueeze(0),
                grid,
                mode="bilinear",
                padding_mode="zeros",
                align_corners=False
            ).squeeze(0)
            
            return rotated
            
        except Exception as e:
            logger.error(f"Failed to rotate logo: {str(e)}")
            return logo_tensor

    def _create_rotation_grid(self, height, width, cos_a, sin_a):
        """Create rotation grid for grid_sample."""
        # Create coordinate grid
        y, x = torch.meshgrid(
            torch.linspace(-1, 1, height),
            torch.linspace(-1, 1, width),
            indexing='ij'
        )
        
        # Apply rotation transformation
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a
        
        # Stack coordinates
        grid = torch.stack([x_rot, y_rot], dim=-1).unsqueeze(0)
        
        return grid

    def _calculate_position_with_padding(self, background_image, logo_tensor, position, padding_percentage, offset_x, offset_y):
        """Calculate logo position with padding and offset."""
        try:
            bg_height, bg_width = background_image.shape[1], background_image.shape[2]
            logo_height, logo_width = logo_tensor.shape[1], logo_tensor.shape[2]
            
            # Calculate padding in pixels
            padding_pixels = int(min(bg_height, bg_width) * (padding_percentage / 100.0))
            
            # Base positions with padding
            positions = {
                "top-left": (padding_pixels, padding_pixels),
                "top-center": ((bg_width - logo_width) // 2, padding_pixels),
                "top-right": (bg_width - logo_width - padding_pixels, padding_pixels),
                "center-left": (padding_pixels, (bg_height - logo_height) // 2),
                "center": ((bg_width - logo_width) // 2, (bg_height - logo_height) // 2),
                "center-right": (bg_width - logo_width - padding_pixels, (bg_height - logo_height) // 2),
                "bottom-left": (padding_pixels, bg_height - logo_height - padding_pixels),
                "bottom-center": ((bg_width - logo_width) // 2, bg_height - logo_height - padding_pixels),
                "bottom-right": (bg_width - logo_width - padding_pixels, bg_height - logo_height - padding_pixels),
            }
            
            x, y = positions.get(position, (0, 0))
            
            # Apply offset
            x += offset_x
            y += offset_y
            
            # Clamp to boundaries
            x = max(0, min(x, bg_width - logo_width))
            y = max(0, min(y, bg_height - logo_height))
            
            return x, y
            
        except Exception as e:
            logger.error(f"Failed to calculate position: {str(e)}")
            return 0, 0

    def _blend_logo(self, background_image, logo_tensor, x, y, blend_mode, has_alpha):
        """Blend logo into background image."""
        try:
            logo_height, logo_width = logo_tensor.shape[1], logo_tensor.shape[2]
            
            # Extract background region - maintain (C, H, W) format
            bg_region = background_image[:, y:y+logo_height, x:x+logo_width]
            
            # Handle alpha channel
            if has_alpha and logo_tensor.shape[0] == 4:
                # Separate RGB and alpha - maintain (C, H, W) format
                logo_rgb = logo_tensor[:3, :, :]  # RGB channels
                logo_alpha = logo_tensor[3:4, :, :].repeat(3, 1, 1)  # Alpha channel repeated for RGB
                
                # Apply blend mode to RGB
                if blend_mode == "normal":
                    blended_rgb = logo_rgb
                elif blend_mode == "multiply":
                    blended_rgb = bg_region * logo_rgb
                elif blend_mode == "screen":
                    blended_rgb = 1 - (1 - bg_region) * (1 - logo_rgb)
                elif blend_mode == "overlay":
                    blended_rgb = torch.where(bg_region < 0.5, 
                                            2 * bg_region * logo_rgb, 
                                            1 - 2 * (1 - bg_region) * (1 - logo_rgb))
                else:
                    blended_rgb = logo_rgb
                
                # Apply alpha blending - maintain (C, H, W) format
                result = background_image.clone()
                result[:, y:y+logo_height, x:x+logo_width] = (
                    blended_rgb * logo_alpha + bg_region * (1 - logo_alpha)
                )
            else:
                # No alpha channel, apply blend mode directly
                if blend_mode == "normal":
                    blended = logo_tensor[:3, :, :]  # Ensure RGB only
                elif blend_mode == "multiply":
                    blended = bg_region * logo_tensor[:3, :, :]
                elif blend_mode == "screen":
                    blended = 1 - (1 - bg_region) * (1 - logo_tensor[:3, :, :])
                elif blend_mode == "overlay":
                    blended = torch.where(bg_region < 0.5, 
                                        2 * bg_region * logo_tensor[:3, :, :], 
                                        1 - 2 * (1 - bg_region) * (1 - logo_tensor[:3, :, :]))
                else:
                    blended = logo_tensor[:3, :, :]
                
                result = background_image.clone()
                result[:, y:y+logo_height, x:x+logo_width] = blended
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to blend logo: {str(e)}")
            return background_image

    def _create_error_overlay(self, background_image):
        """Create red overlay to indicate error."""
        try:
            # Create red overlay - maintain (C, H, W) format
            red_overlay = torch.zeros_like(background_image)
            red_overlay[0, :, :] = 1.0  # Red channel
            
            # Blend with original image
            error_image = background_image * 0.7 + red_overlay * 0.3
            
            return (error_image,)
            
        except Exception as e:
            logger.error(f"Failed to create error overlay: {str(e)}")
            return (background_image,)

NODE_CLASS_MAPPINGS = {
    "APZmediaLogoOverlay": APZmediaLogoOverlay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaLogoOverlay": "APZmedia - Logo Overlay",
}
