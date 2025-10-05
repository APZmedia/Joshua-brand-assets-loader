import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaFontSelector:
    """
    Font Selector Node for easy font switching from brand assets.
    
    This node takes brand assets as input and provides a simple interface
    to select and output the desired font path, replacing the need for
    separate get/set nodes for font management.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "brand_assets": ("BRAND_ASSETS", {}),
                "font_selection": ("STRING", {
                    "choices": [
                        "font_primary",
                        "font_primary_bold", 
                        "font_primary_italic",
                        "font_secondary",
                        "font_secondary_bold",
                        "font_secondary_italic",
                        "font_tertiary",
                        "font_tertiary_bold",
                        "font_tertiary_italic"
                    ],
                    "default": "font_primary"
                }),
            },
            "optional": {
                "custom_font_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "use_custom": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("font_path", "font_name", "font_info")
    
    FUNCTION = "select_font"
    CATEGORY = "apzmedia_brand"

    def select_font(self, brand_assets, font_selection, custom_font_path="", use_custom=False):
        """
        Select and return the appropriate font path from brand assets.
        
        Args:
            brand_assets: Dictionary containing all brand assets
            font_selection: Selected font key (font_primary, font_primary_bold, etc.)
            custom_font_path: Custom font path override
            use_custom: Whether to use custom font path instead of brand assets
            
        Returns:
            Tuple of (font_path, font_name, font_info)
        """
        try:
            # If using custom font path, validate and return it
            if use_custom and custom_font_path:
                if self._validate_font_path(custom_font_path):
                    font_name = self._extract_font_name(custom_font_path)
                    font_info = f"Custom font: {font_name}"
                    logger.info(f"Using custom font: {custom_font_path}")
                    return (custom_font_path, font_name, font_info)
                else:
                    logger.warning(f"Invalid custom font path: {custom_font_path}")
                    return self._return_default_font("Invalid custom font path")
            
            # Extract font path from brand assets
            font_path = self._get_font_from_assets(brand_assets, font_selection)
            
            if not font_path:
                logger.warning(f"No font found for {font_selection}")
                return self._return_default_font(f"No {font_selection} font available")
            
            # Validate the font path
            if not self._validate_font_path(font_path):
                logger.warning(f"Invalid font path: {font_path}")
                return self._return_default_font("Invalid font path")
            
            # Extract font name and create info
            font_name = self._extract_font_name(font_path)
            # Convert font_selection to readable format (e.g., font_primary_bold -> Primary Bold)
            readable_name = font_selection.replace("font_", "").replace("_", " ").title()
            font_info = f"{readable_name}: {font_name}"
            
            logger.info(f"Selected font: {font_path} ({font_name})")
            return (font_path, font_name, font_info)
            
        except Exception as e:
            logger.error(f"Error selecting font: {e}")
            return self._return_default_font(f"Error: {str(e)}")

    def _get_font_from_assets(self, brand_assets: Dict[str, Any], font_selection: str) -> str:
        """
        Extract font path from brand assets dictionary.
        
        Args:
            brand_assets: Dictionary containing brand assets
            font_selection: Selected font key (font_primary, font_primary_bold, etc.)
            
        Returns:
            Font path string or empty string if not found
        """
        try:
            # Get font path from assets using the direct font key
            font_path = brand_assets.get(font_selection, "")
            
            if font_path and isinstance(font_path, str):
                return font_path
            else:
                logger.debug(f"Font key '{font_selection}' not found or empty in brand assets")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting font from assets: {e}")
            return ""

    def _validate_font_path(self, font_path: str) -> bool:
        """
        Validate that the font path exists and is a valid font file.
        
        Args:
            font_path: Path to font file
            
        Returns:
            True if valid, False otherwise
        """
        if not font_path or not isinstance(font_path, str):
            return False
        
        try:
            # Check if file exists
            if not os.path.exists(font_path):
                logger.debug(f"Font file does not exist: {font_path}")
                return False
            
            # Check file extension
            supported_extensions = ['.ttf', '.otf', '.woff', '.woff2']
            font_path_lower = font_path.lower()
            
            if not any(font_path_lower.endswith(ext) for ext in supported_extensions):
                logger.debug(f"Unsupported font file extension: {font_path}")
                return False
            
            # Check file size (basic validation)
            file_size = os.path.getsize(font_path)
            if file_size == 0:
                logger.debug(f"Font file is empty: {font_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating font path {font_path}: {e}")
            return False

    def _extract_font_name(self, font_path: str) -> str:
        """
        Extract font name from file path.
        
        Args:
            font_path: Path to font file
            
        Returns:
            Font name string
        """
        try:
            # Get filename without extension
            filename = Path(font_path).stem
            
            # Clean up the name (remove common prefixes/suffixes)
            name = filename.replace('_', ' ').replace('-', ' ')
            
            # Capitalize words
            name = ' '.join(word.capitalize() for word in name.split())
            
            return name if name else "Unknown Font"
            
        except Exception as e:
            logger.error(f"Error extracting font name from {font_path}: {e}")
            return "Unknown Font"

    def _return_default_font(self, error_message: str) -> tuple:
        """
        Return default values when font selection fails.
        
        Args:
            error_message: Error message to include in font_info
            
        Returns:
            Tuple of (font_path, font_name, font_info)
        """
        return ("", "No Font", error_message)

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaFontSelector": APZmediaFontSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaFontSelector": "APZmedia - Font Selector",
}
