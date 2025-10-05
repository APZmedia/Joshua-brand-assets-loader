import os
import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaBrandAssetReader:
    """
    Brand Asset Reader Node for extracting specific fields from brand assets.
    
    This node demonstrates how to read and use various fields from the
    brand asset loader output in other ComfyUI nodes.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brand_assets": ("BRAND_ASSETS", {}),
                "asset_category": ("STRING", {
                    "choices": ["logo", "font", "color", "metadata", "all"],
                    "default": "all"
                }),
                "specific_asset": ("STRING", {
                    "choices": [
                        "logo_vertical_color", "logo_vertical_mono", "logo_horizontal_color", 
                        "logo_horizontal_mono", "logo_icon",
                        "font_primary", "font_primary_bold", "font_primary_italic",
                        "font_secondary", "font_secondary_bold", "font_secondary_italic",
                        "font_tertiary", "font_tertiary_bold", "font_tertiary_italic",
                        "color_palette", "brand_name", "status_message"
                    ],
                    "default": "brand_name"
                }),
            },
            "optional": {
                "include_debug_info": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("asset_value", "asset_type", "asset_info", "debug_info", "status")
    
    FUNCTION = "read_brand_asset"
    CATEGORY = "apzmedia_brand"

    def read_brand_asset(self, brand_assets, asset_category, specific_asset, include_debug_info=False):
        """
        Read specific fields from brand assets dictionary.
        
        Args:
            brand_assets: Dictionary containing all brand assets
            asset_category: Category of assets to read (logo, font, color, metadata, all)
            specific_asset: Specific asset to extract
            include_debug_info: Whether to include debug information
            
        Returns:
            Tuple of (asset_value, asset_type, asset_info, debug_info, status)
        """
        try:
            # Check if brand assets are valid
            if not brand_assets or not isinstance(brand_assets, dict):
                return self._return_error("Invalid brand assets input")
            
            # Check loading status
            status_message = brand_assets.get("status_message", "")
            if "Error" in status_message or "Failed" in status_message:
                return self._return_error(f"Asset loading failed: {status_message}")
            
            # Extract asset based on category and specific asset
            if asset_category == "all":
                return self._extract_all_assets(brand_assets, include_debug_info)
            elif asset_category == "logo":
                return self._extract_logo_asset(brand_assets, specific_asset, include_debug_info)
            elif asset_category == "font":
                return self._extract_font_asset(brand_assets, specific_asset, include_debug_info)
            elif asset_category == "color":
                return self._extract_color_asset(brand_assets, include_debug_info)
            elif asset_category == "metadata":
                return self._extract_metadata_asset(brand_assets, specific_asset, include_debug_info)
            else:
                return self._return_error(f"Unknown asset category: {asset_category}")
                
        except Exception as e:
            logger.error(f"Error reading brand asset: {e}")
            return self._return_error(f"Error: {str(e)}")

    def _extract_all_assets(self, brand_assets: Dict[str, Any], include_debug_info: bool) -> Tuple:
        """Extract information about all available assets."""
        try:
            # Count available assets
            logo_count = self._count_logo_assets(brand_assets)
            font_count = self._count_font_assets(brand_assets)
            color_available = self._check_color_palette(brand_assets)
            
            asset_info = f"Assets: {logo_count} logos, {font_count} fonts, Colors: {'Yes' if color_available else 'No'}"
            asset_value = f"Logos: {logo_count}, Fonts: {font_count}, Colors: {color_available}"
            asset_type = "summary"
            
            debug_info = ""
            if include_debug_info:
                debug_info = self._generate_debug_info(brand_assets)
            
            status = "Success"
            return (asset_value, asset_type, asset_info, debug_info, status)
            
        except Exception as e:
            return self._return_error(f"Error extracting all assets: {e}")

    def _extract_logo_asset(self, brand_assets: Dict[str, Any], specific_asset: str, include_debug_info: bool) -> Tuple:
        """Extract logo asset information."""
        try:
            # Check if logo exists
            logo_tensor = brand_assets.get(specific_asset)
            mask_tensor = brand_assets.get(f"{specific_asset}_mask")
            
            if logo_tensor is not None:
                # Get tensor shape information
                if hasattr(logo_tensor, 'shape'):
                    shape = logo_tensor.shape
                    asset_value = f"Logo available: {shape}"
                    asset_type = "image_tensor"
                    asset_info = f"Logo: {specific_asset}, Shape: {shape}"
                else:
                    asset_value = "Logo available"
                    asset_type = "image"
                    asset_info = f"Logo: {specific_asset}"
                
                # Check if mask is available
                if mask_tensor is not None:
                    asset_info += f", Mask: Available"
                else:
                    asset_info += f", Mask: Missing"
                
                debug_info = ""
                if include_debug_info:
                    debug_info = f"Logo: {specific_asset}, Shape: {shape if hasattr(logo_tensor, 'shape') else 'Unknown'}"
                
                status = "Success"
                return (asset_value, asset_type, asset_info, debug_info, status)
            else:
                return self._return_error(f"Logo not found: {specific_asset}")
                
        except Exception as e:
            return self._return_error(f"Error extracting logo asset: {e}")

    def _extract_font_asset(self, brand_assets: Dict[str, Any], specific_asset: str, include_debug_info: bool) -> Tuple:
        """Extract font asset information."""
        try:
            font_path = brand_assets.get(specific_asset, "")
            
            if font_path:
                # Validate font path
                if os.path.exists(font_path):
                    asset_value = font_path
                    asset_type = "font_path"
                    asset_info = f"Font: {specific_asset}, Path: {font_path}"
                    
                    # Extract font name
                    font_name = Path(font_path).stem
                    asset_info += f", Name: {font_name}"
                    
                    debug_info = ""
                    if include_debug_info:
                        file_size = os.path.getsize(font_path)
                        debug_info = f"Font: {specific_asset}, Path: {font_path}, Size: {file_size} bytes"
                    
                    status = "Success"
                    return (asset_value, asset_type, asset_info, debug_info, status)
                else:
                    return self._return_error(f"Font file not found: {font_path}")
            else:
                return self._return_error(f"Font not found: {specific_asset}")
                
        except Exception as e:
            return self._return_error(f"Error extracting font asset: {e}")

    def _extract_color_asset(self, brand_assets: Dict[str, Any], include_debug_info: bool) -> Tuple:
        """Extract color palette information."""
        try:
            color_palette_json = brand_assets.get("color_palette", "[]")
            
            if color_palette_json:
                try:
                    colors = json.loads(color_palette_json)
                    if isinstance(colors, list) and len(colors) > 0:
                        asset_value = color_palette_json
                        asset_type = "color_palette"
                        asset_info = f"Color palette: {len(colors)} colors"
                        
                        # List color names
                        color_names = [color.get("name", "Unknown") for color in colors]
                        asset_info += f", Colors: {', '.join(color_names[:3])}"
                        if len(colors) > 3:
                            asset_info += f" and {len(colors) - 3} more"
                        
                        debug_info = ""
                        if include_debug_info:
                            debug_info = f"Color palette: {len(colors)} colors, JSON: {color_palette_json[:100]}..."
                        
                        status = "Success"
                        return (asset_value, asset_type, asset_info, debug_info, status)
                    else:
                        return self._return_error("Empty color palette")
                except json.JSONDecodeError:
                    return self._return_error("Invalid color palette JSON")
            else:
                return self._return_error("No color palette available")
                
        except Exception as e:
            return self._return_error(f"Error extracting color asset: {e}")

    def _extract_metadata_asset(self, brand_assets: Dict[str, Any], specific_asset: str, include_debug_info: bool) -> Tuple:
        """Extract metadata asset information."""
        try:
            if specific_asset == "brand_name":
                brand_name = brand_assets.get("brand_name", "Unknown Brand")
                asset_value = brand_name
                asset_type = "brand_name"
                asset_info = f"Brand: {brand_name}"
                
                debug_info = ""
                if include_debug_info:
                    debug_info = f"Brand name: {brand_name}"
                
                status = "Success"
                return (asset_value, asset_type, asset_info, debug_info, status)
            
            elif specific_asset == "status_message":
                status_message = brand_assets.get("status_message", "No status")
                asset_value = status_message
                asset_type = "status_message"
                asset_info = f"Status: {status_message}"
                
                debug_info = ""
                if include_debug_info:
                    debug_info = f"Status message: {status_message}"
                
                status = "Success"
                return (asset_value, asset_type, asset_info, debug_info, status)
            
            else:
                return self._return_error(f"Unknown metadata asset: {specific_asset}")
                
        except Exception as e:
            return self._return_error(f"Error extracting metadata asset: {e}")

    def _count_logo_assets(self, brand_assets: Dict[str, Any]) -> int:
        """Count available logo assets."""
        logo_keys = [
            "logo_vertical_color", "logo_vertical_mono", "logo_horizontal_color",
            "logo_horizontal_mono", "logo_icon"
        ]
        return sum(1 for key in logo_keys if brand_assets.get(key) is not None)

    def _count_font_assets(self, brand_assets: Dict[str, Any]) -> int:
        """Count available font assets."""
        font_keys = [
            "font_primary", "font_primary_bold", "font_primary_italic",
            "font_secondary", "font_secondary_bold", "font_secondary_italic",
            "font_tertiary", "font_tertiary_bold", "font_tertiary_italic"
        ]
        return sum(1 for key in font_keys if brand_assets.get(key, ""))

    def _check_color_palette(self, brand_assets: Dict[str, Any]) -> bool:
        """Check if color palette is available and valid."""
        color_palette = brand_assets.get("color_palette", "")
        if color_palette:
            try:
                colors = json.loads(color_palette)
                return isinstance(colors, list) and len(colors) > 0
            except json.JSONDecodeError:
                return False
        return False

    def _generate_debug_info(self, brand_assets: Dict[str, Any]) -> str:
        """Generate comprehensive debug information."""
        debug_lines = []
        
        # Brand info
        brand_name = brand_assets.get("brand_name", "Unknown")
        status_message = brand_assets.get("status_message", "No status")
        debug_lines.append(f"Brand: {brand_name}")
        debug_lines.append(f"Status: {status_message}")
        
        # Logo assets
        logo_count = self._count_logo_assets(brand_assets)
        debug_lines.append(f"Logos: {logo_count}/5 available")
        
        # Font assets
        font_count = self._count_font_assets(brand_assets)
        debug_lines.append(f"Fonts: {font_count}/9 available")
        
        # Color palette
        color_available = self._check_color_palette(brand_assets)
        debug_lines.append(f"Colors: {'Available' if color_available else 'Missing'}")
        
        return " | ".join(debug_lines)

    def _return_error(self, error_message: str) -> Tuple:
        """Return error values."""
        return ("", "error", error_message, "", "Error")

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetReader": APZmediaBrandAssetReader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetReader": "APZmedia - Brand Asset Reader",
}
