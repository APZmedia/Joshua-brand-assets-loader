# Enhanced Brand Asset Loader - URL Support & Auto-Download

## Overview

The `APZmediaBrandAssetLoader` has been enhanced to support signed URLs and automatic file downloading capabilities. This allows users to provide URLs (including signed URLs from cloud storage services) for logos and fonts, and the system will automatically download them to temporary locations for processing.

## New Features

### 1. URL Detection & Support

The loader now automatically detects if an input is a URL and handles it appropriately:

#### Supported URL Schemes:
- **HTTP/HTTPS**: Standard web URLs
- **FTP**: File transfer protocol URLs
- **S3**: Amazon S3 URLs (`s3://bucket/path`)
- **R2**: Cloudflare R2 URLs (`https://account-id.r2.cloudflarestorage.com/bucket/path`)
- **GCS**: Google Cloud Storage URLs (`gs://bucket/path`)
- **Azure**: Azure Blob Storage URLs (`azure://container/path`)
- **Blob**: Browser blob URLs (`blob:https://...`)
- **Data**: Data URLs (`data:image/png;base64,...`)

#### Signed URL Support:
The system recognizes signed URLs containing authentication parameters:
- **Standard**: `?signature=...`, `?token=...`, `?expires=...`, `?access_key=...`
- **AWS S3/R2**: `?X-Amz-Algorithm=...`, `?X-Amz-Credential=...`, `?X-Amz-Date=...`, `?X-Amz-Expires=...`, `?X-Amz-SignedHeaders=...`, `?X-Amz-Signature=...`
- **Google Cloud**: `?googleaccessid=...`, `?expires=...`, `?signature=...`
- **Azure Blob**: `?sv=...`, `?sr=...`, `?sig=...`, `?st=...`, `?se=...`
- **Generic**: `?auth=...`, `?key=...`, `?id=...`, `?secret=...`

### 2. Automatic File Download

When a URL is detected, the system automatically downloads the file to a temporary location:

#### Download Methods:
1. **aria2c** (recommended): Fast multi-connection downloads
2. **requests** (fallback): Standard HTTP downloads

#### Download Configuration:
- **use_aria2c**: Boolean to enable/disable aria2c (default: True)
- **download_timeout**: Timeout in seconds (default: 30, range: 10-300)

### 3. Enhanced Input Types

New configuration options have been added to the node:

```python
"optional": {
    # Download Configuration
    "use_aria2c": ("BOOLEAN", {"default": True}),
    "download_timeout": ("INT", {"default": 30, "min": 10, "max": 300}),
    
    # ... existing options ...
}
```

## Usage Examples

### 1. Manual Loading with URLs

```python
# Logo URLs (including signed URLs)
logo_vertical_color = "https://s3.amazonaws.com/bucket/logo.png?signature=abc123"
logo_horizontal_color = "https://storage.googleapis.com/bucket/logo.jpg?token=xyz789"

# Cloudflare R2 signed URLs
logo_icon = "https://abc123.r2.cloudflarestorage.com/bucket/icon.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20130721%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20130721T201207Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d6796c98d7c6c1869311c0e0e1813a855adef6787ea82bebd66f9fb70d1a87c"

# Font URLs
font_primary = "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.ttf"
font_primary_bold = "https://example.com/fonts/Roboto-Bold.woff2?expires=1234567890"
font_secondary = "https://def456.r2.cloudflarestorage.com/fonts/opensans.ttf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20130721%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20130721T201207Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=abc123def456"

# The loader will automatically:
# 1. Detect these are URLs
# 2. Download them to temporary locations
# 3. Process them as if they were local files
```

### 2. API Loading with Enhanced Font Support

The API loading method now also supports downloading fonts from URLs returned by the API:

```python
# API response may contain font URLs like:
{
    "fonts": {
        "primary": {
            "variableFontFile": {
                "url": "https://cdn.example.com/fonts/Roboto-Variable.woff2?signature=abc123"
            }
        }
    }
}

# The loader will automatically download these fonts
```

### 3. Configuration Examples

```python
# Use aria2c for faster downloads (default)
use_aria2c = True
download_timeout = 30

# Fallback to requests if aria2c is not available
use_aria2c = False
download_timeout = 60

# Conservative timeout for slow connections
use_aria2c = True
download_timeout = 120
```

## Technical Implementation

### 1. URL Detection Algorithm

