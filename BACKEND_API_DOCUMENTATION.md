# Backend API Documentation for Brand Asset Nodes

## Overview

This document provides comprehensive specifications for backend microservices that need to support the Joshua Brand Assets Loader ComfyUI extension. The extension provides nodes for loading brand assets (colors, fonts, logos) and applying them to AI-generated images.

## Table of Contents

1. [Core Node Architecture](#core-node-architecture)
2. [API Requirements](#api-requirements)
3. [Data Structures](#data-structures)
4. [Microservice Specifications](#microservice-specifications)
5. [Security Requirements](#security-requirements)
6. [Error Handling](#error-handling)
7. [Performance Requirements](#performance-requirements)
8. [Testing Specifications](#testing-specifications)

## Core Node Architecture

### Primary Node: APZmediaBrandAssetLoader

This is the main node that loads all brand assets from either an API or manual file paths.

**Node Function:** `load_brand_assets`
**Category:** `apzmedia_brand`

#### Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `load_method` | String | Yes | "manual" or "api" |
| `api_brand_id` | String | API mode | Brand identifier |
| `api_base_url` | String | API mode | Base URL for brand API |
| `api_token` | String | No | Authentication token |

#### Output Structure

The node returns a comprehensive set of brand assets:

**Logo Assets (5 variations with masks):**
- `logo_vertical_color` + `logo_vertical_color_mask`
- `logo_vertical_mono` + `logo_vertical_mono_mask`
- `logo_horizontal_color` + `logo_horizontal_color_mask`
- `logo_horizontal_mono` + `logo_horizontal_mono_mask`
- `logo_icon` + `logo_icon_mask`

**Font Assets (9 font files):**
- `font_primary`, `font_primary_bold`, `font_primary_italic`
- `font_secondary`, `font_secondary_bold`, `font_secondary_italic`
- `font_tertiary`, `font_tertiary_bold`, `font_tertiary_italic`

**Metadata:**
- `color_palette` (JSON string)
- `brand_name` (String)
- `status_message` (String)

## API Requirements

### Brand Assets API Endpoint

**Endpoint:** `GET /api/brands/{brand_id}?depth=2`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {api_token} (optional)
```

**Response Format:**
```json
{
  "id": "brand-uuid",
  "name": "Brand Name",
  "logos": {
    "verticalColor": {
      "url": "https://cdn.example.com/logos/vertical-color.png",
      "width": 300,
      "height": 400,
      "format": "PNG"
    },
    "verticalMonocolor": {
      "url": "https://cdn.example.com/logos/vertical-mono.png",
      "width": 300,
      "height": 400,
      "format": "PNG"
    },
    "horizontalColor": {
      "url": "https://cdn.example.com/logos/horizontal-color.png",
      "width": 400,
      "height": 200,
      "format": "PNG"
    },
    "horizontalMonocolor": {
      "url": "https://cdn.example.com/logos/horizontal-mono.png",
      "width": 400,
      "height": 200,
      "format": "PNG"
    },
    "icon": {
      "url": "https://cdn.example.com/logos/icon.png",
      "width": 64,
      "height": 64,
      "format": "PNG"
    }
  },
  "fonts": {
    "primary": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/primary-variable.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/primary-regular.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "normal"
        }
      ]
    },
    "primaryBold": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/primary-bold.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/primary-bold.woff2",
            "format": "WOFF2"
          },
          "weight": 700,
          "style": "normal"
        }
      ]
    },
    "primaryItalic": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/primary-italic.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/primary-italic.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "italic"
        }
      ]
    },
    "secondary": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/secondary-variable.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/secondary-regular.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "normal"
        }
      ]
    },
    "secondaryBold": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/secondary-bold.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/secondary-bold.woff2",
            "format": "WOFF2"
          },
          "weight": 700,
          "style": "normal"
        }
      ]
    },
    "secondaryItalic": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/secondary-italic.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/secondary-italic.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "italic"
        }
      ]
    },
    "tertiary": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/tertiary-variable.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/tertiary-regular.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "normal"
        }
      ]
    },
    "tertiaryBold": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/tertiary-bold.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/tertiary-bold.woff2",
            "format": "WOFF2"
          },
          "weight": 700,
          "style": "normal"
        }
      ]
    },
    "tertiaryItalic": {
      "variableFontFile": {
        "url": "https://cdn.example.com/fonts/tertiary-italic.woff2",
        "format": "WOFF2"
      },
      "staticFontFiles": [
        {
          "fontFile": {
            "url": "https://cdn.example.com/fonts/tertiary-italic.woff2",
            "format": "WOFF2"
          },
          "weight": 400,
          "style": "italic"
        }
      ]
    }
  },
  "colorPalette": [
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
}
```

## Data Structures

### Logo Asset Structure

```typescript
interface LogoAsset {
  url: string;           // Direct download URL (supports signed URLs)
  width: number;         // Image width in pixels
  height: number;        // Image height in pixels
  format: string;        // File format (PNG, JPG, SVG, etc.)
  altText?: string;      // Optional alt text for accessibility
}
```

### Font Asset Structure

```typescript
interface FontAsset {
  variableFontFile?: {
    url: string;         // Variable font file URL
    format: string;      // File format (WOFF2, TTF, OTF)
  };
  staticFontFiles: {
    fontFile: {
      url: string;       // Static font file URL
      format: string;    // File format
    };
    weight: number;      // Font weight (100-900)
    style: string;       // Font style (normal, italic)
  }[];
}
```

### Color Palette Structure

```typescript
interface ColorPalette {
  name: string;          // Color name
  hex: string;           // Hex color code (#RRGGBB)
  id: string;            // Unique identifier
  rgb?: {                // Optional RGB values
    r: number;
    g: number;
    b: number;
  };
  hsl?: {                // Optional HSL values
    h: number;
    s: number;
    l: number;
  };
}
```

## Microservice Specifications

### 1. Brand Assets Service

**Purpose:** Serve brand assets (logos, fonts, colors) via REST API

**Endpoints:**
- `GET /api/brands/{brand_id}` - Get complete brand data
- `GET /api/brands/{brand_id}/logos` - Get logo assets only
- `GET /api/brands/{brand_id}/fonts` - Get font assets only
- `GET /api/brands/{brand_id}/colors` - Get color palette only

**Requirements:**
- Support for signed URLs for secure asset delivery
- CORS headers for cross-origin requests
- Rate limiting (1000 requests/hour per API key)
- Response caching (5 minutes for brand data, 1 hour for assets)

### 2. Asset Storage Service

**Purpose:** Store and serve brand assets (logos, fonts)

**Requirements:**
- Support for multiple file formats (PNG, JPG, SVG, WOFF2, TTF, OTF)
- Image optimization and resizing
- Font subsetting for web delivery
- CDN integration for global distribution
- Signed URL generation for secure access

### 3. Authentication Service

**Purpose:** Handle API authentication and authorization

**Requirements:**
- JWT token generation and validation
- API key management
- Role-based access control
- Rate limiting per user/API key
- Token refresh mechanism

## Security Requirements

### Input Validation

1. **Brand ID Validation:**
   - Only alphanumeric characters, hyphens, and underscores
   - Maximum length: 64 characters
   - No path traversal characters

2. **URL Validation:**
   - Only HTTPS and HTTP protocols
   - Domain allowlist (configurable)
   - No suspicious patterns (file://, javascript:, etc.)

3. **File Size Limits:**
   - Logo files: 10MB maximum
   - Font files: 5MB maximum
   - Image dimensions: 4096x4096 maximum

### Authentication & Authorization

1. **API Token Requirements:**
   - Bearer token format
   - JWT with expiration
   - Scope-based permissions

2. **Rate Limiting:**
   - 1000 requests/hour per API key
   - 100 requests/minute per IP
   - Exponential backoff for violations

3. **CORS Configuration:**
   - Allow specific origins only
   - Required headers: Content-Type, Authorization
   - Preflight request handling

## Error Handling

### HTTP Status Codes

| Code | Description | Response Format |
|------|-------------|-----------------|
| 200 | Success | Brand data JSON |
| 400 | Bad Request | Error message |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Brand not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Generic error |

### Error Response Format

```json
{
  "error": {
    "code": "BRAND_NOT_FOUND",
    "message": "Brand with ID 'invalid-id' not found",
    "details": {
      "brand_id": "invalid-id",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Common Error Codes

- `INVALID_BRAND_ID` - Brand ID format is invalid
- `BRAND_NOT_FOUND` - Brand doesn't exist
- `ASSET_NOT_FOUND` - Specific asset not available
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INVALID_TOKEN` - Authentication token is invalid
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions

## Performance Requirements

### Response Times

- **Brand data API:** < 200ms (95th percentile)
- **Asset downloads:** < 2s for 1MB files (95th percentile)
- **Image processing:** < 500ms for logo resizing

### Scalability

- **Concurrent users:** 10,000+ simultaneous connections
- **Throughput:** 100,000 requests/minute
- **Storage:** Petabyte-scale asset storage
- **CDN:** Global distribution with < 50ms latency

### Caching Strategy

1. **API Responses:**
   - Brand data: 5 minutes
   - Asset metadata: 1 hour
   - Error responses: 1 minute

2. **Asset Files:**
   - Logos: 24 hours
   - Fonts: 7 days
   - Color palettes: 1 hour

3. **CDN Caching:**
   - Static assets: 30 days
   - Dynamic content: 5 minutes

## Testing Specifications

### Unit Tests

1. **API Endpoint Tests:**
   - Valid brand ID returns correct data
   - Invalid brand ID returns 404
   - Missing authentication returns 401
   - Rate limiting works correctly

2. **Data Validation Tests:**
   - Logo URL validation
   - Font file format validation
   - Color palette structure validation
   - Brand ID format validation

### Integration Tests

1. **End-to-End Workflows:**
   - Complete brand asset loading
   - Logo overlay functionality
   - Color palette application
   - Font rendering

2. **Performance Tests:**
   - Load testing with 1000+ concurrent users
   - Asset download performance
   - API response time under load

### Security Tests

1. **Authentication Tests:**
   - Valid token acceptance
   - Invalid token rejection
   - Expired token handling
   - Token refresh functionality

2. **Input Validation Tests:**
   - SQL injection prevention
   - Path traversal prevention
   - XSS prevention
   - File upload security

## Implementation Guidelines

### Technology Stack Recommendations

1. **Backend Framework:**
   - Node.js with Express or Fastify
   - Python with FastAPI or Django
   - Go with Gin or Echo

2. **Database:**
   - PostgreSQL for brand metadata
   - Redis for caching and sessions
   - MongoDB for flexible asset metadata

3. **Storage:**
   - AWS S3 or Google Cloud Storage
   - CDN: Cloudflare or AWS CloudFront
   - Image processing: Sharp (Node.js) or Pillow (Python)

4. **Authentication:**
   - JWT tokens
   - OAuth 2.0 integration
   - API key management

### Deployment Considerations

1. **Containerization:**
   - Docker containers for each microservice
   - Kubernetes for orchestration
   - Health checks and auto-scaling

2. **Monitoring:**
   - Application performance monitoring (APM)
   - Error tracking and alerting
   - Usage analytics and reporting

3. **Backup & Recovery:**
   - Automated backups of brand data
   - Asset file replication
   - Disaster recovery procedures

## Support and Maintenance

### Documentation Requirements

1. **API Documentation:**
   - OpenAPI/Swagger specification
   - Interactive API explorer
   - Code examples in multiple languages

2. **Integration Guides:**
   - ComfyUI node integration
   - SDK development
   - Webhook configuration

3. **Troubleshooting:**
   - Common error solutions
   - Performance optimization tips
   - Security best practices

### Maintenance Schedule

1. **Regular Updates:**
   - Security patches: Within 24 hours
   - Feature updates: Monthly
   - Performance optimizations: Quarterly

2. **Monitoring:**
   - 24/7 uptime monitoring
   - Performance metrics tracking
   - Error rate monitoring

3. **Support:**
   - Developer support via email/chat
   - Documentation updates
   - Community forum maintenance

---

This documentation provides the foundation for building robust microservices that support the Joshua Brand Assets Loader ComfyUI extension. The specifications ensure compatibility, security, and performance while maintaining flexibility for future enhancements.



