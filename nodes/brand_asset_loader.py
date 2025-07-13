import os
import torch
import requests
import json
import re
import urllib.parse
from PIL import Image
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from .global_brand_state import global_brand_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK", "IMAGE", "MASK",  # logos with masks: vertical_color, vertical_color_mask, vertical_mono, vertical_mono_mask, horizontal_color, horizontal_color_mask, horizontal_mono, horizontal_mono_mask, icon, icon_mask
        "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING",  # font paths: primary, primary_bold, primary_italic, secondary, secondary_bold, secondary_italic, tertiary, tertiary_bold, tertiary_italic
        "STRING",  # color palette JSON
        "STRING",  # brand name
        "STRING",  # status message
    )
    RETURN_NAMES = (
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
                         font_tertiary="", font_tertiary_bold="", font_tertiary_italic="", color_palette=""):
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
                return self._load_from_api(api_brand_id, api_base_url, api_token)
            else:
                return self._load_manual(
                    logo_vertical_color, logo_vertical_mono,
                    logo_horizontal_color, logo_horizontal_mono,
                    logo_icon, font_primary, font_primary_bold, font_primary_italic,
                    font_secondary, font_secondary_bold, font_secondary_italic,
                    font_tertiary, font_tertiary_bold, font_tertiary_italic, color_palette
                )
        except Exception as e:
            logger.error("Failed to load brand assets")
            return self._return_defaults("Error: Asset loading failed")

    def _load_from_api(self, brand_id: str, api_base_url: str, api_token: str) -> Tuple:
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
            
            # Load logos with URL validation
            logos = brand_data.get("logos", {})
            logo_vertical_color, logo_vertical_color_mask = self._load_logo_from_url(logos.get("verticalColor", {}).get("url", ""))
            logo_vertical_mono, logo_vertical_mono_mask = self._load_logo_from_url(logos.get("verticalMonocolor", {}).get("url", ""))
            logo_horizontal_color, logo_horizontal_color_mask = self._load_logo_from_url(logos.get("horizontalColor", {}).get("url", ""))
            logo_horizontal_mono, logo_horizontal_mono_mask = self._load_logo_from_url(logos.get("horizontalMonocolor", {}).get("url", ""))
            logo_icon, logo_icon_mask = self._load_logo_from_url(logos.get("icon", {}).get("url", ""))

            # Load fonts with URL validation
            fonts = brand_data.get("fonts", {})
            
            # Primary font variants
            primary_font_path = self._validate_font_url(fonts.get("primary", {}).get("variableFontFile", {}).get("url", ""))
            if not primary_font_path:
                static_files = fonts.get("primary", {}).get("staticFontFiles", [])
                if static_files:
                    primary_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            primary_bold_font_path = self._validate_font_url(fonts.get("primaryBold", {}).get("variableFontFile", {}).get("url", ""))
            if not primary_bold_font_path:
                static_files = fonts.get("primaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    primary_bold_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            primary_italic_font_path = self._validate_font_url(fonts.get("primaryItalic", {}).get("variableFontFile", {}).get("url", ""))
            if not primary_italic_font_path:
                static_files = fonts.get("primaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    primary_italic_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            # Secondary font variants
            secondary_font_path = self._validate_font_url(fonts.get("secondary", {}).get("variableFontFile", {}).get("url", ""))
            if not secondary_font_path:
                static_files = fonts.get("secondary", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            secondary_bold_font_path = self._validate_font_url(fonts.get("secondaryBold", {}).get("variableFontFile", {}).get("url", ""))
            if not secondary_bold_font_path:
                static_files = fonts.get("secondaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_bold_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            secondary_italic_font_path = self._validate_font_url(fonts.get("secondaryItalic", {}).get("variableFontFile", {}).get("url", ""))
            if not secondary_italic_font_path:
                static_files = fonts.get("secondaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    secondary_italic_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            # Tertiary font variants
            tertiary_font_path = self._validate_font_url(fonts.get("tertiary", {}).get("variableFontFile", {}).get("url", ""))
            if not tertiary_font_path:
                static_files = fonts.get("tertiary", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            tertiary_bold_font_path = self._validate_font_url(fonts.get("tertiaryBold", {}).get("variableFontFile", {}).get("url", ""))
            if not tertiary_bold_font_path:
                static_files = fonts.get("tertiaryBold", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_bold_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))
            
            tertiary_italic_font_path = self._validate_font_url(fonts.get("tertiaryItalic", {}).get("variableFontFile", {}).get("url", ""))
            if not tertiary_italic_font_path:
                static_files = fonts.get("tertiaryItalic", {}).get("staticFontFiles", [])
                if static_files:
                    tertiary_italic_font_path = self._validate_font_url(static_files[0].get("fontFile", {}).get("url", ""))

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
                logo_vertical_color, logo_vertical_color_mask, logo_vertical_mono, logo_vertical_mono_mask,
                logo_horizontal_color, logo_horizontal_color_mask, logo_horizontal_mono, logo_horizontal_mono_mask,
                logo_icon, logo_icon_mask, primary_font_path, primary_bold_font_path, primary_italic_font_path,
                secondary_font_path, secondary_bold_font_path, secondary_italic_font_path,
                tertiary_font_path, tertiary_bold_font_path, tertiary_italic_font_path,
                color_palette_json, brand_name, status_message
            )

        except requests.RequestException:
            return self._return_defaults("Network Error: Unable to connect to API")
        except json.JSONDecodeError:
            return self._return_defaults("API Error: Invalid response format")
        except Exception:
            return self._return_defaults("API Loading Error: Unexpected error occurred")

    def _load_manual(self, logo_vertical_color, logo_vertical_mono, 
                    logo_horizontal_color, logo_horizontal_mono, 
                    logo_icon, font_primary, font_primary_bold, font_primary_italic,
                    font_secondary, font_secondary_bold, font_secondary_italic,
                    font_tertiary, font_tertiary_bold, font_tertiary_italic, color_palette) -> Tuple:
        """Load brand assets from manual file paths."""
        try:
            # Load logos from file paths with path validation
            logo_vertical_color_img, logo_vertical_color_mask = self._load_logo_from_path(logo_vertical_color)
            logo_vertical_mono_img, logo_vertical_mono_mask = self._load_logo_from_path(logo_vertical_mono)
            logo_horizontal_color_img, logo_horizontal_color_mask = self._load_logo_from_path(logo_horizontal_color)
            logo_horizontal_mono_img, logo_horizontal_mono_mask = self._load_logo_from_path(logo_horizontal_mono)
            logo_icon_img, logo_icon_mask = self._load_logo_from_path(logo_icon)

            # Validate font paths
            primary_font_path = font_primary if self._is_valid_font_file(font_primary) else ""
            primary_bold_font_path = font_primary_bold if self._is_valid_font_file(font_primary_bold) else ""
            primary_italic_font_path = font_primary_italic if self._is_valid_font_file(font_primary_italic) else ""
            secondary_font_path = font_secondary if self._is_valid_font_file(font_secondary) else ""
            secondary_bold_font_path = font_secondary_bold if self._is_valid_font_file(font_secondary_bold) else ""
            secondary_italic_font_path = font_secondary_italic if self._is_valid_font_file(font_secondary_italic) else ""
            tertiary_font_path = font_tertiary if self._is_valid_font_file(font_tertiary) else ""
            tertiary_bold_font_path = font_tertiary_bold if self._is_valid_font_file(font_tertiary_bold) else ""
            tertiary_italic_font_path = font_tertiary_italic if self._is_valid_font_file(font_tertiary_italic) else ""

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
                logo_vertical_color_img, logo_vertical_color_mask, logo_vertical_mono_img, logo_vertical_mono_mask,
                logo_horizontal_color_img, logo_horizontal_color_mask, logo_horizontal_mono_img, logo_horizontal_mono_mask,
                logo_icon_img, logo_icon_mask, primary_font_path, primary_bold_font_path, primary_italic_font_path,
                secondary_font_path, secondary_bold_font_path, secondary_italic_font_path,
                tertiary_font_path, tertiary_bold_font_path, tertiary_italic_font_path,
                color_palette, brand_name, status_message
            )

        except Exception:
            return self._return_defaults("Manual Loading Error: Failed to load assets")

    def _load_logo_from_url(self, url: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load logo from URL with security validation. Returns (rgb_image, alpha_mask)."""
        if not url:
            return self._create_empty_logo(), self._create_empty_mask()
        
        # Validate URL
        if not self._is_valid_url(url):
            logger.warning("Invalid logo URL format")
            return self._create_empty_logo(), self._create_empty_mask()
        
        try:
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code != 200:
                logger.warning(f"Failed to download logo: HTTP {response.status_code}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp']):
                logger.warning(f"Invalid content type for logo: {content_type}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Check file size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                logger.warning(f"Logo file too large: {content_length} bytes")
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Read content with size limit
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.MAX_FILE_SIZE:
                    logger.warning("Logo file exceeds size limit")
                    return self._create_empty_logo(), self._create_empty_mask()
            
            # Create temporary file-like object
            from io import BytesIO
            image_data = BytesIO(content)
            image = Image.open(image_data)
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                logger.warning(f"Logo image too large: {image.width}x{image.height}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            return self._process_logo_image(image)
            
        except Exception as e:
            logger.error("Failed to load logo from URL")
            return self._create_empty_logo(), self._create_empty_mask()

    def _load_logo_from_path(self, file_path: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load logo from file path with path traversal protection. Returns (rgb_image, alpha_mask)."""
        if not file_path:
            return self._create_empty_logo(), self._create_empty_mask()
        
        # Validate and sanitize file path
        if not self._is_safe_file_path(file_path):
            logger.warning("Unsafe file path detected")
            return self._create_empty_logo(), self._create_empty_mask()
        
        try:
            if not os.path.exists(file_path):
                return self._create_empty_logo(), self._create_empty_mask()
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                logger.warning(f"Logo file too large: {file_size} bytes")
                return self._create_empty_logo(), self._create_empty_mask()
            
            if not self._is_valid_image_file(file_path):
                logger.warning("Invalid image file format")
                return self._create_empty_logo(), self._create_empty_mask()
            
            image = Image.open(file_path)
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                logger.warning(f"Logo image too large: {image.width}x{image.height}")
                return self._create_empty_logo(), self._create_empty_mask()
            
            return self._process_logo_image(image)
            
        except Exception as e:
            logger.error("Failed to load logo from path")
            return self._create_empty_logo(), self._create_empty_mask()

    def _validate_font_url(self, url: str) -> str:
        """Validate font URL and return safe URL or empty string."""
        if not url:
            return ""
        
        if not self._is_valid_url(url):
            return ""
        
        # Check if it's a font file
        if not any(ext in url.lower() for ext in ['.ttf', '.otf', '.woff', '.woff2']):
            return ""
        
        return url

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and security."""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check protocol
            if parsed.scheme not in self.ALLOWED_PROTOCOLS:
                return False
            
            # Check for domain restrictions
            if self.ALLOWED_DOMAINS and parsed.netloc not in self.ALLOWED_DOMAINS:
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                'file://', 'ftp://', 'gopher://', 'data:', 'javascript:',
                'vbscript:', 'onload=', 'onerror=', 'eval(', 'document.cookie'
            ]
            
            url_lower = url.lower()
            for pattern in suspicious_patterns:
                if pattern in url_lower:
                    return False
            
            return True
        except Exception:
            return False

    def _is_valid_brand_id(self, brand_id: str) -> bool:
        """Validate brand ID format."""
        if not brand_id:
            return False
        
        # Only allow alphanumeric characters, hyphens, and underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', brand_id))

    def _is_safe_file_path(self, file_path: str) -> bool:
        """Check if file path is safe from path traversal attacks."""
        if not file_path:
            return False
        
        # Normalize path
        try:
            normalized_path = os.path.normpath(file_path)
            absolute_path = os.path.abspath(normalized_path)
        except Exception:
            return False
        
        # Check for path traversal attempts
        dangerous_patterns = [
            '..', '~', '/etc/', '/var/', '/tmp/', '/proc/', '/sys/',
            'C:\\Windows\\', 'C:\\System32\\', '\\Windows\\', '\\System32\\',
            'Windows', 'System32'
        ]
        path_lower = absolute_path.lower()
        for pattern in dangerous_patterns:
            if pattern in path_lower:
                return False
        # Allow any drive letter, just block system folders
        return True

    def _create_empty_logo(self) -> torch.Tensor:
        """Create an empty logo tensor."""
        return torch.zeros((3, 64, 64))

    def _create_empty_mask(self) -> torch.Tensor:
        """Create an empty mask tensor."""
        return torch.zeros((1, 64, 64))

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
        """Process logo image to extract RGB and alpha mask."""
        try:
            # Check if image has alpha channel
            has_alpha = image.mode == "RGBA"
            
            if has_alpha:
                # Image has alpha channel - extract it
                np_image = np.array(image).astype(np.float32) / 255.0
                
                # Extract RGB channels (first 3 channels)
                rgb_tensor = torch.from_numpy(np_image[:, :, :3]).permute(2, 0, 1)  # (C, H, W)
                
                # Extract alpha channel (4th channel) as mask
                alpha_tensor = torch.from_numpy(np_image[:, :, 3]).unsqueeze(0)  # (1, H, W)
            else:
                # No alpha channel - convert to RGB and create full opacity mask
                rgb_image = image.convert("RGB")
                np_image = np.array(rgb_image).astype(np.float32) / 255.0
                rgb_tensor = torch.from_numpy(np_image).permute(2, 0, 1)  # (C, H, W)
                
                # Create full opacity mask (all white)
                height, width = rgb_image.size[1], rgb_image.size[0]
                alpha_tensor = torch.ones((1, height, width))
            
            return rgb_tensor, alpha_tensor
            
        except Exception as e:
            logger.error("Failed to process logo image")
            return self._create_empty_logo(), self._create_empty_mask()

    def _is_valid_image_file(self, file_path: str) -> bool:
        """Validate if file is a supported image format."""
        if not file_path:
            return False
        supported_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)

    def _is_valid_font_file(self, file_path: str) -> bool:
        """Validate if file is a supported font format."""
        if not file_path:
            return False
        
        # Check path safety first
        if not self._is_safe_file_path(file_path):
            return False
        
        supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
        return any(file_path.lower().endswith(ext) for ext in supported_extensions)



    def _return_defaults(self, status_message: str = "No assets loaded") -> Tuple:
        """Return default values when asset loading fails."""
        empty_logo = self._create_empty_logo()
        empty_mask = self._create_empty_mask()
        return (
            empty_logo, empty_mask, empty_logo, empty_mask, empty_logo, empty_mask, 
            empty_logo, empty_mask, empty_logo, empty_mask,  # logos with masks
            "", "", "", "", "", "", "", "", "",  # font paths (primary, primary_bold, primary_italic, secondary, secondary_bold, secondary_italic, tertiary, tertiary_bold, tertiary_italic)
            self._get_default_color_palette(),  # default color palette
            "Unknown Brand",  # brand name
            status_message  # status message
        )

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
}