```python
def _is_url(self, input_string: str) -> bool:
    """Check if input string is a URL (including signed URLs)."""
    if not input_string or not isinstance(input_string, str):
        return False
    
    # Check for common URL patterns
    url_patterns = [
        r'^https?://',  # HTTP/HTTPS
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
    
    # Check for signed URLs with query parameters
    if '?' in input_string and any(param in input_string.lower() 
        for param in ['signature=', 'token=', 'expires=', 'access_key=']):
        return True
    
    return False
```

### 2. File Download Process

```python
def _download_file_from_url(self, url: str, file_type: str = "auto", 
                           use_aria2c: bool = True, download_timeout: int = 30) -> str:
    """Download file from URL to temporary location."""
    
    # 1. Validate URL
    if not self._is_url(url):
        return ""
    
    # 2. Create temporary directory
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download_temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # 3. Determine file extension
    if file_type == "auto":
        file_type = self._get_file_extension_from_url(url) or "tmp"
    
    # 4. Generate unique filename
    timestamp = int(time.time())
    filename = f'download-{timestamp}.{file_type}'
    file_path = os.path.join(temp_dir, filename)
    
    # 5. Download using preferred method
    if use_aria2c and self._is_aria2c_available():
        return self._download_with_aria2c(url, file_path, temp_dir)
    else:
        return self._download_with_requests(url, file_path, download_timeout)
```

### 3. Enhanced Logo Loading

```python
def _load_logo_from_path(self, file_path: str, use_aria2c: bool = True, 
                        download_timeout: int = 30) -> Tuple[torch.Tensor, torch.Tensor]:
    """Load logo from file path or URL with automatic download."""
    
    # Check if input is a URL
    if self._is_url(file_path):
        logger.info(f"Detected URL, downloading: {file_path}")
        downloaded_path = self._download_file_from_url(
            file_path, file_type="auto", use_aria2c=use_aria2c, 
            download_timeout=download_timeout
        )
        if not downloaded_path:
            return self._create_empty_logo(), self._create_empty_mask()
        
        file_path = downloaded_path
    
    # Continue with existing file processing logic...
```

## Security Features

### 1. URL Validation
- Protocol validation (only allowed protocols)
- Domain restrictions (if configured)
- Suspicious pattern detection
- Path traversal protection

### 2. File Size Limits
- Maximum file size: 10MB
- Maximum image dimension: 4096px
- Download size monitoring

### 3. Content Type Validation
- Image file validation for logos
- Font file validation for fonts
- MIME type checking

## Performance Optimizations

### 1. aria2c Integration
- Multi-connection downloads (16 connections)
- Multi-split downloads (16 splits)
- Resume capability for interrupted downloads

### 2. Caching Strategy
- Temporary files stored in `download_temp/` directory
- Unique filenames with timestamps
- Automatic cleanup (implemented by ComfyUI)

### 3. Fallback Mechanisms
- Graceful fallback from aria2c to requests
- Timeout handling
- Error recovery

## Error Handling

### 1. Download Failures
- Network timeout handling
- Invalid URL detection
- File size limit enforcement
- Content type validation

### 2. Graceful Degradation
- Empty tensor return on failure
- Logging of all errors
- Status message reporting

## Compatibility

### 1. Backward Compatibility
- All existing functionality preserved
- Local file paths work as before
- API loading unchanged

### 2. New Capabilities
- URL inputs automatically detected
- Signed URL support
- Cloud storage integration

## Installation Requirements

### 1. Optional Dependencies
- **aria2c**: For faster downloads (optional)
- **requests**: For HTTP downloads (included)
- **PIL/Pillow**: For image processing (included)

### 2. System Requirements
- Python 3.7+
- Internet connection for URL downloads
- Sufficient disk space for temporary files

## Testing

Run the test suite to verify functionality:

```bash
python test_url_detection.py
```

This will test:
- URL detection for various schemes
- File extension extraction
- Font validation
- Signed URL recognition

## Troubleshooting

### 1. Download Issues
- Check internet connectivity
- Verify URL accessibility
- Review timeout settings
- Check file size limits

### 2. aria2c Issues
- Install aria2c if not available
- Disable aria2c to use requests fallback
- Check aria2c version compatibility

### 3. File Processing Issues
- Verify file format support
- Check file size limits
- Review content type validation

## Future Enhancements

### 1. Planned Features
- Download progress reporting
- Custom download directories
- File format conversion
- Batch download support

### 2. Performance Improvements
- Connection pooling
- Download caching
- Parallel downloads
- Compression support
