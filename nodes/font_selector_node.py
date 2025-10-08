import os
import logging
import requests
import tempfile
import time
import re
import urllib.parse
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
                "font_selection": (["font_primary", "font_primary_bold", "font_primary_italic", "font_secondary", "font_secondary_bold", "font_secondary_italic", "font_tertiary", "font_tertiary_bold", "font_tertiary_italic"], {"default": "font_primary"}),
            },
            "optional": {
                "custom_font_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "use_custom": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("font_path", "font_name", "font_info", "font_list")
    
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
            Tuple of (font_path, font_name, font_info, font_list)
        """
        try:
            # Generate font list for output
            font_list = self._generate_font_list(brand_assets)
            
            # If using custom font path, validate and return it
            if use_custom and custom_font_path:
                if self._validate_font_path(custom_font_path):
                    font_name = self._extract_font_name(custom_font_path)
                    font_info = f"Custom font: {font_name}"
                    logger.info(f"Using custom font: {custom_font_path}")
                    return (custom_font_path, font_name, font_info, font_list)
                else:
                    logger.warning(f"Invalid custom font path: {custom_font_path}")
                    return self._return_default_font("Invalid custom font path", font_list)
            
            # Extract font path from brand assets
            font_path = self._get_font_from_assets(brand_assets, font_selection)
            
            if not font_path:
                logger.warning(f"No font found for {font_selection}")
                return self._return_default_font(f"No {font_selection} font available", font_list)
            
            # Check if it's a URL (including signed URLs) and download if needed
            if self._is_url(font_path):
                logger.info(f"Font is a URL, downloading: {font_path}")
                downloaded_path = self._download_font_from_url(font_path)
                if downloaded_path:
                    font_path = downloaded_path
                    logger.info(f"Downloaded font to: {font_path}")
                else:
                    logger.warning(f"Failed to download font from URL: {font_path}")
                    return self._return_default_font("Failed to download font from URL", font_list)
            
            # Validate the font path
            if not self._validate_font_path(font_path):
                logger.warning(f"Invalid font path: {font_path}")
                return self._return_default_font("Invalid font path", font_list)
            
            # Extract font name and create info
            font_name = self._extract_font_name(font_path)
            # Convert font_selection to readable format (e.g., font_primary_bold -> Primary Bold)
            readable_name = font_selection.replace("font_", "").replace("_", " ").title()
            font_info = f"{readable_name}: {font_name}"
            
            logger.info(f"Selected font: {font_path} ({font_name})")
            return (font_path, font_name, font_info, font_list)
            
        except Exception as e:
            logger.error(f"Error selecting font: {e}")
            return self._return_default_font(f"Error: {str(e)}", "")

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

    def _is_url(self, input_string: str) -> bool:
        """Check if input string is a URL (including signed URLs)."""
        if not input_string or not isinstance(input_string, str):
            return False
        
        # Check for common URL patterns including signed URLs
        url_patterns = [
            r'^https?://',  # Standard HTTP/HTTPS
            r'^ftp://',     # FTP
            r'^s3://',      # S3 URLs
            r'^gs://',      # Google Cloud Storage
            r'^azure://',   # Azure Blob Storage
            r'^blob:',      # Blob URLs
            r'^data:',      # Data URLs
        ]
        
        for pattern in url_patterns:
            if re.match(pattern, input_string, re.IGNORECASE):
                return True
        
        # Check for signed URLs (containing query parameters)
        if '?' in input_string:
            signed_url_params = [
                # Standard signed URL parameters
                'signature=', 'token=', 'expires=', 'access_key=',
                # AWS S3 signed URL parameters
                'x-amz-algorithm=', 'x-amz-credential=', 'x-amz-date=',
                'x-amz-expires=', 'x-amz-signedheaders=', 'x-amz-signature=',
                # Cloudflare R2 signed URL parameters (same as S3)
                'x-amz-algorithm=', 'x-amz-credential=', 'x-amz-date=',
                'x-amz-expires=', 'x-amz-signedheaders=', 'x-amz-signature=',
                # Google Cloud Storage signed URL parameters
                'googleaccessid=', 'expires=', 'signature=',
                # Azure Blob Storage signed URL parameters
                'sv=', 'sr=', 'sig=', 'st=', 'se=',
                # Generic signed URL patterns
                'auth=', 'key=', 'id=', 'secret='
            ]
            
            if any(param in input_string.lower() for param in signed_url_params):
                return True
        
        return False

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and security."""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check scheme (protocol)
            allowed_protocols = {'https', 'http'}
            if parsed.scheme not in allowed_protocols:
                logger.debug(f"Invalid protocol for URL: {url} (scheme: {parsed.scheme})")
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                'file://', 'ftp://', 'gopher://', 'data:', 'javascript:',
                'vbscript:', 'onload=', 'onerror=', 'eval(', 'document.cookie'
            ]
            
            url_lower = url.lower()
            for pattern in suspicious_patterns:
                if pattern in url_lower:
                    logger.debug(f"Suspicious pattern '{pattern}' found in URL: {url}")
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Error parsing or validating URL {url}: {e}")
            return False

    def _download_font_from_url(self, url: str) -> str:
        """Download font from URL and return local path."""
        if not url or not self._is_url(url) or not self._is_valid_url(url):
            logger.warning(f"Invalid font URL: {url}")
            return ""
        
        try:
            # Create temporary directory for downloads
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f'font-{timestamp}.ttf'  # Default to TTF, will be corrected if needed
            file_path = os.path.join(temp_dir, filename)
            
            logger.info(f"Downloading font from {url} to {file_path}")
            
            # Download the font file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'font/' not in content_type and 'application/' not in content_type:
                logger.warning(f"Unexpected content type for font: {content_type}")
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Downloaded font to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download font from {url}: {e}")
            return ""

    def _validate_font_path(self, font_path: str) -> bool:
        """
        Validate that the font path exists and is a valid font file.
        Handles both local file paths and URLs (including signed URLs).
        
        Args:
            font_path: Path to font file or URL
            
        Returns:
            True if valid, False otherwise
        """
        if not font_path or not isinstance(font_path, str):
            return False
        
        try:
            # Check if it's a URL (including signed URLs)
            if self._is_url(font_path):
                logger.info(f"Detected font URL, validating: {font_path}")
                # For URLs, we just validate the URL format and extension
                if not self._is_valid_url(font_path):
                    logger.debug(f"Invalid font URL format: {font_path}")
                    return False
                
                # Check if it appears to be a font file
                supported_extensions = ['.ttf', '.otf', '.woff', '.woff2']
                font_path_lower = font_path.lower()
                
                if not any(ext in font_path_lower for ext in supported_extensions):
                    logger.debug(f"URL does not appear to be a font file: {font_path}")
                    return False
                
                return True
            
            # For local file paths, check if file exists
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

    def _extract_font_name_from_url(self, url: str) -> str:
        """
        Extract font name from URL.
        
        Args:
            url: URL to font file
            
        Returns:
            Font name string
        """
        try:
            # Parse URL to get path
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            
            # Get filename from path
            filename = os.path.basename(path)
            
            # Remove query parameters if present
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Remove extension
            filename = Path(filename).stem
            
            # Clean up the name (remove common prefixes/suffixes)
            name = filename.replace('_', ' ').replace('-', ' ')
            
            # Capitalize words
            name = ' '.join(word.capitalize() for word in name.split())
            
            return name if name else "URL Font"
            
        except Exception as e:
            logger.error(f"Error extracting font name from URL {url}: {e}")
            return "URL Font"

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

    def _return_default_font(self, error_message: str, font_list: str = "") -> tuple:
        """
        Return default values when font selection fails.
        
        Args:
            error_message: Error message to include in font_info
            font_list: Font list string to return
            
        Returns:
            Tuple of (font_path, font_name, font_info, font_list)
        """
        return ("", "No Font", error_message, font_list)

    def _generate_font_list(self, brand_assets: Dict[str, Any]) -> str:
        """
        Generate a formatted list of available fonts from brand assets.
        
        Args:
            brand_assets: Dictionary containing brand assets
            
        Returns:
            Formatted string list of available fonts
        """
        try:
            font_list = []
            font_keys = [
                "font_primary", "font_primary_bold", "font_primary_italic",
                "font_secondary", "font_secondary_bold", "font_secondary_italic", 
                "font_tertiary", "font_tertiary_bold", "font_tertiary_italic"
            ]
            
            for key in font_keys:
                font_path = brand_assets.get(key, "")
                if font_path and self._validate_font_path(font_path):
                    # For URLs, extract name from URL, for local paths use file name
                    if self._is_url(font_path):
                        font_name = self._extract_font_name_from_url(font_path)
                    else:
                        font_name = self._extract_font_name(font_path)
                    readable_key = key.replace("font_", "").replace("_", " ").title()
                    font_list.append(f"• {readable_key}: {font_name}")
            
            if font_list:
                return "Available Fonts:\n" + "\n".join(font_list)
            else:
                return "No valid fonts found in brand assets"
                
        except Exception as e:
            logger.error(f"Error generating font list: {e}")
            return f"Error generating font list: {str(e)}"

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "APZmediaFontSelector": APZmediaFontSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaFontSelector": "APZmedia - Font Selector",
}
