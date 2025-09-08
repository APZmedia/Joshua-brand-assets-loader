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
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APZmediaURLImageLoader:
    # Security constants
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    MAX_IMAGE_DIMENSION = 4096  # 4K max dimension
    ALLOWED_DOMAINS = set()  # Empty set means no domain restrictions
    ALLOWED_PROTOCOLS = {'https', 'http'}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "use_aria2c": ("BOOLEAN", {"default": True}),
                "download_timeout": ("INT", {"default": 30, "min": 10, "max": 300}),
                "max_width": ("INT", {"default": 2048, "min": 64, "max": 4096}),
                "max_height": ("INT", {"default": 2048, "min": 64, "max": 4096}),
                "resize_mode": ("STRING", {"choices": ["none", "fit", "crop", "stretch"], "default": "fit"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "status_message")

    FUNCTION = "load_image_from_url"
    CATEGORY = "apzmedia_brand"

    def load_image_from_url(self, url, use_aria2c=True, download_timeout=30, 
                           max_width=2048, max_height=2048, resize_mode="fit"):
        """
        Load image from URL (including signed URLs) and return as ComfyUI tensor.
        
        Args:
            url: URL to load image from (supports signed URLs)
            use_aria2c: Whether to use aria2c for faster downloads
            download_timeout: Download timeout in seconds
            max_width: Maximum width for resizing
            max_height: Maximum height for resizing
            resize_mode: How to resize the image
            
        Returns:
            Tuple of (image_tensor, mask_tensor, status_message)
        """
        try:
            # Input validation
            if not url or not url.strip():
                return self._return_empty("Error: No URL provided")
            
            url = url.strip()
            
            # Validate URL
            if not self._is_valid_url(url):
                return self._return_empty("Error: Invalid URL format")
            
            logger.info(f"Loading image from URL: {url[:100]}...")
            
            # Download image
            image_data = self._download_image_from_url(url, use_aria2c, download_timeout)
            if not image_data:
                return self._return_empty("Error: Failed to download image from URL")
            
            # Process image
            image_tensor, mask_tensor = self._process_image_data(
                image_data, max_width, max_height, resize_mode
            )
            
            if image_tensor is None:
                return self._return_empty("Error: Failed to process downloaded image")
            
            status_message = f"Successfully loaded image from URL (size: {image_tensor.shape[1]}x{image_tensor.shape[2]})"
            logger.info(status_message)
            
            return (image_tensor, mask_tensor, status_message)
            
        except Exception as e:
            logger.error(f"Failed to load image from URL: {e}")
            return self._return_empty(f"Error: {str(e)}")

    def _download_image_from_url(self, url: str, use_aria2c: bool = True, download_timeout: int = 30) -> Optional[bytes]:
        """Download image from URL and return raw bytes."""
        try:
            if use_aria2c and self._is_aria2c_available():
                return self._download_with_aria2c(url, download_timeout)
            else:
                return self._download_with_requests(url, download_timeout)
                
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None

    def _download_with_aria2c(self, url: str, timeout: int = 30) -> Optional[bytes]:
        """Download image using aria2c for better performance."""
        try:
            # Create temporary directory for downloads
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f'url_image-{timestamp}.tmp'
            file_path = os.path.join(temp_dir, filename)
            
            cmd = [
                "aria2c", 
                "-o", filename,
                "-x", "16",  # 16 connections
                "-s", "16",  # 16 splits
                url, 
                "-d", temp_dir,
                "--timeout", str(timeout),
                "--max-tries", "3"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"aria2c download completed: {result.stdout}")
            
            # Read downloaded file
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                # Clean up temporary file
                os.remove(file_path)
                
                # Validate file size
                if len(data) > self.MAX_FILE_SIZE:
                    logger.warning(f"Downloaded file too large: {len(data)} bytes")
                    return None
                
                return data
            else:
                logger.error("File not found after aria2c download")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"aria2c download failed: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"aria2c download error: {e}")
            return None

    def _download_with_requests(self, url: str, timeout: int = 30) -> Optional[bytes]:
        """Download image using requests as fallback."""
        try:
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image/', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp', 'image/tiff']):
                logger.warning(f"Invalid content type: {content_type}")
                return None
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                logger.warning(f"File too large: {content_length} bytes")
                return None
            
            # Download file
            data = b""
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    data += chunk
                    if len(data) > self.MAX_FILE_SIZE:
                        logger.warning("File exceeds size limit during download")
                        return None
            
            logger.info(f"Downloaded {len(data)} bytes from URL")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Requests download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    def _process_image_data(self, image_data: bytes, max_width: int, max_height: int, resize_mode: str) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor]]:
        """Process downloaded image data into ComfyUI tensors."""
        try:
            # Create image from bytes
            image = Image.open(BytesIO(image_data))
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                logger.warning(f"Image too large: {image.width}x{image.height}")
                return None, None
            
            # Convert to RGBA for consistent handling
            image = image.convert("RGBA")
            
            # Resize if needed
            if resize_mode != "none":
                image = self._resize_image(image, max_width, max_height, resize_mode)
            
            # Convert to ComfyUI tensor format
            return self._image_to_tensor(image)
            
        except Exception as e:
            logger.error(f"Failed to process image data: {e}")
            return None, None

    def _resize_image(self, image: Image.Image, max_width: int, max_height: int, resize_mode: str) -> Image.Image:
        """Resize image based on specified mode."""
        try:
            original_width, original_height = image.size
            
            if resize_mode == "fit":
                # Fit image within bounds while preserving aspect ratio
                ratio = min(max_width / original_width, max_height / original_height)
                if ratio < 1:
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            elif resize_mode == "crop":
                # Crop image to exact dimensions
                if original_width > max_width or original_height > max_height:
                    # Calculate crop box to center the image
                    left = max(0, (original_width - max_width) // 2)
                    top = max(0, (original_height - max_height) // 2)
                    right = min(original_width, left + max_width)
                    bottom = min(original_height, top + max_height)
                    image = image.crop((left, top, right, bottom))
            
            elif resize_mode == "stretch":
                # Stretch image to exact dimensions
                image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image

    def _image_to_tensor(self, image: Image.Image) -> Tuple[torch.Tensor, torch.Tensor]:
        """Convert PIL image to ComfyUI tensor format."""
        try:
            # Convert to numpy array and normalize to 0-1 range
            np_image = np.array(image).astype(np.float32) / 255.0
            
            # Extract RGB channels (first 3 channels) - shape will be (H, W, 3)
            rgb_tensor = torch.from_numpy(np_image[:, :, :3])
            
            # Extract alpha channel (4th channel) as mask - shape will be (H, W)
            alpha_tensor = torch.from_numpy(np_image[:, :, 3])
            
            # Add batch dimension to both tensors
            rgb_tensor = rgb_tensor.unsqueeze(0)  # Convert (H, W, 3) to (1, H, W, 3)
            alpha_tensor = alpha_tensor.unsqueeze(0)  # Convert (H, W) to (1, H, W)
            
            return rgb_tensor, alpha_tensor
            
        except Exception as e:
            logger.error(f"Failed to convert image to tensor: {e}")
            return None, None

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

    def _is_aria2c_available(self) -> bool:
        """Check if aria2c is available on the system."""
        try:
            subprocess.run(["aria2c", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _return_empty(self, status_message: str) -> Tuple[torch.Tensor, torch.Tensor, str]:
        """Return empty tensors with status message."""
        empty_image = torch.zeros((1, 64, 64, 3), dtype=torch.float32)
        empty_mask = torch.zeros((1, 64, 64), dtype=torch.float32)
        return (empty_image, empty_mask, status_message)

NODE_CLASS_MAPPINGS = {
    "APZmediaURLImageLoader": APZmediaURLImageLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaURLImageLoader": "APZmedia - URL Image Loader",
}
