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
                "font_type": ("STRING", {
                    "choices": ["primary", "secondary", "tertiary"],
                    "default": "primary"
                }),
                "font_variant": ("STRING", {
                    "choices": ["regular", "bold", "italic"],
                    "default": "regular"
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

    def select_font(self, brand_assets, font_type, font_variant, custom_font_path="", use_custom=False):
        """
        Select and return the appropriate font path from brand assets.
        
        Args:
            brand_assets: Dictionary containing all brand assets
            font_type: Type of font (primary, secondary, tertiary)
            font_variant: Font variant (regular, bold, italic)
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
            font_path = self._get_font_from_assets(brand_assets, font_type, font_variant)
            
            if not font_path:
                logger.warning(f"No font found for {font_type}_{font_variant}")
                return self._return_default_font(f"No {font_type} {font_variant} font available")
            
            # Validate the font path
            if not self._validate_font_path(font_path):
                logger.warning(f"Invalid font path: {font_path}")
                return self._return_default_font("Invalid font path")
            
            # Extract font name and create info
            font_name = self._extract_font_name(font_path)
            font_info = f"{font_type.title()} {font_variant.title()}: {font_name}"
            
            logger.info(f"Selected font: {font_path} ({font_name})")
            return (font_path, font_name, font_info)
            
        except Exception as e:
            logger.error(f"Error selecting font: {e}")
            return self._return_default_font(f"Error: {str(e)}")

    def _get_font_from_assets(self, brand_assets: Dict[str, Any], font_type: str, font_variant: str) -> str:
        """
        Extract font path from brand assets dictionary.
        
        Args:
            brand_assets: Dictionary containing brand assets
            font_type: Type of font (primary, secondary, tertiary)
            font_variant: Font variant (regular, bold, italic)
            
        Returns:
            Font path string or empty string if not found
        """
        try:
            # Handle different font variants
            if font_variant == "regular":
                font_key = f"font_{font_type}"
            elif font_variant == "bold":
                font_key = f"font_{font_type}_bold"
            elif font_variant == "italic":
                font_key = f"font_{font_type}_italic"
            else:
                logger.warning(f"Unknown font variant: {font_variant}")
                return ""
            
            # Get font path from assets
            font_path = brand_assets.get(font_key, "")
            
            if font_path and isinstance(font_path, str):
                return font_path
            else:
                logger.debug(f"Font key '{font_key}' not found or empty in brand assets")
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
