import torch
import logging
from typing import Tuple, Optional
from .global_brand_state import global_brand_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaGlobalBrandAccess:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_type": (["logo", "font", "color_palette", "brand_info"], {"default": "logo"}),
                "logo_type": (["vertical_color", "vertical_mono", "horizontal_color", "horizontal_mono", "icon"], {"default": "vertical_color"}),
                "font_type": (["primary", "secondary", "tertiary"], {"default": "primary"}),
                "font_variant": (["", "bold", "italic"], {"default": ""}),
                "include_mask": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("logo_image", "logo_mask", "font_path", "color_palette", "brand_info")

    FUNCTION = "get_global_brand_asset"
    CATEGORY = "apzmedia_brand"

    def get_global_brand_asset(self, asset_type, logo_type, font_type, font_variant, include_mask):
        """
        Get brand assets from global state without requiring explicit connections.
        
        Args:
            asset_type: Type of asset to retrieve (logo, font, color_palette, brand_info)
            logo_type: Type of logo (vertical_color, vertical_mono, horizontal_color, horizontal_mono, icon)
            font_type: Type of font (primary, secondary, tertiary)
            font_variant: Font variant (bold, italic, or empty for regular)
            include_mask: Whether to include logo mask for logo assets
            
        Returns:
            Tuple of requested brand assets
        """
        try:
            # Check if assets are loaded
            if not global_brand_state.is_assets_loaded():
                logger.warning("No brand assets loaded in global state")
                return self._return_empty_assets()
            
            if asset_type == "logo":
                return self._get_logo_asset(logo_type, include_mask)
            elif asset_type == "font":
                return self._get_font_asset(font_type, font_variant)
            elif asset_type == "color_palette":
                return self._get_color_palette_asset()
            elif asset_type == "brand_info":
                return self._get_brand_info_asset()
            else:
                logger.error(f"Unknown asset type: {asset_type}")
                return self._return_empty_assets()
                
        except Exception as e:
            logger.error(f"Failed to get global brand asset: {str(e)}")
            return self._return_empty_assets()

    def _get_logo_asset(self, logo_type: str, include_mask: bool) -> Tuple:
        """Get logo asset from global state."""
        try:
            if include_mask:
                logo_image, logo_mask = global_brand_state.get_logo(logo_type, include_mask=True)
                return (logo_image, logo_mask, "", "", "")
            else:
                logo_image = global_brand_state.get_logo(logo_type, include_mask=False)
                return (logo_image, torch.zeros((1, 64, 64)), "", "", "")
        except Exception as e:
            logger.error(f"Failed to get logo asset: {str(e)}")
            return self._return_empty_assets()

    def _get_font_asset(self, font_type: str, font_variant: str) -> Tuple:
        """Get font asset from global state."""
        try:
            font_path = global_brand_state.get_font(font_type, font_variant)
            return (torch.zeros((3, 64, 64)), torch.zeros((1, 64, 64)), font_path, "", "")
        except Exception as e:
            logger.error(f"Failed to get font asset: {str(e)}")
            return self._return_empty_assets()

    def _get_color_palette_asset(self) -> Tuple:
        """Get color palette from global state."""
        try:
            color_palette = global_brand_state.get_color_palette()
            return (torch.zeros((3, 64, 64)), torch.zeros((1, 64, 64)), "", color_palette, "")
        except Exception as e:
            logger.error(f"Failed to get color palette: {str(e)}")
            return self._return_empty_assets()

    def _get_brand_info_asset(self) -> Tuple:
        """Get brand info from global state."""
        try:
            brand_name = global_brand_state.get_brand_name()
            status_message = global_brand_state.get_status_message()
            brand_info = f"Brand: {brand_name}\nStatus: {status_message}"
            return (torch.zeros((3, 64, 64)), torch.zeros((1, 64, 64)), "", "", brand_info)
        except Exception as e:
            logger.error(f"Failed to get brand info: {str(e)}")
            return self._return_empty_assets()

    def _return_empty_assets(self) -> Tuple:
        """Return empty assets when nothing is available."""
        return (
            torch.zeros((3, 64, 64)),  # empty logo image
            torch.zeros((1, 64, 64)),  # empty logo mask
            "",  # empty font path
            "[]",  # empty color palette
            "No brand assets loaded"  # empty brand info
        )

class APZmediaGlobalBrandStatus:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "check_status": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("brand_name", "status_message", "load_status")

    FUNCTION = "get_global_brand_status"
    CATEGORY = "apzmedia_brand"

    def get_global_brand_status(self, check_status):
        """
        Get the current status of global brand assets.
        
        Args:
            check_status: Whether to check the status (always returns current status)
            
        Returns:
            Tuple of brand name, status message, and load status
        """
        try:
            brand_name = global_brand_state.get_brand_name()
            status_message = global_brand_state.get_status_message()
            is_loaded = global_brand_state.is_assets_loaded()
            
            load_status = "✅ Loaded" if is_loaded else "❌ Not Loaded"
            
            return (brand_name, status_message, load_status)
            
        except Exception as e:
            logger.error(f"Failed to get global brand status: {str(e)}")
            return ("Unknown Brand", "Error getting status", "❌ Error")

NODE_CLASS_MAPPINGS = {
    "APZmediaGlobalBrandAccess": APZmediaGlobalBrandAccess,
    "APZmediaGlobalBrandStatus": APZmediaGlobalBrandStatus,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaGlobalBrandAccess": "APZmedia - Global Brand Asset Access",
    "APZmediaGlobalBrandStatus": "APZmedia - Global Brand Status",
} 