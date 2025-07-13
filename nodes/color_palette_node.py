import logging
import re
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaColorPalette:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "color_1": ("STRING", {"default": "#FF0000", "multiline": False}),
                "color_2": ("STRING", {"default": "#00FF00", "multiline": False}),
                "color_3": ("STRING", {"default": "#0000FF", "multiline": False}),
                "color_4": ("STRING", {"default": "#FFFF00", "multiline": False}),
                "color_5": ("STRING", {"default": "#FF00FF", "multiline": False}),
                "color_6": ("STRING", {"default": "#00FFFF", "multiline": False}),
                "color_7": ("STRING", {"default": "#000000", "multiline": False}),
            },
            "optional": {
                "palette_name": ("STRING", {"default": "Brand Palette", "multiline": False}),
                "validate_colors": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (
        "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING",  # Individual colors
        "STRING",  # Combined palette JSON
        "STRING",  # Palette name
        "STRING",  # Status message
    )
    RETURN_NAMES = (
        "color_1", "color_2", "color_3", "color_4", "color_5", "color_6", "color_7",
        "palette_json", "palette_name", "status_message"
    )

    FUNCTION = "create_color_palette"
    CATEGORY = "apzmedia_brand"

    def create_color_palette(self, color_1, color_2, color_3, color_4, color_5, color_6, color_7,
                           palette_name="Brand Palette", validate_colors=True):
        """
        Create a color palette from seven hex color inputs.
        
        Args:
            color_1-7: Hex color strings (e.g., "#FF0000", "FF0000")
            palette_name: Name for the color palette
            validate_colors: Whether to validate hex color format
            
        Returns:
            Tuple of individual color strings, combined JSON, palette name, and status
        """
        try:
            colors = [color_1, color_2, color_3, color_4, color_5, color_6, color_7]
            validated_colors = []
            invalid_colors = []
            
            # Validate colors if requested
            if validate_colors:
                for i, color in enumerate(colors, 1):
                    if self._is_valid_hex_color(color):
                        validated_colors.append(color)
                    else:
                        invalid_colors.append(f"Color {i}: {color}")
                        # Use a default color for invalid ones
                        validated_colors.append("#000000")
            else:
                validated_colors = colors
            
            # Create status message
            if invalid_colors:
                status_message = f"Warning: Invalid colors found - {', '.join(invalid_colors)}"
                logger.warning(status_message)
            else:
                status_message = "All colors validated successfully"
                logger.info(status_message)
            
            # Create palette JSON
            palette_json = self._create_palette_json(validated_colors, palette_name)
            
            logger.info(f"Created color palette '{palette_name}' with {len(validated_colors)} colors")
            
            # Return individual colors, JSON, name, and status
            return (
                validated_colors[0], validated_colors[1], validated_colors[2], 
                validated_colors[3], validated_colors[4], validated_colors[5], validated_colors[6],
                palette_json, palette_name, status_message
            )
            
        except Exception as e:
            logger.error(f"Failed to create color palette: {str(e)}")
            # Return default values on error
            default_colors = ["#000000"] * 7
            return (
                *default_colors,
                self._create_palette_json(default_colors, "Error Palette"),
                "Error Palette",
                f"Error: {str(e)}"
            )

    def _is_valid_hex_color(self, hex_color: str) -> bool:
        """
        Validate hex color format.
        
        Args:
            hex_color: Hex color string to validate
            
        Returns:
            True if valid hex color format, False otherwise
        """
        try:
            if not hex_color or not isinstance(hex_color, str):
                return False
            
            # Remove # if present
            hex_color = hex_color.strip().upper()
            if hex_color.startswith('#'):
                hex_color = hex_color[1:]
            
            # Check format: 6 hex digits (RGB) or 8 hex digits (RGBA)
            if not re.match(r'^[0-9A-F]{6}([0-9A-F]{2})?$', hex_color):
                return False
            
            # Extract RGB values and validate range
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
            
        except Exception as e:
            logger.debug(f"Hex color validation failed for '{hex_color}': {str(e)}")
            return False

    def _create_palette_json(self, colors: list, palette_name: str) -> str:
        """
        Create JSON representation of the color palette.
        
        Args:
            colors: List of hex color strings
            palette_name: Name of the palette
            
        Returns:
            JSON string representation of the palette
        """
        try:
            import json
            
            palette_data = {
                "name": palette_name,
                "colors": []
            }
            
            color_names = [
                "Primary", "Secondary", "Accent", "Highlight", 
                "Neutral", "Background", "Text"
            ]
            
            for i, color in enumerate(colors):
                color_info = {
                    "name": color_names[i] if i < len(color_names) else f"Color {i+1}",
                    "hex": color,
                    "id": f"color-{i+1}"
                }
                palette_data["colors"].append(color_info)
            
            return json.dumps(palette_data, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to create palette JSON: {str(e)}")
            return '{"error": "Failed to create palette JSON"}'

    def _parse_hex_color(self, hex_color: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse hex color string and return RGB values.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000", "FF0000")
            
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

    def get_color_info(self, hex_color: str) -> dict:
        """
        Get detailed information about a hex color.
        
        Args:
            hex_color: Hex color string
            
        Returns:
            Dictionary with color information (RGB, HSL, etc.)
        """
        try:
            rgb_values = self._parse_hex_color(hex_color)
            if rgb_values is None:
                return {"error": "Invalid hex color"}
            
            r, g, b = rgb_values
            
            # Convert to HSL (simplified calculation)
            r_norm = r / 255.0
            g_norm = g / 255.0
            b_norm = b / 255.0
            
            max_val = max(r_norm, g_norm, b_norm)
            min_val = min(r_norm, g_norm, b_norm)
            delta = max_val - min_val
            
            # Calculate lightness
            l = (max_val + min_val) / 2
            
            # Calculate saturation
            if delta == 0:
                s = 0
            else:
                s = delta / (1 - abs(2 * l - 1))
            
            # Calculate hue
            if delta == 0:
                h = 0
            elif max_val == r_norm:
                h = 60 * (((g_norm - b_norm) / delta) % 6)
            elif max_val == g_norm:
                h = 60 * ((b_norm - r_norm) / delta + 2)
            else:  # max_val == b_norm
                h = 60 * ((r_norm - g_norm) / delta + 4)
            
            return {
                "hex": hex_color,
                "rgb": {"r": r, "g": g, "b": b},
                "hsl": {"h": round(h, 1), "s": round(s * 100, 1), "l": round(l * 100, 1)},
                "is_dark": l < 0.5,
                "is_bright": max_val > 0.8
            }
            
        except Exception as e:
            logger.error(f"Failed to get color info for '{hex_color}': {str(e)}")
            return {"error": f"Failed to analyze color: {str(e)}"}

# Node class mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaColorPalette": APZmediaColorPalette
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaColorPalette": "APZmedia Color Palette"
} 