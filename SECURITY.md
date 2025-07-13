# Security Documentation

## Overview
This document outlines the security measures implemented in the Joshua Brand Assets Loader ComfyUI extension to protect against common vulnerabilities and ensure safe operation.

## Security Measures Implemented

### 🔒 Input Validation & Sanitization

#### URL Validation
- **Protocol Restrictions**: Only `http` and `https` protocols are allowed
- **Domain Validation**: Configurable domain whitelist (currently unrestricted)
- **Suspicious Pattern Detection**: Blocks URLs containing dangerous patterns:
  - `file://`, `ftp://`, `gopher://`, `data:`
  - `javascript:`, `vbscript:`
  - `onload=`, `onerror=`, `eval(`, `document.cookie`

#### Brand ID Validation
- **Format Validation**: Only alphanumeric characters, hyphens, and underscores allowed
- **Regex Pattern**: `^[a-zA-Z0-9_-]+$`
- **Prevents**: SQL injection, command injection, path traversal via ID

#### File Path Security
- **Path Traversal Protection**: Blocks dangerous path patterns:
  - `..` (directory traversal)
  - `~` (home directory)
  - System directories: `/etc/`, `/var/`, `/tmp/`, `/proc/`, `/sys/`
  - Windows system directories: `C:\Windows\`, `C:\System32\`
- **Path Normalization**: Uses `os.path.normpath()` and `os.path.abspath()`
- **Extension Validation**: Strict file type checking for images and fonts

### 🛡️ Resource Protection

#### File Size Limits
- **Maximum File Size**: 10MB per file
- **Streaming Downloads**: Prevents memory exhaustion attacks
- **Chunked Reading**: 8KB chunks with size monitoring

#### Image Dimension Limits
- **Maximum Dimension**: 4096 pixels (4K)
- **Prevents**: Memory exhaustion from oversized images
- **Validates**: Both width and height before processing

#### Content Type Validation
- **Image Validation**: Only allows image content types
- **Font Validation**: Only allows font file extensions
- **MIME Type Checking**: Validates server-provided content types

### 🔐 API Security

#### Authentication
- **Bearer Token Support**: Secure token-based authentication
- **Token Sanitization**: Tokens are not logged or exposed in error messages

#### Request Security
- **Timeout Limits**: 30-second timeout for all HTTP requests
- **Error Sanitization**: Generic error messages prevent information disclosure
- **Response Validation**: JSON structure validation before processing

### 📝 Logging Security

#### Sensitive Data Protection
- **URL Sanitization**: Only partial URLs are logged (e.g., `brand ID: 12345678...`)
- **Token Masking**: API tokens are never logged
- **Generic Error Messages**: No sensitive information in error logs
- **Path Sanitization**: File paths are not logged in detail

#### Log Levels
- **Info Level**: General operation status
- **Warning Level**: Security violations and validation failures
- **Error Level**: Generic error messages without sensitive details

### 🚫 Attack Prevention

#### Server-Side Request Forgery (SSRF)
- **URL Validation**: Comprehensive URL format and protocol checking
- **Domain Restrictions**: Configurable domain whitelist
- **Protocol Restrictions**: Only HTTP/HTTPS allowed

#### Path Traversal
- **Path Sanitization**: Normalization and absolute path resolution
- **Dangerous Pattern Detection**: Blocks common traversal patterns
- **Extension Validation**: Strict file type enforcement

#### Denial of Service (DoS)
- **File Size Limits**: Prevents large file uploads
- **Memory Protection**: Streaming downloads with size monitoring
- **Timeout Limits**: Prevents hanging requests

#### Information Disclosure
- **Error Sanitization**: Generic error messages
- **Log Sanitization**: No sensitive data in logs
- **Response Filtering**: Validates API responses before processing

## Configuration

### Security Constants
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
MAX_IMAGE_DIMENSION = 4096  # 4K max dimension
ALLOWED_DOMAINS = set()  # Empty set means no domain restrictions
ALLOWED_PROTOCOLS = {'https', 'http'}
```

### Domain Restrictions
To restrict API calls to specific domains, modify the `ALLOWED_DOMAINS` set:
```python
ALLOWED_DOMAINS = {'api.yourcompany.com', 'brands.yourcompany.com'}
```

## Best Practices

### For Users
1. **Use HTTPS**: Always use HTTPS URLs for API endpoints
2. **Secure Tokens**: Store API tokens securely, never in plain text
3. **Regular Updates**: Keep the extension updated for security patches
4. **Monitor Logs**: Check logs for security warnings

### For Developers
1. **Input Validation**: Always validate user inputs
2. **Error Handling**: Use generic error messages
3. **Resource Limits**: Implement file size and dimension limits
4. **Logging**: Never log sensitive information
5. **Dependencies**: Keep dependencies updated

## Security Checklist

- [x] Input validation for all user inputs
- [x] URL validation and sanitization
- [x] Path traversal protection
- [x] File size and dimension limits
- [x] Content type validation
- [x] Secure logging practices
- [x] Error message sanitization
- [x] Timeout limits
- [x] Protocol restrictions
- [x] Extension validation

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** create a public issue
2. **Email** security details to: security@apzmedia.com
3. **Include** detailed reproduction steps
4. **Wait** for acknowledgment before public disclosure

## Version History

### v1.0.0
- Initial security implementation
- Comprehensive input validation
- Resource protection measures
- Secure logging practices 