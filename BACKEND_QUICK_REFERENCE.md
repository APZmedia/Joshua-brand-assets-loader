# Backend Quick Reference Guide

## Essential Information for Microservice Development

### 🎯 Core API Endpoint

**Brand Assets API:**
```
GET /api/brands/{brand_id}?depth=2
```

**Required Headers:**
```
Content-Type: application/json
Authorization: Bearer {api_token} (optional)
```

### 📊 Data Structure Requirements

#### Brand Response Format
```json
{
  "id": "brand-uuid",
  "name": "Brand Name",
  "logos": {
    "verticalColor": {"url": "https://cdn.example.com/logos/vertical-color.png", "width": 300, "height": 400, "format": "PNG"},
    "verticalMonocolor": {"url": "https://cdn.example.com/logos/vertical-mono.png", "width": 300, "height": 400, "format": "PNG"},
    "horizontalColor": {"url": "https://cdn.example.com/logos/horizontal-color.png", "width": 400, "height": 200, "format": "PNG"},
    "horizontalMonocolor": {"url": "https://cdn.example.com/logos/horizontal-mono.png", "width": 400, "height": 200, "format": "PNG"},
    "icon": {"url": "https://cdn.example.com/logos/icon.png", "width": 64, "height": 64, "format": "PNG"}
  },
  "fonts": {
    "primary": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/primary-variable.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/primary-regular.woff2", "format": "WOFF2"}, "weight": 400, "style": "normal"}]
    },
    "primaryBold": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/primary-bold.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/primary-bold.woff2", "format": "WOFF2"}, "weight": 700, "style": "normal"}]
    },
    "primaryItalic": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/primary-italic.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/primary-italic.woff2", "format": "WOFF2"}, "weight": 400, "style": "italic"}]
    },
    "secondary": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/secondary-variable.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/secondary-regular.woff2", "format": "WOFF2"}, "weight": 400, "style": "normal"}]
    },
    "secondaryBold": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/secondary-bold.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/secondary-bold.woff2", "format": "WOFF2"}, "weight": 700, "style": "normal"}]
    },
    "secondaryItalic": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/secondary-italic.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/secondary-italic.woff2", "format": "WOFF2"}, "weight": 400, "style": "italic"}]
    },
    "tertiary": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/tertiary-variable.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/tertiary-regular.woff2", "format": "WOFF2"}, "weight": 400, "style": "normal"}]
    },
    "tertiaryBold": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/tertiary-bold.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/tertiary-bold.woff2", "format": "WOFF2"}, "weight": 700, "style": "normal"}]
    },
    "tertiaryItalic": {
      "variableFontFile": {"url": "https://cdn.example.com/fonts/tertiary-italic.woff2", "format": "WOFF2"},
      "staticFontFiles": [{"fontFile": {"url": "https://cdn.example.com/fonts/tertiary-italic.woff2", "format": "WOFF2"}, "weight": 400, "style": "italic"}]
    }
  },
  "colorPalette": [
    {"name": "Primary Blue", "hex": "#0066CC", "id": "primary-blue"},
    {"name": "Secondary Gray", "hex": "#666666", "id": "secondary-gray"},
    {"name": "Accent Orange", "hex": "#FF6600", "id": "accent-orange"},
    {"name": "Background White", "hex": "#FFFFFF", "id": "background-white"},
    {"name": "Text Black", "hex": "#000000", "id": "text-black"}
  ]
}
```

### 🔧 Required Microservices

#### 1. Brand Assets Service
- **Purpose:** Serve brand data via REST API
- **Key Endpoint:** `GET /api/brands/{brand_id}`
- **Requirements:** Authentication, rate limiting, caching

#### 2. Asset Storage Service
- **Purpose:** Store and serve logos/fonts
- **Features:** CDN integration, signed URLs, format support
- **Supported Formats:** PNG, JPG, SVG, WOFF2, TTF, OTF

#### 3. Authentication Service
- **Purpose:** Handle API authentication
- **Features:** JWT tokens, API key management, rate limiting

#### 4. Image Processing Service
- **Purpose:** Process images for logo overlay
- **Endpoint:** `POST /api/images/process`
- **Operations:** Logo overlay, scaling, blending

#### 5. Color Generation Service
- **Purpose:** Generate solid color images
- **Endpoint:** `POST /api/colors/generate`
- **Features:** Hex validation, RGB/HSL conversion

#### 6. Gradient Generation Service
- **Purpose:** Create gradient overlays
- **Endpoint:** `POST /api/gradients/generate`
- **Types:** Linear, radial, conical gradients

### 🛡️ Security Requirements

#### Input Validation
- **Brand ID:** Alphanumeric, hyphens, underscores only (max 64 chars)
- **URLs:** HTTPS/HTTP only, domain allowlist
- **File Sizes:** 10MB max for logos, 5MB max for fonts
- **Image Dimensions:** 4096x4096 maximum

#### Authentication
- **Token Format:** Bearer JWT
- **Rate Limiting:** 1000 requests/hour per API key
- **CORS:** Configured for specific origins

### ⚡ Performance Targets

- **API Response:** < 200ms (95th percentile)
- **Asset Downloads:** < 2s for 1MB files
- **Image Processing:** < 500ms
- **Concurrent Users:** 10,000+
- **Throughput:** 100,000 requests/minute

### 🚨 Error Handling

#### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Brand Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

#### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "parameter": "value",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

### 📋 Implementation Checklist

#### Phase 1: Core API
- [ ] Brand Assets API endpoint
- [ ] Authentication service
- [ ] Basic error handling
- [ ] Input validation

#### Phase 2: Asset Management
- [ ] Asset storage service
- [ ] CDN integration
- [ ] Signed URL generation
- [ ] File format support

#### Phase 3: Processing Services
- [ ] Image processing service
- [ ] Color generation service
- [ ] Gradient generation service
- [ ] Performance optimization

#### Phase 4: Production Ready
- [ ] Rate limiting
- [ ] Caching strategy
- [ ] Monitoring and logging
- [ ] Load testing

### 🔗 Technology Recommendations

#### Backend Stack
- **Framework:** Node.js (Express/Fastify) or Python (FastAPI/Django)
- **Database:** PostgreSQL for metadata, Redis for caching
- **Storage:** AWS S3 or Google Cloud Storage
- **CDN:** Cloudflare or AWS CloudFront

#### Development Tools
- **Containerization:** Docker + Kubernetes
- **Monitoring:** APM tools (New Relic, DataDog)
- **Testing:** Jest (Node.js) or pytest (Python)
- **Documentation:** OpenAPI/Swagger

### 📞 Support Information

#### Key Files to Reference
- `BACKEND_API_DOCUMENTATION.md` - Complete API specifications
- `NODE_SPECIFICATIONS.md` - Detailed node requirements
- `assets/example_color_palette.json` - Color palette format example

#### Testing Resources
- Use the example brand assets in `assets/brand_assets/`
- Test with the provided color palette format
- Validate against the node input/output specifications

---

**Priority:** Start with the Brand Assets API endpoint and authentication service, then build out the asset storage and processing services incrementally.



