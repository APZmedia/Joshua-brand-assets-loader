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
                return self._return_empty("❌ Error: No URL provided. Please enter a valid image URL.")
            
            url = url.strip()
            
            # Validate URL
            url_validation_result = self._validate_url_detailed(url)
            if not url_validation_result["valid"]:
                return self._return_empty(f"❌ URL Validation Error: {url_validation_result['error']}")
            
            logger.info(f"Loading image from URL: {url[:100]}...")
            
            # Download image
            download_result = self._download_image_from_url(url, use_aria2c, download_timeout)
            if not download_result["success"]:
                return self._return_empty(f"❌ Download Error: {download_result['error']}")
            
            image_data = download_result["data"]
            
            # Process image
            process_result = self._process_image_data_detailed(
                image_data, max_width, max_height, resize_mode
            )
            
            if not process_result["success"]:
                return self._return_empty(f"❌ Image Processing Error: {process_result['error']}")
            
            image_tensor, mask_tensor = process_result["tensors"]
            original_size = process_result["original_size"]
            final_size = process_result["final_size"]
            resize_info = process_result["resize_info"]
            
            status_message = f"✅ Successfully loaded image from URL\n📏 Original: {original_size[0]}x{original_size[1]} → Final: {final_size[0]}x{final_size[1]}\n🔧 Resize: {resize_info}"
            logger.info(f"Successfully loaded image: {original_size[0]}x{original_size[1]} → {final_size[0]}x{final_size[1]} ({resize_mode})")
            
            return (image_tensor, mask_tensor, status_message)
            
        except Exception as e:
            error_msg = f"❌ Unexpected Error: {str(e)}\n💡 Tip: Check URL accessibility, network connection, and image format support"
            logger.error(f"Failed to load image from URL: {e}")
            return self._return_empty(error_msg)

    def _validate_url_detailed(self, url: str) -> Dict[str, Union[bool, str]]:
        """Validate URL with detailed error information."""
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check scheme (protocol)
            if parsed.scheme not in self.ALLOWED_PROTOCOLS:
                return {
                    "valid": False,
                    "error": f"Protocol '{parsed.scheme}' not allowed. Use HTTP or HTTPS only."
                }
            
            # Check for domain restrictions if ALLOWED_DOMAINS is not empty
            if self.ALLOWED_DOMAINS and parsed.netloc and parsed.netloc not in self.ALLOWED_DOMAINS:
                return {
                    "valid": False,
                    "error": f"Domain '{parsed.netloc}' not in allowed list. Contact administrator."
                }
            
            # Check for suspicious patterns
            suspicious_patterns = [
                ('file://', 'Local file URLs are not allowed for security reasons'),
                ('ftp://', 'FTP protocol is not supported'),
                ('gopher://', 'Gopher protocol is not supported'),
                ('data:', 'Data URLs are not allowed for security reasons'),
                ('javascript:', 'JavaScript URLs are not allowed for security reasons'),
                ('vbscript:', 'VBScript URLs are not allowed for security reasons'),
                ('onload=', 'Suspicious JavaScript code detected'),
                ('onerror=', 'Suspicious JavaScript code detected'),
                ('eval(', 'Suspicious JavaScript code detected'),
                ('document.cookie', 'Suspicious JavaScript code detected')
            ]
            
            url_lower = url.lower()
            for pattern, message in suspicious_patterns:
                if pattern in url_lower:
                    return {
                        "valid": False,
                        "error": f"{message} (found: '{pattern}')"
                    }
            
            return {"valid": True, "error": ""}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"URL parsing failed: {str(e)}"
            }

    def _download_image_from_url(self, url: str, use_aria2c: bool = True, download_timeout: int = 30) -> Dict[str, Union[bool, str, bytes]]:
        """Download image from URL and return detailed result."""
        try:
            if use_aria2c and self._is_aria2c_available():
                result = self._download_with_aria2c(url, download_timeout)
                if result is not None:
                    return {"success": True, "data": result, "error": ""}
                else:
                    return {"success": False, "data": None, "error": "aria2c download failed - check network connection and URL accessibility"}
            else:
                result = self._download_with_requests(url, download_timeout)
                if result is not None:
                    return {"success": True, "data": result, "error": ""}
                else:
                    return {"success": False, "data": None, "error": "HTTP download failed - check network connection, URL accessibility, and content type"}
                
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": f"Download exception: {str(e)}"
            }

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
                    logger.warning(f"Downloaded file too large: {len(data)} bytes (max: {self.MAX_FILE_SIZE})")
                    return None
                
                return data
            else:
                logger.error("File not found after aria2c download")
                return None
                
        except subprocess.CalledProcessError as e:
            error_msg = f"aria2c command failed (exit code {e.returncode})"
            if e.stderr:
                error_msg += f": {e.stderr.strip()}"
            logger.error(error_msg)
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
            valid_image_types = ['image/', 'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/bmp', 'image/tiff']
            if not any(img_type in content_type for img_type in valid_image_types):
                logger.warning(f"Invalid content type: {content_type}. Expected image format.")
                return None
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.MAX_FILE_SIZE:
                logger.warning(f"File too large: {content_length} bytes (max: {self.MAX_FILE_SIZE})")
                return None
            
            # Download file
            data = b""
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    data += chunk
                    if len(data) > self.MAX_FILE_SIZE:
                        logger.warning(f"File exceeds size limit during download: {len(data)} bytes (max: {self.MAX_FILE_SIZE})")
                        return None
            
            logger.info(f"Downloaded {len(data)} bytes from URL")
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout after {timeout} seconds")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - check network connectivity and URL accessibility")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"Requests download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None

    def _process_image_data_detailed(self, image_data: bytes, max_width: int, max_height: int, resize_mode: str) -> Dict[str, Union[bool, str, Tuple, List]]:
        """Process downloaded image data into ComfyUI tensors with detailed information."""
        try:
            # Create image from bytes
            image = Image.open(BytesIO(image_data))
            original_size = (image.width, image.height)
            
            # Validate image dimensions
            if image.width > self.MAX_IMAGE_DIMENSION or image.height > self.MAX_IMAGE_DIMENSION:
                return {
                    "success": False,
                    "error": f"Image too large: {image.width}x{image.height} (max: {self.MAX_IMAGE_DIMENSION}x{self.MAX_IMAGE_DIMENSION})",
                    "tensors": None,
                    "original_size": original_size,
                    "final_size": original_size,
                    "resize_info": "Failed - image too large"
                }
            
            # Convert to RGBA for consistent handling
            image = image.convert("RGBA")
            
            # Resize if needed
            resize_info = ""
            if resize_mode != "none":
                image, resize_info = self._resize_image_detailed(image, max_width, max_height, resize_mode)
            else:
                resize_info = "No resizing applied"
            
            final_size = (image.width, image.height)
            
            # Convert to ComfyUI tensor format
            tensors = self._image_to_tensor(image)
            if tensors[0] is None:
                return {
                    "success": False,
                    "error": "Failed to convert image to tensor format",
                    "tensors": None,
                    "original_size": original_size,
                    "final_size": final_size,
                    "resize_info": resize_info
                }
            
            return {
                "success": True,
                "error": "",
                "tensors": tensors,
                "original_size": original_size,
                "final_size": final_size,
                "resize_info": resize_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Image processing failed: {str(e)}",
                "tensors": None,
                "original_size": (0, 0),
                "final_size": (0, 0),
                "resize_info": "Failed - processing error"
            }

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

    def _resize_image_detailed(self, image: Image.Image, max_width: int, max_height: int, resize_mode: str) -> Tuple[Image.Image, str]:
        """Resize image based on specified mode with detailed information."""
        try:
            original_width, original_height = image.size
            resize_info = ""
            
            if resize_mode == "fit":
                # Fit image within bounds while preserving aspect ratio
                ratio = min(max_width / original_width, max_height / original_height)
                if ratio < 1:
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resize_info = f"Scaled down by {ratio:.2f} to fit bounds"
                else:
                    resize_info = "No scaling needed - image fits within bounds"
            
            elif resize_mode == "crop":
                # Crop image to exact dimensions
                if original_width > max_width or original_height > max_height:
                    # Calculate crop box to center the image
                    left = max(0, (original_width - max_width) // 2)
                    top = max(0, (original_height - max_height) // 2)
                    right = min(original_width, left + max_width)
                    bottom = min(original_height, top + max_height)
                    image = image.crop((left, top, right, bottom))
                    resize_info = f"Cropped from center to {max_width}x{max_height}"
                else:
                    resize_info = "No cropping needed - image smaller than target"
            
            elif resize_mode == "stretch":
                # Stretch image to exact dimensions
                image = image.resize((max_width, max_height), Image.Resampling.LANCZOS)
                resize_info = f"Stretched to exact {max_width}x{max_height} (may distort aspect ratio)"
            
            return image, resize_info
            
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image, f"Resize failed: {str(e)}"

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
            return self._create_empty_image(), self._create_empty_mask()

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

    def _create_empty_image(self) -> torch.Tensor:
        """Create an empty image tensor in (1, H, W, 3) format."""
        return torch.zeros((1, 64, 64, 3), dtype=torch.float32)

    def _create_empty_mask(self) -> torch.Tensor:
        """Create an empty mask tensor in (1, H, W) format."""
        return torch.zeros((1, 64, 64), dtype=torch.float32)

    def _return_empty(self, status_message: str) -> Tuple[torch.Tensor, torch.Tensor, str]:
        """Return empty tensors with status message."""
        return (self._create_empty_image(), self._create_empty_mask(), status_message)

NODE_CLASS_MAPPINGS = {
    "APZmediaURLImageLoader": APZmediaURLImageLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaURLImageLoader": "APZmedia - URL Image Loader",
}
