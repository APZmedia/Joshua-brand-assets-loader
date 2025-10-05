import json
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaColorPaletteSelector:
    """
    Color Palette Selector Node for easy color selection from brand assets.
    
    This node takes brand assets as input and provides a simple interface
    to select and output specific colors from the color palette, replacing
    the need for separate get/set nodes for color management.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "palette_json": ("STRING", {}),
                "color_selection": ("STRING", {
                    "choices": [
                        "color_1",
                        "color_2", 
                        "color_3",
                        "color_4",
                        "color_5",
                        "color_6",
                        "color_7",
                        "first_color",
                        "second_color",
                        "third_color"
                    ],
                    "default": "color_1"
                }),
            },
            "optional": {
                "custom_color": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "use_custom": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("color_hex", "color_name", "color_info", "color_palette_json")
    
    FUNCTION = "select_color"
    CATEGORY = "apzmedia_brand"

    def select_color(self, brand_assets, color_selection, custom_color="", use_custom=False):
        """
        Select and return the appropriate color from brand assets.
        
        Args:
            brand_assets: Dictionary containing all brand assets
            color_selection: Selected color key (primary_color, secondary_color, etc.)
            custom_color: Custom color hex override
            use_custom: Whether to use custom color instead of brand assets
            
        Returns:
            Tuple of (color_hex, color_name, color_info, color_palette_json)
        """
        try:
            # If using custom color, validate and return it
            if use_custom and custom_color:
                if self._validate_color_hex(custom_color):
                    color_name = self._extract_color_name(custom_color)
                    color_info = f"Custom Color: {color_name}"
                    color_palette_json = self._get_color_palette_json(brand_assets)
                    logger.info(f"Using custom color: {custom_color}")
                    return (custom_color, color_name, color_info, color_palette_json)
                else:
                    logger.warning(f"Invalid custom color: {custom_color}")
                    return self._return_default_color("Invalid custom color")
            
            # Extract color from brand assets
            color_hex = self._get_color_from_assets(brand_assets, color_selection)
            
            if not color_hex:
                logger.warning(f"No color found for {color_selection}")
                return self._return_default_color(f"No {color_selection} color available")
            
            # Validate the color hex
            if not self._validate_color_hex(color_hex):
                logger.warning(f"Invalid color hex: {color_hex}")
                return self._return_default_color("Invalid color hex")
            
            # Extract color name and create info
            color_name = self._extract_color_name(color_hex)
            # Convert color_selection to readable format (e.g., primary_color -> Primary Color)
            readable_name = color_selection.replace("_", " ").title()
            color_info = f"{readable_name}: {color_name}"
            color_palette_json = self._get_color_palette_json(brand_assets)
            
            logger.info(f"Selected color: {color_hex} ({color_name})")
            return (color_hex, color_name, color_info, color_palette_json)
            
        except Exception as e:
            logger.error(f"Error selecting color: {e}")
            return self._return_default_color(f"Error: {str(e)}")

    def _get_color_from_assets(self, brand_assets: Dict[str, Any], color_selection: str) -> str:
        """
        Extract color from brand assets dictionary by parsing the color palette JSON.
        
        Args:
            brand_assets: Dictionary containing brand assets
            color_selection: Selected color type (primary, secondary, accent, etc.)
            
        Returns:
            Color hex string or empty string if not found
        """
        try:
            # Get color palette JSON from brand assets
            color_palette_json = brand_assets.get("color_palette", "[]")
            if not color_palette_json:
                logger.debug("No color palette found in brand assets")
                return ""
            
            try:
                colors = json.loads(color_palette_json)
                if not isinstance(colors, list) or len(colors) == 0:
                    logger.debug("Empty or invalid color palette")
                    return ""
                
                # Try to find color by matching name, id, or position
                for i, color in enumerate(colors):
                    if not isinstance(color, dict):
                        continue
                    
                    color_name = color.get("name", "").lower()
                    color_id = color.get("id", "").lower()
                    color_hex = color.get("hex", "")
                    
                    if not color_hex:
                        continue
                    
                    # Match by name patterns
                    if (color_selection in color_name or 
                        color_selection in color_id or
                        self._matches_color_type(color_name, color_id, color_selection)):
                        return color_hex
                
                # If no specific match found, return color by position
                if color_selection == "first_color" and len(colors) > 0:
                    return colors[0].get("hex", "")
                elif color_selection == "second_color" and len(colors) > 1:
                    return colors[1].get("hex", "")
                elif color_selection == "third_color" and len(colors) > 2:
                    return colors[2].get("hex", "")
                elif color_selection in ["primary", "secondary", "accent", "background", "text"]:
                    # Return first color as fallback for named selections
                    return colors[0].get("hex", "")
                
                logger.debug(f"No color found for selection: {color_selection}")
                return ""
                
            except json.JSONDecodeError:
                logger.warning("Invalid color palette JSON format")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting color from assets: {e}")
            return ""

    def _matches_color_type(self, color_name: str, color_id: str, color_selection: str) -> bool:
        """
        Check if a color matches the selected type based on name patterns.
        
        Args:
            color_name: Color name from palette
            color_id: Color ID from palette  
            color_selection: Selected color type
            
        Returns:
            True if color matches the selection type
        """
        # Common patterns for different color types
        patterns = {
            "primary": ["primary", "main", "brand", "logo"],
            "secondary": ["secondary", "second", "support"],
            "accent": ["accent", "highlight", "emphasis"],
            "background": ["background", "bg", "base"],
            "text": ["text", "foreground", "content"]
        }
        
        if color_selection not in patterns:
            return False
        
        # Check if any pattern matches the color name or id
        for pattern in patterns[color_selection]:
            if pattern in color_name or pattern in color_id:
                return True
        
        return False

    def _get_color_palette_json(self, brand_assets: Dict[str, Any]) -> str:
        """
        Get the full color palette JSON from brand assets.
        
        Args:
            brand_assets: Dictionary containing brand assets
            
        Returns:
            Color palette JSON string
        """
        try:
            color_palette = brand_assets.get("color_palette", "[]")
            if color_palette and isinstance(color_palette, str):
                # Validate JSON format
                try:
                    json.loads(color_palette)
                    return color_palette
                except json.JSONDecodeError:
                    return "[]"
            return "[]"
        except Exception as e:
            logger.error(f"Error getting color palette: {e}")
            return "[]"

    def _validate_color_hex(self, color_hex: str) -> bool:
        """
        Validate that the color hex is a valid hex color.
        
        Args:
            color_hex: Hex color string (e.g., "#FF0000" or "FF0000")
            
        Returns:
            True if valid, False otherwise
        """
        if not color_hex or not isinstance(color_hex, str):
            return False
        
        try:
            # Remove # if present
            hex_color = color_hex.lstrip('#')
            
            # Check if it's a valid hex color (3 or 6 characters)
            if len(hex_color) not in [3, 6]:
                return False
            
            # Check if all characters are valid hex digits
            if not all(c in '0123456789ABCDEFabcdef' for c in hex_color):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating color hex {color_hex}: {e}")
            return False

    def _extract_color_name(self, color_hex: str) -> str:
        """
        Extract color name from hex color.
        
        Args:
            color_hex: Hex color string
            
        Returns:
            Color name string
        """
        try:
            # Remove # if present
            hex_color = color_hex.lstrip('#').upper()
            
            # Basic color name mapping
            color_names = {
                "FF0000": "Red",
                "00FF00": "Green", 
                "0000FF": "Blue",
                "FFFF00": "Yellow",
                "FF00FF": "Magenta",
                "00FFFF": "Cyan",
                "000000": "Black",
                "FFFFFF": "White",
                "808080": "Gray",
                "800000": "Maroon",
                "008000": "Lime",
                "000080": "Navy",
                "800080": "Purple",
                "808000": "Olive",
                "008080": "Teal"
            }
            
            # Check for exact match
            if hex_color in color_names:
                return color_names[hex_color]
            
            # Check for close matches (simplified)
            if hex_color.startswith("FF"):
                return "Red-ish"
            elif hex_color.startswith("00") and hex_color.endswith("FF"):
                return "Blue-ish"
            elif hex_color.startswith("00FF"):
                return "Green-ish"
            elif hex_color.startswith("FFFF"):
                return "Yellow-ish"
            elif hex_color.startswith("FF00"):
                return "Magenta-ish"
            elif hex_color.startswith("00FF"):
                return "Cyan-ish"
            else:
                return f"Color #{hex_color}"
                
        except Exception as e:
            logger.error(f"Error extracting color name from {color_hex}: {e}")
            return "Unknown Color"

    def _return_default_color(self, error_message: str) -> Tuple:
        """
        Return default values when color selection fails.
        
        Args:
            error_message: Error message to include in color_info
            
        Returns:
            Tuple of (color_hex, color_name, color_info, color_palette_json)
        """
        return ("#000000", "No Color", error_message, "[]")

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaColorPaletteSelector": APZmediaColorPaletteSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaColorPaletteSelector": "APZmedia - Color Palette Selector",
}
