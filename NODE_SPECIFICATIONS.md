# Node Specifications for Backend Microservices

## Overview

This document provides detailed specifications for each node in the Joshua Brand Assets Loader ComfyUI extension, including their input/output requirements, data formats, and the microservices needed to support them.

## Node Architecture Overview

The extension consists of 5 main nodes that work together to provide comprehensive brand asset management:

1. **APZmediaBrandAssetLoader** - Main asset loading node
2. **APZmediaColorPalette** - Color palette creation and management
3. **APZmediaLogoOverlay** - Logo placement and overlay functionality
4. **APZmediaSolidColor** - Solid color image generation
5. **APZmediaGradientOverlay** - Gradient overlay application

## 1. APZmediaBrandAssetLoader Node

### Purpose
Loads complete brand assets (logos, fonts, colors) from either an API or manual file paths.

### Input Parameters

#### Required Parameters
```typescript
interface BrandAssetLoaderInputs {
  load_method: "manual" | "api";  // Loading method selection
}
```

#### Optional Parameters (API Mode)
```typescript
interface APIModeInputs {
  api_brand_id: string;           // Brand identifier (UUID format)
  api_base_url: string;           // Base URL for brand API
  api_token: string;              // Authentication token (optional)
}
```

#### Optional Parameters (Manual Mode)
```typescript
interface ManualModeInputs {
  // Logo file paths or URLs
  logo_vertical_color: string;    // Vertical color logo path/URL
  logo_vertical_mono: string;     // Vertical monochrome logo path/URL
  logo_horizontal_color: string;  // Horizontal color logo path/URL
  logo_horizontal_mono: string;   // Horizontal monochrome logo path/URL
  logo_icon: string;              // Icon logo path/URL
  
  // Font file paths or URLs
  font_primary: string;           // Primary font path/URL
  font_primary_bold: string;      // Primary bold font path/URL
  font_primary_italic: string;    // Primary italic font path/URL
  font_secondary: string;         // Secondary font path/URL
  font_secondary_bold: string;    // Secondary bold font path/URL
  font_secondary_italic: string;  // Secondary italic font path/URL
  font_tertiary: string;          // Tertiary font path/URL
  font_tertiary_bold: string;     // Tertiary bold font path/URL
  font_tertiary_italic: string;   // Tertiary italic font path/URL
  
  // Color palette
  color_palette: string;          // JSON string of color palette
}
```

### Output Structure

#### Primary Output: Brand Assets Dictionary
```typescript
interface BrandAssets {
  // Logo tensors (PyTorch tensors in format: 1, H, W, 3)
  logo_vertical_color: torch.Tensor;
  logo_vertical_color_mask: torch.Tensor;
  logo_vertical_mono: torch.Tensor;
  logo_vertical_mono_mask: torch.Tensor;
  logo_horizontal_color: torch.Tensor;
  logo_horizontal_color_mask: torch.Tensor;
  logo_horizontal_mono: torch.Tensor;
  logo_horizontal_mono_mask: torch.Tensor;
  logo_icon: torch.Tensor;
  logo_icon_mask: torch.Tensor;
  
  // Font file paths
  font_primary: string;
  font_primary_bold: string;
  font_primary_italic: string;
  font_secondary: string;
  font_secondary_bold: string;
  font_secondary_italic: string;
  font_tertiary: string;
  font_tertiary_bold: string;
  font_tertiary_italic: string;
  
  // Metadata
  color_palette: string;          // JSON string
  brand_name: string;
  status_message: string;
}
```

#### Individual Outputs
The node also provides individual outputs for each asset type for direct connection to other nodes.

### Backend Requirements

#### API Endpoint Specification
```
GET /api/brands/{brand_id}?depth=2
```

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

## 2. APZmediaColorPalette Node

### Purpose
Creates and manages color palettes from individual hex color inputs.

### Input Parameters
```typescript
interface ColorPaletteInputs {
  // Required color inputs
  color_1: string;        // Hex color (e.g., "#FF0000")
  color_2: string;        // Hex color
  color_3: string;        // Hex color
  color_4: string;        // Hex color
  color_5: string;        // Hex color
  color_6: string;        // Hex color
  color_7: string;        // Hex color
  
  // Optional parameters
  palette_name: string;   // Name for the palette
  validate_colors: boolean; // Whether to validate hex format
}
```

