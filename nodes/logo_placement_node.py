import torch
import torch.nn.functional as F
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaLogoPlacement:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "background_image": ("IMAGE", {}),
                "logo_image": ("IMAGE", {}),
                "logo_mask": ("IMAGE", {}),
                "position": ("STRING", {"choices": [
                    "top-left", "top-center", "top-right",
                    "center-left", "center", "center-right",
                    "bottom-left", "bottom-center", "bottom-right"
                ]}),
                "scale": ("FLOAT", {"default": 0.2, "min": 0.01, "max": 1.0, "step": 0.01}),
                "offset_x": ("INT", {"default": 0, "min": -1000, "max": 1000}),
                "offset_y": ("INT", {"default": 0, "min": -1000, "max": 1000}),
            },
            "optional": {
                "blend_mode": ("STRING", {"choices": ["normal", "multiply", "screen", "overlay"], "default": "normal"}),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("composited_image",)

    FUNCTION = "place_logo"

    CATEGORY = "apzmedia_brand"

    def place_logo(self, background_image, logo_image, logo_mask, position, scale, offset_x, offset_y, blend_mode="normal", opacity=1.0):
        """
        Place logo on background image with comprehensive error handling and validation.
        
        Args:
            background_image: Background image tensor
            logo_image: Logo image tensor
            logo_mask: Logo mask tensor
            position: Logo position on background
            scale: Logo scale factor
            offset_x: Horizontal offset
            offset_y: Vertical offset
            blend_mode: Blending mode for logo
            opacity: Logo opacity
            
        Returns:
            Composited image tensor
        """
        try:
            # Input validation
            if not self._validate_inputs(background_image, logo_image, logo_mask):
                logger.error("Invalid input images")
                return (background_image,)
            
            # Clone inputs to avoid modifying originals
            bg = background_image.clone()
            logo = logo_image.clone()
            mask = logo_mask.clone()
            
            # Get background dimensions
            bg_h, bg_w = bg.shape[1], bg.shape[2]
            
            # Scale logo with aspect ratio preservation
            logo, mask = self._scale_logo(logo, mask, bg_w, bg_h, scale)
            
            # Calculate position with offset
            x, y = self._calculate_position(position, bg_w, bg_h, logo.shape[2], logo.shape[1])
            x += offset_x
            y += offset_y
            
            # Clamp to boundaries
            x, y = self._clamp_position(x, y, bg_w, bg_h, logo.shape[2], logo.shape[1])
            
            # Apply opacity to logo and mask
            logo = logo * opacity
            mask = mask * opacity
            
            # Blend logo into background
            result = self._blend_images(bg, logo, mask, x, y, blend_mode)
            
            return (result,)
            
        except Exception as e:
            logger.error(f"Failed to place logo: {str(e)}")
            # Return original background image on error
            return (background_image,)

    def _validate_inputs(self, background_image, logo_image, logo_mask):
        """Validate input tensors."""
        try:
            # Check if inputs are tensors
            if not isinstance(background_image, torch.Tensor) or not isinstance(logo_image, torch.Tensor) or not isinstance(logo_mask, torch.Tensor):
                logger.error("Inputs must be PyTorch tensors")
                return False
            
            # Check tensor dimensions
            if background_image.dim() != 3 or logo_image.dim() != 3 or logo_mask.dim() != 3:
                logger.error("Input tensors must be 3-dimensional (C, H, W)")
                return False
            
            # Check background image has 3 channels (RGB)
            if background_image.shape[0] != 3:
                logger.error("Background image must have 3 channels (RGB)")
                return False
            
            # Check logo image has 3 channels (RGB)
            if logo_image.shape[0] != 3:
                logger.error("Logo image must have 3 channels (RGB)")
                return False
            
            # Check mask has 1 channel (grayscale)
            if logo_mask.shape[0] != 1:
                logger.error("Logo mask must have 1 channel (grayscale)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            return False

    def _scale_logo(self, logo, mask, bg_w, bg_h, scale):
        """Scale logo and mask while preserving aspect ratio."""
        try:
            # Calculate new dimensions
            new_w = int(bg_w * scale)
            aspect_ratio = logo.shape[1] / logo.shape[2]
            new_h = int(new_w * aspect_ratio)
            
            # Ensure minimum size
            new_w = max(new_w, 1)
            new_h = max(new_h, 1)
            
            # Scale logo
            logo = F.interpolate(
                logo.unsqueeze(0), 
                size=(new_h, new_w), 
                mode="bilinear", 
                align_corners=False
            ).squeeze(0)
            
            # Scale mask
            mask = F.interpolate(
                mask.unsqueeze(0), 
                size=(new_h, new_w), 
                mode="bilinear", 
                align_corners=False
            ).squeeze(0)
            
            return logo, mask
            
        except Exception as e:
            logger.error(f"Failed to scale logo: {str(e)}")
            # Return original logo and mask on error
            return logo, mask

    def _calculate_position(self, position, bg_w, bg_h, logo_w, logo_h):
        """Calculate logo position based on position string."""
        positions = {
            "top-left": (0, 0),
            "top-center": ((bg_w - logo_w) // 2, 0),
            "top-right": (bg_w - logo_w, 0),
            "center-left": (0, (bg_h - logo_h) // 2),
            "center": ((bg_w - logo_w) // 2, (bg_h - logo_h) // 2),
            "center-right": (bg_w - logo_w, (bg_h - logo_h) // 2),
            "bottom-left": (0, bg_h - logo_h),
            "bottom-center": ((bg_w - logo_w) // 2, bg_h - logo_h),
            "bottom-right": (bg_w - logo_w, bg_h - logo_h),
        }
        return positions.get(position, (0, 0))

    def _clamp_position(self, x, y, bg_w, bg_h, logo_w, logo_h):
        """Clamp logo position to background boundaries."""
        x = max(0, min(x, bg_w - logo_w))
        y = max(0, min(y, bg_h - logo_h))
        return x, y

    def _blend_images(self, bg, logo, mask, x, y, blend_mode):
        """Blend logo into background using specified blend mode."""
        try:
            # Ensure mask has correct dimensions
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            if mask.shape[0] == 1:
                mask = mask.repeat(3, 1, 1)
            
            # Get logo dimensions
            logo_h, logo_w = logo.shape[1], logo.shape[2]
            
            # Extract background region
            bg_region = bg[:, y:y+logo_h, x:x+logo_w]
            
            # Apply blend mode
            if blend_mode == "normal":
                blended = logo
            elif blend_mode == "multiply":
                blended = bg_region * logo
            elif blend_mode == "screen":
                blended = 1 - (1 - bg_region) * (1 - logo)
            elif blend_mode == "overlay":
                blended = torch.where(bg_region < 0.5, 
                                    2 * bg_region * logo, 
                                    1 - 2 * (1 - bg_region) * (1 - logo))
            else:
                blended = logo
            
            # Apply mask and blend
            result = bg.clone()
            result[:, y:y+logo_h, x:x+logo_w] = (blended * mask) + (bg_region * (1 - mask))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to blend images: {str(e)}")
            return bg

NODE_CLASS_MAPPINGS = {
    "APZmediaLogoPlacement": APZmediaLogoPlacement,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaLogoPlacement": "APZmedia - Logo Placement",
}
