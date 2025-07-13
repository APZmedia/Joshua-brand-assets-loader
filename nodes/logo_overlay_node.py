import torch
import torch.nn.functional as F
import logging
import os
from PIL import Image
import numpy as np
from .global_brand_state import global_brand_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaLogoOverlay:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brand_assets_token": ("STRING", {"default": ""}),
                "background_image": ("IMAGE", {}),
                "logo_selection": (["vertical_color", "vertical_mono", "horizontal_color", "horizontal_mono", "icon"], {"default": "vertical_color"}),
                "logo_type": (["vertical", "horizontal", "auto"], {"default": "auto"}),
                "position": (["top-left", "top-center", "top-right",
                             "center-left", "center", "center-right",
                             "bottom-left", "bottom-center", "bottom-right"], {"default": "bottom-right"}),
                "scale_percentage": ("FLOAT", {"default": 15.0, "min": 1.0, "max": 100.0, "step": 0.5}),
                "padding_percentage": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 50.0, "step": 0.5}),
                "rotation_degrees": ("FLOAT", {"default": 0.0, "min": -180.0, "max": 180.0, "step": 1.0}),
                "offset_x": ("INT", {"default": 0, "min": -1000, "max": 1000}),
                "offset_y": ("INT", {"default": 0, "min": -1000, "max": 1000}),
            },
            "optional": {
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blend_mode": (["normal", "multiply", "screen", "overlay"], {"default": "normal"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("overlaid_image",)

    FUNCTION = "overlay_logo"

    CATEGORY = "apzmedia_brand"

    def overlay_logo(self, brand_assets_token, background_image, logo_selection, logo_type, position, scale_percentage, 
                    padding_percentage, rotation_degrees, offset_x, offset_y, opacity=1.0, blend_mode="normal"):
        """
        Overlay logo on background image with comprehensive positioning and scaling.
        
        Args:
            background_image: Background image tensor (C, H, W) format with RGB channels
            logo_selection: Selected logo from global brand assets
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
            # Normalize background image shape to (3, H, W)
            background_image = self._normalize_input_shape(background_image)
            
            # Input validation
            if not self._validate_inputs(background_image, logo_selection):
                logger.error("Invalid inputs")
                return self._create_error_overlay(background_image)

            logger.info(f"[overlay_logo] background_image: shape={background_image.shape}, dtype={background_image.dtype}, min={background_image.min().item()}, max={background_image.max().item()}, mean={background_image.mean().item()}")

            # Load and process logo from global state
            logo_tensor, logo_mask, has_alpha = self._load_logo_from_global_state(logo_selection)
            if logo_tensor is None:
                logger.error(f"Failed to load logo from global state: {logo_selection}")
                return self._create_error_overlay(background_image)

            logger.info(f"[overlay_logo] logo_tensor: shape={logo_tensor.shape}, dtype={logo_tensor.dtype}, min={logo_tensor.min().item()}, max={logo_tensor.max().item()}, mean={logo_tensor.mean().item()}")
            if logo_mask is not None:
                logger.info(f"[overlay_logo] logo_mask: shape={logo_mask.shape}, dtype={logo_mask.dtype}, min={logo_mask.min().item()}, max={logo_mask.max().item()}, mean={logo_mask.mean().item()}")
            else:
                logger.info("[overlay_logo] logo_mask: None")

            # Determine logo orientation
            if logo_type == "auto":
                logo_type = self._detect_logo_orientation(logo_tensor)

            # Scale logo based on orientation and percentage
            scaled_logo = self._scale_logo_by_percentage(logo_tensor, background_image, logo_type, scale_percentage)
            logger.info(f"[overlay_logo] scaled_logo: shape={scaled_logo.shape}, dtype={scaled_logo.dtype}, min={scaled_logo.min().item()}, max={scaled_logo.max().item()}, mean={scaled_logo.mean().item()}")

            # Apply rotation
            if rotation_degrees != 0:
                scaled_logo = self._rotate_logo(scaled_logo, rotation_degrees)
                logger.info(f"[overlay_logo] rotated_logo: shape={scaled_logo.shape}, dtype={scaled_logo.dtype}, min={scaled_logo.min().item()}, max={scaled_logo.max().item()}, mean={scaled_logo.mean().item()}")

            # Calculate position with padding and offset
            x, y = self._calculate_position_with_padding(
                background_image, scaled_logo, position, padding_percentage, offset_x, offset_y
            )
            logger.info(f"[overlay_logo] logo position: x={x}, y={y}")

            # Apply opacity
            scaled_logo = scaled_logo * opacity
            logger.info(f"[overlay_logo] after opacity: min={scaled_logo.min().item()}, max={scaled_logo.max().item()}, mean={scaled_logo.mean().item()}")

            # Blend logo into background
            result = self._blend_logo(background_image, scaled_logo, logo_mask, x, y, blend_mode, has_alpha)
            logger.info(f"[overlay_logo] result: shape={result.shape}, dtype={result.dtype}, min={result.min().item()}, max={result.max().item()}, mean={result.mean().item()}")

            # Convert result from (3, H, W) to (1, H, W, 3) for ComfyUI
            if result.dim() == 3 and result.shape[0] == 3:
                result = result[[2, 1, 0], :, :]  # Swap R and B channels
                result = result.permute(1, 2, 0).unsqueeze(0)  # (3, H, W) -> (H, W, 3) -> (1, H, W, 3)
                logger.info(f"[overlay_logo] final output shape: {result.shape}")
            else:
                logger.error(f"[overlay_logo] Unexpected result shape before return: {result.shape}")
            return (result,)
        except Exception as e:
            logger.error(f"Failed to overlay logo: {str(e)}")
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
                    # Remove batch dimension
                    background_image = background_image.squeeze(0)
                elif background_image.shape[3] == 3:  # (1, H, W, 3)
                    # Remove batch and permute to (3, H, W)
                    background_image = background_image.squeeze(0).permute(2, 0, 1)
                else:
                    logger.error(f"Unexpected 4D tensor shape: {background_image.shape}")
                    return background_image
            elif background_image.dim() == 3:  # (3, H, W) or (H, W, 3)
                if background_image.shape[0] == 3:  # Already (3, H, W)
                    pass
                elif background_image.shape[2] == 3:  # (H, W, 3)
                    # Permute to (3, H, W)
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

    def _validate_inputs(self, background_image, logo_selection):
        """Validate input parameters."""
        try:
            # Check background image
            if not isinstance(background_image, torch.Tensor):
                logger.error("Background image must be a PyTorch tensor")
                return False
            
            # Check if it's a 3D tensor with 3 channels (RGB)
            if background_image.dim() != 3 or background_image.shape[0] != 3:
                logger.error(f"Background image must be 3D tensor with 3 channels (RGB), got shape {background_image.shape}")
                return False
            
            # Check if brand assets are loaded
            if not global_brand_state.is_assets_loaded():
                logger.error("No brand assets loaded in global state")
                return False
            
            # Check logo selection
            if not logo_selection or logo_selection not in ["vertical_color", "vertical_mono", "horizontal_color", "horizontal_mono", "icon"]:
                logger.error(f"Invalid logo selection: {logo_selection}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            return False

    def _load_logo_from_global_state(self, logo_selection):
        """Load logo from global state and detect alpha channel."""
        try:
            # Get logo and mask from global state
            logo_tensor, logo_mask = global_brand_state.get_logo(logo_selection, include_mask=True)
            
            if logo_tensor is None:
                logger.error(f"Logo not found in global state: {logo_selection}")
                return None, None, False
            
            # Normalize logo tensor shape to (3, H, W)
            logo_tensor = self._normalize_logo_shape(logo_tensor)
            
            # Check if mask has meaningful alpha (not all white)
            has_alpha = torch.any(logo_mask < 1.0)
            
            return logo_tensor, logo_mask, has_alpha
            
        except Exception as e:
            logger.error(f"Failed to load logo from global state: {str(e)}")
            return None, None, False

    def _normalize_logo_shape(self, logo_tensor):
        """Normalize logo tensor to (3, H, W) format."""
        try:
            if not isinstance(logo_tensor, torch.Tensor):
                logger.error("Logo tensor must be a PyTorch tensor")
                return logo_tensor
            
            logger.info(f"[_normalize_logo_shape] input shape: {logo_tensor.shape}")
            
            # Handle different input shapes
            if logo_tensor.dim() == 4:  # (1, H, W, 3) or (1, 3, H, W)
                if logo_tensor.shape[1] == 3:  # (1, 3, H, W)
                    # Remove batch dimension
                    logo_tensor = logo_tensor.squeeze(0)
                elif logo_tensor.shape[3] == 3:  # (1, H, W, 3)
                    # Remove batch and permute to (3, H, W)
                    logo_tensor = logo_tensor.squeeze(0).permute(2, 0, 1)
                else:
                    logger.error(f"Unexpected 4D logo tensor shape: {logo_tensor.shape}")
                    return logo_tensor
            elif logo_tensor.dim() == 3:  # (3, H, W) or (H, W, 3)
                if logo_tensor.shape[0] == 3:  # Already (3, H, W)
                    pass
                elif logo_tensor.shape[2] == 3:  # (H, W, 3)
                    # Permute to (3, H, W)
                    logo_tensor = logo_tensor.permute(2, 0, 1)
                else:
                    logger.error(f"Unexpected 3D logo tensor shape: {logo_tensor.shape}")
                    return logo_tensor
            else:
                logger.error(f"Logo tensor must be 3D or 4D tensor, got {logo_tensor.dim()}D")
                return logo_tensor
            
            logger.info(f"[_normalize_logo_shape] normalized shape: {logo_tensor.shape}")
            return logo_tensor
            
        except Exception as e:
            logger.error(f"Failed to normalize logo shape: {str(e)}")
            return logo_tensor



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
            logger.info(f"[_scale_logo_by_percentage] scaled_logo: shape={scaled_logo.shape}, dtype={scaled_logo.dtype}, min={scaled_logo.min().item()}, max={scaled_logo.max().item()}, mean={scaled_logo.mean().item()}")
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

    def _blend_logo(self, background_image, logo_tensor, logo_mask, x, y, blend_mode, has_alpha):
        """Blend logo into background image using mask from global state."""
        try:
            logo_height, logo_width = logo_tensor.shape[1], logo_tensor.shape[2]
            
            # Extract background region - maintain (C, H, W) format
            bg_region = background_image[:, y:y+logo_height, x:x+logo_width]
            logger.info(f"[_blend_logo] bg_region: shape={bg_region.shape}, dtype={bg_region.dtype}, min={bg_region.min().item()}, max={bg_region.max().item()}, mean={bg_region.mean().item()}")
            logger.info(f"[_blend_logo] logo_tensor: shape={logo_tensor.shape}, dtype={logo_tensor.dtype}, min={logo_tensor.min().item()}, max={logo_tensor.max().item()}, mean={logo_tensor.mean().item()}")
            if logo_mask is not None:
                logger.info(f"[_blend_logo] logo_mask: shape={logo_mask.shape}, dtype={logo_mask.dtype}, min={logo_mask.min().item()}, max={logo_mask.max().item()}, mean={logo_mask.mean().item()}")
            else:
                logger.info("[_blend_logo] logo_mask: None")
            
            # Scale logo mask to match logo size if needed
            if logo_mask.shape[1:] != (logo_height, logo_width):
                logo_mask = F.interpolate(
                    logo_mask.unsqueeze(0),
                    size=(logo_height, logo_width),
                    mode="bilinear",
                    align_corners=False
                ).squeeze(0)
            
            # Ensure mask is 3-channel for RGB blending
            if logo_mask.shape[0] == 1:
                logo_mask = logo_mask.repeat(3, 1, 1)  # (3, H, W)
            
            # Apply blend mode to RGB
            if blend_mode == "normal":
                blended_rgb = logo_tensor
            elif blend_mode == "multiply":
                blended_rgb = bg_region * logo_tensor
            elif blend_mode == "screen":
                blended_rgb = 1 - (1 - bg_region) * (1 - logo_tensor)
            elif blend_mode == "overlay":
                blended_rgb = torch.where(bg_region < 0.5, 
                                        2 * bg_region * logo_tensor, 
                                        1 - 2 * (1 - bg_region) * (1 - logo_tensor))
            else:
                blended_rgb = logo_tensor
            
            # Apply alpha blending - maintain (C, H, W) format
            result = background_image.clone()
            result[:, y:y+logo_height, x:x+logo_width] = (
                blended_rgb * logo_mask + bg_region * (1 - logo_mask)
            )
            logger.info(f"[_blend_logo] result: shape={result.shape}, dtype={result.dtype}, min={result.min().item()}, max={result.max().item()}, mean={result.mean().item()}")
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
            
            # Convert error image to (1, H, W, 3) for ComfyUI
            if error_image.dim() == 3 and error_image.shape[0] == 3:
                error_image = error_image[[2, 1, 0], :, :]  # Swap R and B channels
                error_image = error_image.permute(1, 2, 0).unsqueeze(0)
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
