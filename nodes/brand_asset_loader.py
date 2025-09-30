import os
import torch
import requests
import json
import re
import urllib.parse
import subprocess
import time
import tempfile
from PIL import Image
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
# Assuming global_brand_state is available in the same relative path
# from .global_brand_state import global_brand_state 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Placeholder for global_brand_state if not externally defined, for demonstration
# In a real ComfyUI custom node setup, you would typically define global_brand_state
# in its own file and import it correctly.
class GlobalBrandState:
    def __init__(self):
        self._brand_assets = {}

    def set_brand_assets(self, assets: Dict):
        self._brand_assets = assets
        logger.info("Brand assets stored in global state.")

    def get_brand_assets(self) -> Dict:
        return self._brand_assets

global_brand_state = GlobalBrandState()

class APZmediaBrandAssetLoader:
    # Security constants
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    MAX_IMAGE_DIMENSION = 4096  # 4K max dimension
    ALLOWED_DOMAINS = set()  # Empty set means no domain restrictions
    ALLOWED_PROTOCOLS = {'https', 'http'}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "load_method": (["manual", "api"], {"default": "manual"}),
            },
            "optional": {
                # API Configuration
                "api_brand_id": ("STRING", {"default": "", "multiline": False}),
                "api_base_url": ("STRING", {"default": "https://api.example.com", "multiline": False}),
                "api_token": ("STRING", {"default": "", "multiline": False}),
                
                # Logo Assets
                "logo_vertical_color": ("STRING", {"default": "", "multiline": False}),
                "logo_vertical_mono": ("STRING", {"default": "", "multiline": False}),
                "logo_horizontal_color": ("STRING", {"default": "", "multiline": False}),
                "logo_horizontal_mono": ("STRING", {"default": "", "multiline": False}),
                "logo_icon": ("STRING", {"default": "", "multiline": False}),
                
                # Font Assets
                "font_primary": ("STRING", {"default": "", "multiline": False}),
                "font_primary_bold": ("STRING", {"default": "", "multiline": False}),
                "font_primary_italic": ("STRING", {"default": "", "multiline": False}),
                "font_secondary": ("STRING", {"default": "", "multiline": False}),
                "font_secondary_bold": ("STRING", {"default": "", "multiline": False}),
                "font_secondary_italic": ("STRING", {"default": "", "multiline": False}),
                "font_tertiary": ("STRING", {"default": "", "multiline": False}),
                "font_tertiary_bold": ("STRING", {"default": "", "multiline": False}),
                "font_tertiary_italic": ("STRING", {"default": "", "multiline": False}),
                
                # Color Palette
                "color_palette": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = (
        "BRAND_ASSETS",
        "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK",
        "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING",
        "STRING",
        "STRING",
        "STRING"
    )
    RETURN_NAMES = (
        "brand_assets",
        "logo_vertical_color", "logo_vertical_color_mask", "logo_vertical_mono", "logo_vertical_mono_mask", 
        "logo_horizontal_color", "logo_horizontal_color_mask", "logo_horizontal_mono", "logo_horizontal_mono_mask", 
        "logo_icon", "logo_icon_mask",
        "font_primary", "font_primary_bold", "font_primary_italic", "font_secondary", "font_secondary_bold", "font_secondary_italic", 
        "font_tertiary", "font_tertiary_bold", "font_tertiary_italic",
        "color_palette", "brand_name", "status_message"
    )

    FUNCTION = "load_brand_assets"
    CATEGORY = "apzmedia_brand"

    def load_brand_assets(self, load_method, api_brand_id="", api_base_url="", api_token="", 
                         logo_vertical_color="", logo_vertical_mono="", 
                         logo_horizontal_color="", logo_horizontal_mono="", 
                         logo_icon="", font_primary="", font_primary_bold="", font_primary_italic="",
                         font_secondary="", font_secondary_bold="", font_secondary_italic="",
                         font_tertiary="", font_tertiary_bold="", font_tertiary_italic="", color_palette="",
                         use_aria2c=True, download_timeout=30):
        """
        Load all brand assets either manually or via API.
        
        Args:
            load_method: "manual" or "api"
            brand_id: Brand ID for API loading
            api_base_url: Base URL for the brand API
            api_token: API authentication token
            logo_*_path: Manual file paths for logos
            *_font_path: Manual file paths for fonts
            color_palette_json: Manual color palette JSON string
            
        Returns:
            Tuple of all brand assets and metadata
        """
        try:
            if load_method == "api":
                return self._load_from_api(api_brand_id, api_base_url, api_token, use_aria2c, download_timeout)
            else:
                return self._load_manual(
                    logo_vertical_color, logo_vertical_mono,
                    logo_horizontal_color, logo_horizontal_mono,
                    logo_icon, font_primary, font_primary_bold, font_primary_italic,
                    font_secondary, font_secondary_bold, font_secondary_italic,
                    font_tertiary, font_tertiary_bold, font_tertiary_italic, color_palette,
                    use_aria2c, download_timeout
                )
        except Exception as e:
            logger.error(f"Failed to load brand assets: {e}")
            return self._return_defaults("Error: Asset loading failed")

    def _load_from_api(self, brand_id: str, api_base_url: str, api_token: str, use_aria2c: bool = True, download_timeout: int = 30) -> Tuple:
        """Load brand assets from API."""
        try:
            if not brand_id or not api_base_url:
                return self._return_defaults("Error: Brand ID and API URL required for API loading")

            # Validate API URL
            if not self._is_valid_url(api_base_url):
                return self._return_defaults("Error: Invalid API URL format")

            # Sanitize brand_id to prevent injection
            if not self._is_valid_brand_id(brand_id):
                return self._return_defaults("Error: Invalid brand ID format")

            # Construct API URL
            api_url = f"{api_base_url.rstrip('/')}/api/brands/{brand_id}?depth=2"
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
            }
            
            # Add authorization header only if token is provided
            if api_token and api_token.strip():
                headers["Authorization"] = f"Bearer {api_token}"
                logger.info(f"Fetching brand assets from API for brand ID: {brand_id[:8]}... (with authentication)")
            else:
                logger.info(f"Fetching brand assets from API for brand ID: {brand_id[:8]}... (public access)")

            # Make API request
            response = requests.get(api_url, headers=headers, timeout=30)
            
            if response.status_code == 401:
                return self._return_defaults("API Error: Authentication required - please provide a valid API token")
            elif response.status_code == 403:
                return self._return_defaults("API Error: Access denied - check your API token and permissions")
            elif response.status_code == 404:
                return self._return_defaults("API Error: Brand not found - check the brand ID")
            elif response.status_code != 200:
                return self._return_defaults(f"API Error: HTTP {response.status_code}")

            brand_data = response.json()
            brand_name = brand_data.get("name", "Unknown Brand")
            
            # Load logos with URL validation and download support
            logos = brand_data.get("logos", {})
            logo_vertical_color, logo_vertical_color_mask = self._load_logo_from_url(logos.get("verticalColor", {}).get("url", ""), use_aria2c, download_timeout)
            logo_vertical_mono, logo_vertical_mono_mask = self._load_logo_from_url(logos.get("verticalMonocolor", {}).get("url", ""), use_aria2c, download_timeout)
            logo_horizontal_color, logo_horizontal_color_mask = self._load_logo_from_url(logos.get("horizontalColor", {}).get("url", ""), use_aria2c, download_timeout)
            logo_horizontal_mono, logo_horizontal_mono_mask = self._load_logo_from_url(logos.get("horizontalMonocolor", {}).get("url", ""), use_aria2c, download_timeout)
            logo_icon, logo_icon_mask = self._load_logo_from_url(logos.get("icon", {}).get("url", ""), use_aria2c, download_timeout)

            # Load fonts with URL validation
            fonts = brand_data.get("fonts", {})
            
            # Primary font variants
            primary_font_path = self._process_font_url(fonts.get("primary", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not primary_font_path:
                static_files = fonts.get("primary", {}).get("staticFontFiles", [])
                if static_files:
                    primary_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            primary_bold_font_path = self._process_font_url(fonts.get("primaryBold", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not primary_bold_font_path:
                static_files = fonts.get("primaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    primary_bold_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            primary_italic_font_path = self._process_font_url(fonts.get("primaryItalic", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not primary_italic_font_path:
                static_files = fonts.get("primaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    primary_italic_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            # Secondary font variants
            secondary_font_path = self._process_font_url(fonts.get("secondary", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not secondary_font_path:
                static_files = fonts.get("secondary", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            secondary_bold_font_path = self._process_font_url(fonts.get("secondaryBold", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not secondary_bold_font_path:
                static_files = fonts.get("secondaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_bold_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            secondary_italic_font_path = self._process_font_url(fonts.get("secondaryItalic", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not secondary_italic_font_path:
                static_files = fonts.get("secondaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_italic_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            # Tertiary font variants
            tertiary_font_path = self._process_font_url(fonts.get("tertiary", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not tertiary_font_path:
                static_files = fonts.get("tertiary", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            tertiary_bold_font_path = self._process_font_url(fonts.get("tertiaryBold", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not tertiary_bold_font_path:
                static_files = fonts.get("tertiaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_bold_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)
            
            tertiary_italic_font_path = self._process_font_url(fonts.get("tertiaryItalic", {}).get("variableFontFile", {}).get("url", ""), use_aria2c, download_timeout)
            if not tertiary_italic_font_path:
                static_files = fonts.get("tertiaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_italic_font_path = self._process_font_url(static_files[0].get("fontFile", {}).get("url", ""), use_aria2c, download_timeout)

            # Load color palette
            color_palette = brand_data.get("colorPalette", [])
            if not color_palette:
                color_palette_json = self._get_default_color_palette()
            else:
                color_palette_json = json.dumps(color_palette, indent=2)

            status_message = f"Successfully loaded {brand_name} assets from API"
            
            # Store assets in global state
            assets_dict = {
                "logo_vertical_color": logo_vertical_color,
                "logo_vertical_color_mask": logo_vertical_color_mask,
                "logo_vertical_mono": logo_vertical_mono,
                "logo_vertical_mono_mask": logo_vertical_mono_mask,
                "logo_horizontal_color": logo_horizontal_color,
                "logo_horizontal_color_mask": logo_horizontal_color_mask,
                "logo_horizontal_mono": logo_horizontal_mono,
                "logo_horizontal_mono_mask": logo_horizontal_mono_mask,
                "logo_icon": logo_icon,
                "logo_icon_mask": logo_icon_mask,
                "font_primary": primary_font_path,
                "font_primary_bold": primary_bold_font_path,
                "font_primary_italic": primary_italic_font_path,
                "font_secondary": secondary_font_path,
                "font_secondary_bold": secondary_bold_font_path,
                "font_secondary_italic": secondary_italic_font_path,
                "font_tertiary": tertiary_font_path,
                "font_tertiary_bold": tertiary_bold_font_path,
                "font_tertiary_italic": tertiary_italic_font_path,
                "color_palette": color_palette_json,
                "brand_name": brand_name,
                "status_message": status_message
            }
            global_brand_state.set_brand_assets(assets_dict)
            
            return (
                assets_dict,
                logo_vertical_color, logo_vertical_color_mask, logo_vertical_mono, logo_vertical_mono_mask,
                logo_horizontal_color, logo_horizontal_color_mask, logo_horizontal_mono, logo_horizontal_mono_mask,
                logo_icon, logo_icon_mask, primary_font_path, primary_bold_font_path, primary_italic_font_path,
                secondary_font_path, secondary_bold_font_path, secondary_italic_font_path,
                tertiary_font_path, tertiary_bold_font_path, tertiary_italic_font_path,
                color_palette_json, brand_name, status_message
            )

        except requests.RequestException as e:
            logger.error(f"Network Error during API loading: {e}")
            return self._return_defaults("Network Error: Unable to connect to API")
        except json.JSONDecodeError as e:
            logger.error(f"API Error: Invalid response format: {e}")
            return self._return_defaults("API Error: Invalid response format")
        except Exception as e:
            logger.error(f"API Loading Error: Unexpected error occurred: {e}")
            return self._return_defaults("API Loading Error: Unexpected error occurred")

    def _load_manual(self, logo_vertical_color, logo_vertical_mono, 
                    logo_horizontal_color, logo_horizontal_mono, 
                    logo_icon, font_primary, font_primary_bold, font_primary_italic,
                    font_secondary, font_secondary_bold, font_secondary_italic,
                    font_tertiary, font_tertiary_bold, font_tertiary_italic, color_palette,
                    use_aria2c=True, download_timeout=30) -> Tuple:
        """Load brand assets from manual file paths."""
        try:
            # Load logos from file paths with path validation
            logo_vertical_color_img, logo_vertical_color_mask = self._load_logo_from_path(logo_vertical_color, use_aria2c, download_timeout)
            logo_vertical_mono_img, logo_vertical_mono_mask = self._load_logo_from_path(logo_vertical_mono, use_aria2c, download_timeout)
            logo_horizontal_color_img, logo_horizontal_color_mask = self._load_logo_from_path(logo_horizontal_color, use_aria2c, download_timeout)
            logo_horizontal_mono_img, logo_horizontal_mono_mask = self._load_logo_from_path(logo_horizontal_mono, use_aria2c, download_timeout)
            logo_icon_img, logo_icon_mask = self._load_logo_from_path(logo_icon, use_aria2c, download_timeout)

            # Validate and download font paths if they are URLs
            primary_font_path = self._process_font_input(font_primary, use_aria2c, download_timeout)
            primary_bold_font_path = self._process_font_input(font_primary_bold, use_aria2c, download_timeout)
            primary_italic_font_path = self._process_font_input(font_primary_italic, use_aria2c, download_timeout)
            secondary_font_path = self._process_font_input(font_secondary, use_aria2c, download_timeout)
            secondary_bold_font_path = self._process_font_input(font_secondary_bold, use_aria2c, download_timeout)
            secondary_italic_font_path = self._process_font_input(font_secondary_italic, use_aria2c, download_timeout)
            tertiary_font_path = self._process_font_input(font_tertiary, use_aria2c, download_timeout)
            tertiary_bold_font_path = self._process_font_input(font_tertiary_bold, use_aria2c, download_timeout)
            tertiary_italic_font_path = self._process_font_input(font_tertiary_italic, use_aria2c, download_timeout)

            # Validate color palette JSON
            if color_palette:
                try:
                    parsed = json.loads(color_palette)
                    # Validate color palette structure
                    if isinstance(parsed, list):
                        for color in parsed:
                            if not isinstance(color, dict) or 'hex' not in color:
                                color_palette = self._get_default_color_palette()
                                break
                    else:
                        color_palette = self._get_default_color_palette()
                except json.JSONDecodeError:
                    color_palette = self._get_default_color_palette()
            else:
                color_palette = self._get_default_color_palette()

            brand_name = "Manual Brand Assets"
            status_message = "Successfully loaded manual brand assets"
            
            # Store assets in global state
            assets_dict = {
                "logo_vertical_color": logo_vertical_color_img,
                "logo_vertical_color_mask": logo_vertical_color_mask,
                "logo_vertical_mono": logo_vertical_mono_img,
                "logo_vertical_mono_mask": logo_vertical_mono_mask,
                "logo_horizontal_color": logo_horizontal_color_img,
                "logo_horizontal_color_mask": logo_horizontal_color_mask,
                "logo_horizontal_mono": logo_horizontal_mono_img,
                "logo_horizontal_mono_mask": logo_horizontal_mono_mask,
                "logo_icon": logo_icon_img,
                "logo_icon_mask": logo_icon_mask,
                "font_primary": primary_font_path,
                "font_primary_bold": primary_bold_font_path,
                "font_primary_italic": primary_italic_font_path,
                "font_secondary": secondary_font_path,
                "font_secondary_bold": secondary_bold_font_path,
                "font_secondary_italic": secondary_italic_font_path,
                "font_tertiary": tertiary_font_path,
                "font_tertiary_bold": tertiary_bold_font_path,
                "font_tertiary_italic": tertiary_italic_font_path,
                "color_palette": color_palette,
                "brand_name": brand_name,
                "status_message": status_message
            }
            global_brand_state.set_brand_assets(assets_dict)
            
            return (
                assets_dict,
                logo_vertical_color_img, logo_vertical_color_mask, logo_vertical_mono_img, logo_vertical_mono_mask,
                logo_horizontal_color_img, logo_horizontal_color_mask, logo_horizontal_mono_img, logo_horizontal_mono_mask,
                logo_icon_img, logo_icon_mask, primary_font_path, primary_bold_font_path, primary_italic_font_path,
                secondary_font_path, secondary_bold_font_path, secondary_italic_font_path,
                tertiary_font_path, tertiary_bold_font_path, tertiary_italic_font_path,
                color_palette, brand_name, status_message
            )
        except Exception:
            return self._return_defaults("Manual Loading Error: Failed to load assets")

    def _load_logo_from_url(self, url: str, use_aria2c: bool = True, download_timeout: int = 30) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load logo from URL with security validation. Returns (rgb_image, alpha_mask)."""
        if not url:
            return self._create_empty_logo(), self._create_empty_mask()
        
        # Validate URL
        if not self._is_valid_url(url):
            logger.warning(f"Invalid logo URL format: {url}")
            return self._create_empty_logo(), self._create_empty_mask()
        
        try:
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code != 200:
                logger.warning(f"Failed to download logo from {url}: HTTP {response.status_code}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp']):
                logger.warning(f"Invalid content type for logo from {url}: {content_type}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                logger.warning(f"Logo file from {url} too large: {content_length} bytes")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Read content with size limit
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.MAX_FILE_SIZE:
                    logger.warning(f"Logo file from {url} exceeds size limit during download")
                    return self._create_empty_logo(), self._create_empty_mask()
            
            # Create temporary file-like object
            from io import BytesIO
            image_data = BytesIO(content)
            image = Image.open(image_data)
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                logger.warning(f"Logo image from {url} too large: {image.width}x{image.height}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            return self._process_logo_image(image)
            
        except Exception as e:
            logger.error(f"Failed to load logo from URL {url}: {e}")
            return self._create_empty_logo(), self._create_empty_mask()

    def _load_logo_from_path(self, file_path: str, use_aria2c: bool = True, download_timeout: int = 30) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load logo from file path or URL with automatic download. Returns (rgb_image, alpha_mask)."""
        logger.info(f"[BrandAssetLoader] Trying to load logo from: {file_path}")
        if not file_path:
            logger.info("[BrandAssetLoader] No file path provided.")
            return self._create_empty_logo(), self._create_empty_mask()
        
        # Check if input is a URL (including signed URLs)
        if self._is_url(file_path):
            logger.info(f"[BrandAssetLoader] Detected URL, downloading: {file_path}")
            downloaded_path = self._download_file_from_url(file_path, file_type="auto", use_aria2c=use_aria2c, download_timeout=download_timeout)
            if not downloaded_path:
                logger.warning(f"[BrandAssetLoader] Failed to download from URL: {file_path}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            logger.info(f"[BrandAssetLoader] Downloaded to: {downloaded_path}")
            file_path = downloaded_path
        
        # Validate and sanitize file path
        if not self._is_safe_file_path(file_path):
            logger.warning(f"[BrandAssetLoader] Unsafe file path detected: {file_path}")
            return self._create_empty_logo(), self._create_empty_mask()
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"[BrandAssetLoader] File does not exist: {file_path}")
                return self._create_empty_logo(), self._create_empty_mask()
            logger.info(f"[BrandAssetLoader] File exists: {file_path}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            logger.info(f"[BrandAssetLoader] File size: {file_size} bytes")
            if file_size > self.MAX_FILE_SIZE:
                logger.warning(f"[BrandAssetLoader] Logo file too large: {file_size} bytes")
                return self._create_empty_logo(), self._create_empty_mask()
            
            if not self._is_valid_image_file(file_path):
                logger.warning(f"[BrandAssetLoader] Invalid image file format: {file_path}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            image = Image.open(file_path)
            logger.info(f"[BrandAssetLoader] Loaded image: size={image.size}, mode={image.mode}")
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                logger.warning(f"[BrandAssetLoader] Logo image too large: {image.width}x{image.height}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            rgb_tensor, alpha_tensor = self._process_logo_image(image)
            logger.info(f"[BrandAssetLoader] RGB tensor shape: {rgb_tensor.shape}, min/max: {rgb_tensor.min().item()}/{rgb_tensor.max().item()}")
            logger.info(f"[BrandAssetLoader] Alpha tensor shape: {alpha_tensor.shape}, min/max: {alpha_tensor.min().item()}/{alpha_tensor.max().item()}")
            return rgb_tensor, alpha_tensor
            
        except Exception as e:
            logger.error(f"[BrandAssetLoader] Exception loading logo from {file_path}: {e}")
            return self._create_empty_logo(), self._create_empty_mask()

    def _validate_font_url(self, url: str) -> str:
        """Validate font URL and return safe URL or empty string."""
        if not url:
            return ""
        
        if not self._is_valid_url(url):
            logger.warning(f"Invalid font URL format: {url}")
            return ""
        
        # Check if it's a font file (simple extension check for now)
        if not any(ext in url.lower() for ext in ['.ttf', '.otf', '.woff', '.woff2']):
            logger.warning(f"URL does not seem to be a font file: {url}")
            return ""
        
        return url

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
            if parsed.scheme not in self.ALLOWED_PROTOCOLS:
                logger.debug(f"Invalid protocol for URL: {url} (scheme: {parsed.scheme})")
                return False
            
            # Check for domain restrictions if ALLOWED_DOMAINS is not empty
            if self.ALLOWED_DOMAINS and parsed.netloc and parsed.netloc not in self.ALLOWED_DOMAINS:
                logger.debug(f"Domain not allowed for URL: {url} (netloc: {parsed.netloc})")
                return False
            
            # Check for suspicious patterns in the whole URL string
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

    def _download_file_from_url(self, url: str, file_type: str = "auto", use_aria2c: bool = True, download_timeout: int = 30) -> str:
        """
        Download file from URL to a temporary location.
        
        Args:
            url: URL to download from (supports signed URLs)
            file_type: File extension or "auto" to detect from URL
            use_aria2c: Whether to use aria2c for faster downloads
            
        Returns:
            Path to downloaded file or empty string if failed
        """
        if not url or not self._is_url(url):
            logger.warning(f"Invalid URL provided for download: {url}")
            return ""
        
        try:
            # Create temporary directory for downloads
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Determine file extension
            if file_type == "auto":
                file_type = self._get_file_extension_from_url(url) or "tmp"
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f'download-{timestamp}.{file_type}'
            file_path = os.path.join(temp_dir, filename)
            
            logger.info(f"Downloading file from {url} to {file_path}")
            
            if use_aria2c and self._is_aria2c_available():
                # Use aria2c for faster downloads
                return self._download_with_aria2c(url, file_path, temp_dir)
            else:
                # Fallback to requests
                return self._download_with_requests(url, file_path, download_timeout)
                
        except Exception as e:
            logger.error(f"Failed to download file from {url}: {e}")
            return ""

    def _get_file_extension_from_url(self, url: str) -> str:
        """Extract file extension from URL."""
        try:
            parsed_url = urllib.parse.urlparse(url)
            path = parsed_url.path
            filename = os.path.basename(path)
            
            # Remove query parameters if present
            if '?' in filename:
                filename = filename.split('?')[0]
            
            match = re.search(r'\.([a-zA-Z0-9]+)$', filename)
            if match:
                return match.group(1).lower()
        except Exception as e:
            logger.debug(f"Error extracting file extension from URL {url}: {e}")
        
        return ""

    def _is_aria2c_available(self) -> bool:
        """Check if aria2c is available on the system."""
        try:
            subprocess.run(["aria2c", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _download_with_aria2c(self, url: str, file_path: str, temp_dir: str) -> str:
        """Download file using aria2c for better performance."""
        try:
            filename = os.path.basename(file_path)
            cmd = [
                "aria2c", 
                "-o", filename,
                "-x", "16",  # 16 connections
                "-s", "16",  # 16 splits
                url, 
                "-d", temp_dir
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"aria2c download completed: {result.stdout}")
            
            # Verify file was downloaded
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"Downloaded file size: {file_size} bytes")
                return file_path
            else:
                logger.error("File not found after aria2c download")
                return ""
                
        except subprocess.CalledProcessError as e:
            logger.error(f"aria2c download failed: {e.stderr}")
            return ""

    def _download_with_requests(self, url: str, file_path: str, timeout: int = 30) -> str:
        """Download file using requests as fallback."""
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                logger.warning(f"File too large: {content_length} bytes")
                return ""
            
            # Download file
            with open(file_path, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_size += len(chunk)
                        if downloaded_size > self.MAX_FILE_SIZE:
                            logger.warning("File exceeds size limit during download")
                            f.close()
                            os.remove(file_path)
                            return ""
                        f.write(chunk)
            
            logger.info(f"Downloaded file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Requests download failed: {e}")
            return ""

    def _is_valid_brand_id(self, brand_id: str) -> bool:
        """Validate brand ID format."""
        if not brand_id:
            return False
        
        # Only allow alphanumeric characters, hyphens, and underscores
        if not bool(re.match(r'^[a-zA-Z0-9_-]+$', brand_id)):
            logger.warning(f"Invalid brand ID format: {brand_id}")
            return False
        return True

    def _is_safe_file_path(self, file_path: str) -> bool:
        """Check if file path is safe from path traversal attacks."""
        if not file_path:
            return False
        
        # Normalize path to resolve '..' and '.'
        try:
            normalized_path = os.path.normpath(file_path)
            absolute_path = os.path.abspath(normalized_path)
        except Exception as e:
            logger.warning(f"Error normalizing file path {file_path}: {e}")
            return False
        
        # Check for path traversal attempts and absolute system paths
        dangerous_patterns = [
            '..\\', '../', '~', '/etc/', '/var/', '/tmp/', '/proc/', '/sys/',
            'C:\\Windows\\', 'C:\\System32\\', '\\Windows\\', '\\System32\\',
            'Windows', 'System32', 
            'usr/local', 'home/', 'root/', 
        ]
        
        path_lower = absolute_path.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in path_lower:
                logger.warning(f"Dangerous pattern '{pattern}' found in file path: {absolute_path}")
                return False
        
        return True

    def _create_empty_logo(self) -> torch.Tensor:
        """Create an empty logo tensor in (1, H, W, 3) format."""
        # Default to a small, black image for empty output
        return torch.zeros((1, 64, 64, 3), dtype=torch.float32)

    def _create_empty_mask(self) -> torch.Tensor:
        """Create an empty mask tensor in (1, H, W) format (all zeros, i.e., fully transparent)."""
        return torch.zeros((1, 64, 64), dtype=torch.float32)

    def _get_default_color_palette(self) -> str:
        """Get default color palette JSON string."""
        default_palette = [
            {
                "name": "Primary Blue",
                "hex": "#0066CC",
                "id": "primary-blue"
            },
            {
                "name": "Secondary Gray", 
                "hex": "#666666",
                "id": "secondary-gray"
            },
            {
                "name": "Accent Orange",
                "hex": "#FF6600", 
                "id": "accent-orange"
            },
            {
                "name": "Background White",
                "hex": "#FFFFFF",
                "id": "background-white"
            },
            {
                "name": "Text Black",
                "hex": "#000000",
                "id": "text-black"
            }
        ]
        return json.dumps(default_palette, indent=2)

    def _process_logo_image(self, image: Image.Image) -> Tuple[torch.Tensor, torch.Tensor]:
        """Process logo image to extract RGB and alpha mask.
           Returns:
               rgb_image_tensor: torch.Tensor of shape (1, H, W, 3) (float32, 0-1)
               alpha_mask_tensor: torch.Tensor of shape (1, H, W) (float32, 0-1)
        """
        try:
            # Ensure image is in RGBA mode for consistent handling of alpha
            image = image.convert("RGBA")
            
            # Convert to numpy array and normalize to 0-1 range
            np_image = np.array(image).astype(np.float32) / 255.0
            
            # Extract RGB channels (first 3 channels) - shape will be (H, W, 3)
            rgb_tensor = torch.from_numpy(np_image[:, :, :3]) 
            
            # Extract alpha channel (4th channel) as mask - shape will be (H, W)
            alpha_tensor = torch.from_numpy(np_image[:, :, 3])
            
            # Add batch dimension to both tensors
            rgb_tensor = rgb_tensor.unsqueeze(0)  # Convert (H, W, 3) to (1, H, W, 3)
            alpha_tensor = alpha_tensor.unsqueeze(0) # Convert (H, W) to (1, H, W)
            
            return rgb_tensor, alpha_tensor
            
        except Exception as e:
            logger.error(f"Failed to process logo image: {e}")
            # Ensure empty tensors also have the correct batch dimension and format
            return self._create_empty_logo(), self._create_empty_mask()

    def _is_valid_image_file(self, file_path: str) -> bool:
        """Validate if file is a supported image format by checking extension."""
        if not file_path:
            return False
        supported_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _process_font_url(self, url: str, use_aria2c: bool = True, download_timeout: int = 30) -> str:
        """Process font URL - download if valid, return path or empty string."""
        if not url:
            return ""
        
        if not self._is_valid_url(url):
            logger.warning(f"Invalid font URL format: {url}")
            return ""
        
        # Check if it's a font file (simple extension check for now)
        if not any(ext in url.lower() for ext in ['.ttf', '.otf', '.woff', '.woff2']):
            logger.warning(f"URL does not seem to be a font file: {url}")
            return ""
        
        # Download the font file
        logger.info(f"[BrandAssetLoader] Downloading font from URL: {url}")
        downloaded_path = self._download_file_from_url(url, file_type="auto", use_aria2c=use_aria2c, download_timeout=download_timeout)
        if not downloaded_path:
            logger.warning(f"[BrandAssetLoader] Failed to download font from URL: {url}")
            return ""
        
        logger.info(f"[BrandAssetLoader] Downloaded font to: {downloaded_path}")
        return downloaded_path

    def _process_font_input(self, font_input: str, use_aria2c: bool = True, download_timeout: int = 30) -> str:
        """Process font input - download if URL, validate if file path."""
        if not font_input:
            return ""
        
        # Check if it's a URL
        if self._is_url(font_input):
            logger.info(f"[BrandAssetLoader] Detected font URL, downloading: {font_input}")
            downloaded_path = self._download_file_from_url(font_input, file_type="auto", use_aria2c=use_aria2c, download_timeout=download_timeout)
            if not downloaded_path:
                logger.warning(f"[BrandAssetLoader] Failed to download font from URL: {font_input}")
                return ""
            
            logger.info(f"[BrandAssetLoader] Downloaded font to: {downloaded_path}")
            return downloaded_path
        
        # Validate local file path
        if self._is_valid_font_file(font_input):
            return font_input
        
        logger.warning(f"[BrandAssetLoader] Invalid font input: {font_input}")
        return ""

    def _is_valid_font_file(self, file_path: str) -> bool:
        """Validate if file is a supported font format or URL."""
        if not file_path:
            return False
        
        # Check if it's a URL
        if self._is_url(file_path):
            # For URLs, check if it appears to be a font file
            supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
            return any(ext in file_path.lower() for ext in supported_extensions)
        
        # Check path safety first
        if not self._is_safe_file_path(file_path):
            return False
        
        supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _return_defaults(self, status_message: str = "No assets loaded") -> Tuple:
        """Return default values when asset loading fails."""
        empty_logo = self._create_empty_logo() 
        empty_mask = self._create_empty_mask() 
        
        # Create empty assets dictionary
        empty_assets = {
            "logo_vertical_color": empty_logo,
            "logo_vertical_color_mask": empty_mask,
            "logo_vertical_mono": empty_logo,
            "logo_vertical_mono_mask": empty_mask,
            "logo_horizontal_color": empty_logo,
            "logo_horizontal_color_mask": empty_mask,
            "logo_horizontal_mono": empty_logo,
            "logo_horizontal_mono_mask": empty_mask,
            "logo_icon": empty_logo,
            "logo_icon_mask": empty_mask,
            "font_primary": "",
            "font_primary_bold": "",
            "font_primary_italic": "",
            "font_secondary": "",
            "font_secondary_bold": "",
            "font_secondary_italic": "",
            "font_tertiary": "",
            "font_tertiary_bold": "",
            "font_tertiary_italic": "",
            "color_palette": self._get_default_color_palette(),
            "brand_name": "Unknown Brand",
            "status_message": status_message
        }
        
        return (
            empty_assets,
            empty_logo, empty_mask, empty_logo, empty_mask, empty_logo, empty_mask,
            empty_logo, empty_mask, empty_logo, empty_mask,
            "", "", "", "", "", "", "",
            self._get_default_color_palette(),
            "Unknown Brand",
            status_message
        )

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
}