### Output Structure
```typescript
interface ColorPaletteOutputs {
  // Individual color outputs
  color_1: string;        // Validated hex color
  color_2: string;        // Validated hex color
  color_3: string;        // Validated hex color
  color_4: string;        // Validated hex color
  color_5: string;        // Validated hex color
  color_6: string;        // Validated hex color
  color_7: string;        // Validated hex color
  
  // Combined outputs
  palette_json: string;   // JSON string of complete palette
  palette_name: string;   // Palette name
  status_message: string; // Validation status
}
```

### Backend Requirements

#### Color Validation Service
The backend should provide a color validation endpoint:

```
POST /api/colors/validate
```

**Request Body:**
```json
{
  "colors": ["#FF0000", "#00FF00", "#0000FF"],
  "validate_format": true
}
```

**Response:**
```json
{
  "valid": true,
  "validated_colors": ["#FF0000", "#00FF00", "#0000FF"],
  "invalid_colors": [],
  "palette_info": {
    "name": "Generated Palette",
    "colors": [
      {
        "name": "Primary",
        "hex": "#FF0000",
        "id": "color-1"
      },
      {
        "name": "Secondary", 
        "hex": "#00FF00",
        "id": "color-2"
      },
      {
        "name": "Accent",
        "hex": "#0000FF", 
        "id": "color-3"
      }
    ]
  }
}
```

## 3. APZmediaLogoOverlay Node

### Purpose
Places logos on background images with positioning, scaling, and blending controls.

### Input Parameters
```typescript
interface LogoOverlayInputs {
  // Required inputs
  brand_assets: BrandAssets;      // From BrandAssetLoader
  background_image: torch.Tensor; // Background image (1, H, W, 3)
  logo_selection: "vertical_color" | "vertical_mono" | "horizontal_color" | "horizontal_mono" | "icon";
  logo_type: "vertical" | "horizontal" | "auto";
  position: "top-left" | "top-center" | "top-right" | "center-left" | "center" | "center-right" | "bottom-left" | "bottom-center" | "bottom-right";
  scale_percentage: number;       // 1.0 to 100.0
  padding_percentage: number;     // 0.0 to 50.0
  rotation_degrees: number;       // -180.0 to 180.0
  offset_x: number;              // -1000 to 1000
  offset_y: number;              // -1000 to 1000
  
  // Optional inputs
  opacity: number;               // 0.0 to 1.0
  blend_mode: "normal" | "multiply" | "screen" | "overlay";
}
```

### Output Structure
```typescript
interface LogoOverlayOutputs {
  overlaid_image: torch.Tensor;  // Result image (1, H, W, 3)
}
```

### Backend Requirements

#### Image Processing Service
The backend should provide image processing capabilities:

```
POST /api/images/process
```

**Request Body:**
```json
{
  "operation": "logo_overlay",
  "background_image": "base64_encoded_image",
  "logo_image": "base64_encoded_logo",
  "logo_mask": "base64_encoded_mask",
  "parameters": {
    "position": "bottom-right",
    "scale_percentage": 15.0,
    "padding_percentage": 5.0,
    "rotation_degrees": 0.0,
    "offset_x": 0,
    "offset_y": 0,
    "opacity": 1.0,
    "blend_mode": "normal"
  }
}
```

**Response:**
```json
{
  "success": true,
  "processed_image": "base64_encoded_result",
  "processing_time": 0.245,
  "image_info": {
    "width": 1024,
    "height": 768,
    "format": "PNG"
  }
}
```

## 4. APZmediaSolidColor Node

### Purpose
Generates solid color images from hex color values.

### Input Parameters
```typescript
interface SolidColorInputs {
  hex_color: string;     // Hex color (e.g., "#FF0000")
  width: number;         // Image width (1 to 8192)
  height: number;        // Image height (1 to 8192)
  alpha: number;         // Opacity (0.0 to 1.0)
}
```

### Output Structure
```typescript
interface SolidColorOutputs {
  solid_color_image: torch.Tensor; // Generated image (1, H, W, 3)
}
```

### Backend Requirements

#### Color Generation Service
The backend should provide color generation capabilities:

```
POST /api/colors/generate
```

**Request Body:**
```json
{
  "hex_color": "#FF0000",
  "width": 512,
  "height": 512,
  "alpha": 1.0,
  "format": "PNG"
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "https://cdn.example.com/generated/color-ff0000-512x512.png",
  "image_data": "base64_encoded_image",
  "color_info": {
    "hex": "#FF0000",
    "rgb": {"r": 255, "g": 0, "b": 0},
    "hsl": {"h": 0, "s": 100, "l": 50}
  }
}
```

## 5. APZmediaGradientOverlay Node

### Purpose
Applies gradient overlays to background images with various gradient types and blending modes.

