#!/usr/bin/env python3
"""
Simplified test script for URL detection functionality.
"""

import re
import urllib.parse

def is_url(input_string):
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

def get_file_extension_from_url(url):
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
        print(f"Error extracting file extension from URL {url}: {e}")
    
    return ""

def test_url_detection():
    """Test URL detection functionality."""
    # Test various URL formats
    test_urls = [
        "https://example.com/image.png",
        "http://example.com/font.ttf",
        "https://s3.amazonaws.com/bucket/file.jpg?signature=abc123",
        "https://storage.googleapis.com/bucket/file.woff2?token=xyz789",
        "https://example.com/file.png?expires=1234567890&signature=def456",
        "ftp://example.com/file.ttf",
        "s3://bucket/file.otf",
        "gs://bucket/file.woff",
        "blob:https://example.com/12345678-1234-1234-1234-123456789012",
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        # Cloudflare R2 signed URL examples
        "https://abc123.r2.cloudflarestorage.com/bucket/logo.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20130721%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20130721T201207Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d6796c98d7c6c1869311c0e0e1813a855adef6787ea82bebd66f9fb70d1a87c",
        "https://def456.r2.cloudflarestorage.com/fonts/roboto.ttf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20130721%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20130721T201207Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=abc123def456",
    ]
    
    print("Testing URL detection:")
    for url in test_urls:
        result = is_url(url)
        print(f"  {url[:50]}{'...' if len(url) > 50 else ''} -> {result}")
    
    # Test non-URLs
    test_non_urls = [
        "/path/to/local/file.png",
        "C:\\Windows\\file.ttf",
        "file.txt",
        "relative/path/image.jpg",
        "",
        None,
    ]
    
    print("\nTesting non-URL detection:")
    for path in test_non_urls:
        result = is_url(path)
        print(f"  {str(path)[:50]}{'...' if len(str(path)) > 50 else ''} -> {result}")

def test_file_extension_extraction():
    """Test file extension extraction from URLs."""
    test_cases = [
        ("https://example.com/image.png", "png"),
        ("https://example.com/font.ttf?signature=abc123", "ttf"),
        ("https://s3.amazonaws.com/bucket/file.jpg", "jpg"),
        ("https://storage.googleapis.com/bucket/file.woff2", "woff2"),
        ("https://example.com/file.otf?expires=1234567890", "otf"),
        ("https://example.com/file", ""),
        ("https://example.com/file.", ""),
    ]
    
    print("\nTesting file extension extraction:")
    for url, expected in test_cases:
        ext = get_file_extension_from_url(url)
        status = "✓" if ext == expected else "✗"
        print(f"  {status} {url[:40]}{'...' if len(url) > 40 else ''} -> '{ext}' (expected: '{expected}')")

def test_font_validation():
    """Test font file validation."""
    test_cases = [
        ("https://example.com/font.ttf", True),
        ("https://example.com/font.otf", True),
        ("https://example.com/font.woff", True),
        ("https://example.com/font.woff2", True),
        ("https://example.com/image.png", False),
        ("/path/to/font.ttf", True),
        ("C:\\fonts\\font.otf", True),
        ("/path/to/image.jpg", False),
        ("", False),
    ]
    
    print("\nTesting font validation:")
    for input_str, expected in test_cases:
        # Check if it's a URL
        if is_url(input_str):
            # For URLs, check if it appears to be a font file
            supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
            is_valid = any(ext in input_str.lower() for ext in supported_extensions)
        else:
            # For local paths, check extension
            supported_extensions = [".ttf", ".otf", ".woff", ".woff2"]
            is_valid = any(input_str.lower().endswith(ext) for ext in supported_extensions)
        
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} {str(input_str)[:40]}{'...' if len(str(input_str)) > 40 else ''} -> {is_valid} (expected: {expected})")

if __name__ == "__main__":
    import os
    
    print("Enhanced Brand Asset Loader - URL Detection Test Suite")
    print("=" * 60)
    
    test_url_detection()
    test_file_extension_extraction()
    test_font_validation()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("\nKey Features Tested:")
    print("✓ URL detection (including signed URLs)")
    print("✓ File extension extraction from URLs")
    print("✓ Font file validation")
    print("✓ Support for various URL schemes (HTTP, HTTPS, S3, GCS, etc.)")
    print("✓ Support for signed URLs with query parameters")