### Input Parameters
```typescript
interface GradientOverlayInputs {
  // Required inputs
  background_image: torch.Tensor; // Background image (1, H, W, 3)
  hex_color: string;              // Gradient color
  gradient_type: "linear" | "radial" | "conical";
  orientation: "horizontal" | "vertical" | "diagonal_tl_br" | "diagonal_tr_bl";
  start_position: "top" | "center" | "bottom" | "left" | "right" | "top-left" | "top-right" | "bottom-left" | "bottom-right";
  end_position: "top" | "center" | "bottom" | "left" | "right" | "top-left" | "top-right" | "bottom-left" | "bottom-right";
  start_alpha: number;            // 0.0 to 1.0
  end_alpha: number;              // 0.0 to 1.0
  
  // Optional inputs
  blend_mode: "normal" | "multiply" | "screen" | "overlay" | "soft_light" | "hard_light";
  opacity: number;                // 0.0 to 1.0
  gradient_center_x: number;      // 0.0 to 1.0
  gradient_center_y: number;      // 0.0 to 1.0
  gradient_radius: number;        // 0.0 to 2.0
}
```

### Output Structure
```typescript
interface GradientOverlayOutputs {
  gradient_overlay_image: torch.Tensor; // Result image (1, H, W, 3)
}
```

### Backend Requirements

#### Gradient Generation Service
The backend should provide gradient generation capabilities:

```
POST /api/gradients/generate
```

**Request Body:**
```json
{
  "background_image": "base64_encoded_image",
  "gradient_config": {
    "hex_color": "#000000",
    "gradient_type": "linear",
    "orientation": "horizontal",
    "start_position": "left",
    "end_position": "right",
    "start_alpha": 0.0,
    "end_alpha": 1.0,
    "blend_mode": "normal",
    "opacity": 1.0,
    "gradient_center_x": 0.5,
    "gradient_center_y": 0.5,
    "gradient_radius": 0.5
  }
}
```

**Response:**
```json
{
  "success": true,
  "processed_image": "base64_encoded_result",
  "gradient_info": {
    "type": "linear",
    "orientation": "horizontal",
    "color": "#000000",
    "alpha_range": [0.0, 1.0]
  }
}
```

## Data Flow Architecture

### Node Interaction Flow

```
1. BrandAssetLoader → Loads all brand assets
   ↓
2. ColorPalette → Creates/manages color palettes
   ↓
3. LogoOverlay → Places logos on images
   ↓
4. SolidColor → Generates solid color backgrounds
   ↓
5. GradientOverlay → Applies gradient effects
```

### Backend Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Brand API     │    │  Asset Storage  │    │ Authentication  │
│   Service       │    │   Service       │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
         │ Image Processing│    │ Color Generation│    │ Gradient        │
         │   Service       │    │   Service       │    │ Generation      │
         └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Security Considerations

### Input Validation
- All hex colors must be validated for proper format
- Image dimensions must be within acceptable limits
- File paths must be sanitized to prevent path traversal
- URLs must be validated for allowed protocols and domains

### Authentication
- API tokens must be validated for each request
- Rate limiting must be enforced per user/API key
- CORS must be properly configured for cross-origin requests

### File Handling
- Maximum file sizes must be enforced (10MB for logos, 5MB for fonts)
- Image dimensions must be limited (4096x4096 maximum)
- File format validation must be performed

## Performance Requirements

### Response Times
- Brand data API: < 200ms
- Asset downloads: < 2s for 1MB files
- Image processing: < 500ms
- Color validation: < 100ms

### Scalability
- Support 10,000+ concurrent users
- Handle 100,000 requests/minute
- Global CDN distribution for assets

## Error Handling

### Common Error Scenarios
1. **Invalid brand ID** - Return 404 with clear error message
2. **Missing assets** - Return partial data with status indicators
3. **Invalid color format** - Return default colors with warnings
4. **Image processing failures** - Return original image with error overlay
5. **Network timeouts** - Implement retry logic with exponential backoff

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "parameter": "value",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  }
}
```

## Testing Requirements

### Unit Tests
- Test each node's input validation
- Test output format consistency
- Test error handling scenarios

### Integration Tests
- Test complete workflows from asset loading to final output
- Test API integration with mock services
- Test performance under load

### End-to-End Tests
- Test complete ComfyUI workflow integration
- Test with real brand assets
- Test error recovery scenarios

---

This specification provides the foundation for building robust backend microservices that support all the nodes in the Joshua Brand Assets Loader ComfyUI extension. Each service should be designed for high availability, scalability, and maintainability.



