# Logo Nodes Documentation

## Overview

The APZmedia Logo nodes provide comprehensive logo placement and overlay capabilities for ComfyUI workflows. These nodes offer extensive personalization options, allowing users to create professional, brand-consistent designs with precise control over logo positioning, scaling, and blending.

## Node Information

### APZmediaLogoOverlay
- **Node Name**: `APZmediaLogoOverlay`
- **Display Name**: "APZmedia - Logo Overlay"
- **Category**: `apzmedia_brand`
- **Function**: `overlay_logo`

### APZmediaLogoPlacement
- **Node Name**: `APZmediaLogoPlacement`
- **Display Name**: "APZmedia - Logo Placement"
- **Category**: `apzmedia_brand`
- **Function**: `place_logo`

## Key Features

### Logo Selection and Management
- **Multiple Logo Variants**: Vertical, horizontal, monochrome, and icon options
- **Auto-Detection**: Automatic logo orientation detection
- **Brand Asset Integration**: Seamless integration with brand asset loader
- **Mask Support**: Alpha channel and mask support for complex logos

### Advanced Positioning
- **9-Point Positioning**: Top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right
- **Pixel-Perfect Offsets**: Precise X and Y offset control
- **Padding Control**: Percentage-based padding from edges
- **Boundary Clamping**: Automatic boundary protection

### Scaling and Transformation
- **Percentage-Based Scaling**: Scale as percentage of background
- **Aspect Ratio Preservation**: Maintains logo proportions
- **Rotation Support**: Full 360-degree rotation
- **Orientation-Aware Scaling**: Different scaling for vertical vs horizontal logos

### Professional Blending
- **Multiple Blend Modes**: Normal, multiply, screen, overlay
- **Opacity Control**: Precise transparency control
- **Alpha Channel Support**: Proper alpha blending
- **Mask-Based Blending**: Advanced masking capabilities

## APZmediaLogoOverlay Node

### Inputs

#### Required Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `brand_assets` | BRAND_ASSETS | Brand assets dictionary | - | - |
| `background_image` | IMAGE | Background image for overlay | - | - |
| `logo_selection` | SELECT | Logo variant to use | `vertical_color` | vertical_color, vertical_mono, horizontal_color, horizontal_mono, icon |
| `logo_type` | SELECT | Logo orientation | `auto` | vertical, horizontal, auto |
| `position` | SELECT | Logo position | `bottom-right` | 9-point positioning |
| `scale_percentage` | FLOAT | Logo size as percentage | 15.0 | 1.0-100.0 |
| `padding_percentage` | FLOAT | Padding from edges | 5.0 | 0.0-50.0 |
| `rotation_degrees` | FLOAT | Logo rotation | 0.0 | -180.0 to 180.0 |
| `offset_x` | INT | Horizontal offset | 0 | -1000 to 1000 |
| `offset_y` | INT | Vertical offset | 0 | -1000 to 1000 |

#### Optional Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `opacity` | FLOAT | Logo opacity | 1.0 | 0.0-1.0 |
| `blend_mode` | SELECT | Blending mode | `normal` | normal, multiply, screen, overlay |

### Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `overlaid_image` | IMAGE | Image with logo overlaid |

## APZmediaLogoPlacement Node

### Inputs

#### Required Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `background_image` | IMAGE | Background image | - | - |
| `logo_image` | IMAGE | Logo image | - | - |
| `logo_mask` | IMAGE | Logo mask/alpha | - | - |
| `position` | STRING | Logo position | - | 9-point positioning |
| `scale` | FLOAT | Logo scale factor | 0.2 | 0.01-1.0 |
| `offset_x` | INT | Horizontal offset | 0 | -1000 to 1000 |
| `offset_y` | INT | Vertical offset | 0 | -1000 to 1000 |

#### Optional Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `blend_mode` | STRING | Blending mode | `normal` | normal, multiply, screen, overlay |
| `opacity` | FLOAT | Logo opacity | 1.0 | 0.0-1.0 |

### Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `composited_image` | IMAGE | Final composited image |

## Personalization Options

### 1. Logo Selection and Variants

#### Logo Variants
```python
logo_selection = "vertical_color"    # Vertical logo in color
logo_selection = "vertical_mono"     # Vertical logo in monochrome
logo_selection = "horizontal_color"  # Horizontal logo in color
logo_selection = "horizontal_mono"   # Horizontal logo in monochrome
logo_selection = "icon"              # Icon/logo mark only
```

**Use Cases:**
- **vertical_color**: Standard vertical logo for most applications
- **vertical_mono**: Single-color version for limited color applications
- **horizontal_color**: Wide format for headers and banners
- **horizontal_mono**: Single-color horizontal for consistency
- **icon**: Logo mark for small spaces and social media

#### Auto-Detection
```python
logo_type = "auto"  # Automatically detect orientation
```

**Detection Logic:**
- **Aspect ratio > 1.2**: Detected as vertical
- **Aspect ratio < 0.8**: Detected as horizontal
- **Aspect ratio 0.8-1.2**: Defaults to horizontal

### 2. Positioning and Layout

#### 9-Point Positioning
```python
position = "top-left"      # Top-left corner
position = "top-center"    # Top center
position = "top-right"     # Top-right corner
position = "center-left"    # Left center
position = "center"        # Center of image
position = "center-right"  # Right center
position = "bottom-left"   # Bottom-left corner
position = "bottom-center" # Bottom center
position = "bottom-right"  # Bottom-right corner
```

**Use Cases:**
- **top-left**: Brand placement, watermarks
- **top-center**: Headers, banners
- **top-right**: Secondary branding
- **center**: Main focus, hero images
- **bottom-right**: Copyright, attribution
- **bottom-center**: Footer branding

#### Offset Control
```python
offset_x = 50   # Move 50 pixels right
offset_y = -25  # Move 25 pixels up
```

**Use Cases:**
- **Fine-tuning**: Precise positioning adjustments
- **Multiple logos**: Offset secondary logos
- **Design alignment**: Align with other elements
- **Responsive design**: Adjust for different screen sizes

#### Padding Control
```python
padding_percentage = 5.0  # 5% padding from edges
```

**Use Cases:**
- **Consistent spacing**: Maintain brand guidelines
- **Responsive design**: Scale with image size
- **Professional layout**: Avoid edge placement
- **Brand compliance**: Follow brand standards

### 3. Scaling and Transformation

#### Percentage-Based Scaling
```python
scale_percentage = 15.0  # 15% of background size
```

**Use Cases:**
- **Small logos**: 5-10% for watermarks
- **Medium logos**: 10-20% for standard placement
- **Large logos**: 20-50% for prominent branding
- **Hero logos**: 30-50% for main focus

#### Orientation-Aware Scaling
- **Vertical logos**: Scale based on height percentage
- **Horizontal logos**: Scale based on width percentage
- **Aspect ratio preservation**: Maintains logo proportions
- **Minimum size protection**: Ensures visibility

#### Rotation Control
```python
rotation_degrees = 45.0  # 45-degree rotation
```

**Use Cases:**
- **Creative effects**: Angled logos for dynamic designs
- **Brand guidelines**: Specific rotation requirements
- **Layout constraints**: Fit within design elements
- **Artistic expression**: Creative logo placement

### 4. Blending and Transparency

#### Blend Modes
```python
blend_mode = "normal"    # Standard alpha blending
blend_mode = "multiply"   # Darken background
blend_mode = "screen"     # Lighten background
blend_mode = "overlay"   # Increase contrast
```

**Use Cases:**
- **normal**: Standard logo placement
- **multiply**: Dark logos on light backgrounds
- **screen**: Light logos on dark backgrounds
- **overlay**: High contrast effects

#### Opacity Control
```python
opacity = 0.8  # 80% opacity
```

**Use Cases:**
- **Watermarks**: Low opacity (0.1-0.3)
- **Standard placement**: Full opacity (1.0)
- **Subtle branding**: Medium opacity (0.5-0.8)
- **Transparency effects**: Variable opacity

## Usage Examples

### Example 1: Standard Brand Placement
```python
# Logo Overlay Node
logo_selection = "vertical_color"
logo_type = "auto"
position = "bottom-right"
scale_percentage = 12.0
padding_percentage = 5.0
rotation_degrees = 0.0
offset_x = 0
offset_y = 0
opacity = 1.0
blend_mode = "normal"
```

### Example 2: Watermark Effect
```python
# Subtle watermark
logo_selection = "icon"
logo_type = "auto"
position = "center"
scale_percentage = 25.0
padding_percentage = 0.0
rotation_degrees = 0.0
offset_x = 0
offset_y = 0
opacity = 0.3
blend_mode = "normal"
```

### Example 3: Creative Placement
```python
# Angled logo for dynamic design
logo_selection = "horizontal_color"
logo_type = "horizontal"
position = "top-left"
scale_percentage = 18.0
padding_percentage = 8.0
rotation_degrees = 15.0
offset_x = 20
offset_y = -10
opacity = 0.9
blend_mode = "overlay"
```

## Workflow Integration

### Basic Logo Workflow
```
Background Image → Logo Overlay → Final Image
```

### Brand Asset Workflow
```
Brand Asset Loader → Logo Overlay → Final Image
```

### Multi-Logo Workflow
```
Background Image → Logo Overlay 1 → Logo Overlay 2 → Final Image
```

### Advanced Workflow
```
Background Image → Gradient Overlay → Logo Overlay → Text Overlay → Final Image
```

## Best Practices

### 1. Logo Selection
- **Choose appropriate variant** for your use case
- **Use auto-detection** for orientation
- **Consider background contrast** for visibility
- **Test different variants** for best results

### 2. Positioning Strategy
- **Follow brand guidelines** for placement
- **Use appropriate padding** to avoid edge placement
- **Consider visual hierarchy** in design
- **Test different positions** for optimal impact

### 3. Scaling Guidelines
- **Start with 10-15%** for standard placement
- **Use smaller percentages** for watermarks
- **Consider logo complexity** when scaling
- **Test readability** at different sizes

### 4. Blending and Transparency
- **Use normal blending** for standard placement
- **Try different blend modes** for creative effects
- **Adjust opacity** for subtle branding
- **Consider background colors** when choosing blend modes

## Troubleshooting

### Common Issues

#### 1. Logo Not Visible
**Symptoms**: Logo appears transparent or missing
**Solutions**:
- Check opacity value (should be > 0)
- Verify logo selection in brand assets
- Check blend mode compatibility
- Ensure logo is within image bounds

#### 2. Incorrect Positioning
**Symptoms**: Logo in wrong location
**Solutions**:
- Verify position setting
- Check offset values
- Adjust padding percentage
- Test with different positions

#### 3. Scaling Issues
**Symptoms**: Logo too large or too small
**Solutions**:
- Adjust scale_percentage value
- Check logo orientation detection
- Verify aspect ratio preservation
- Test with different background sizes

#### 4. Blending Problems
**Symptoms**: Unexpected blending results
**Solutions**:
- Try different blend modes
- Adjust opacity values
- Check background image contrast
- Test with different logo variants

### Debug Tips
1. **Start with high opacity** (1.0) to see logo clearly
2. **Use center positioning** for initial testing
3. **Test with simple backgrounds** first
4. **Check console output** for error messages

## Advanced Features

### 1. Mask Support
- **Alpha channel handling** for transparent logos
- **Mask-based blending** for complex shapes
- **Automatic mask scaling** with logo
- **Fallback handling** when masks unavailable

### 2. Orientation Detection
- **Automatic aspect ratio analysis**
- **Smart orientation selection**
- **Fallback to horizontal** for square logos
- **Manual override** when needed

### 3. Boundary Protection
- **Automatic clamping** to image boundaries
- **Minimum size protection** for visibility
- **Aspect ratio preservation** during scaling
- **Error handling** for edge cases

## Performance Considerations

### Processing Speed
- **Logo Overlay**: Faster processing with brand assets
- **Logo Placement**: More flexible but slower
- **Complex blending**: Additional processing time
- **Large images**: May require more memory

### Memory Usage
- **Brand assets**: Cached for efficiency
- **Mask processing**: Additional memory overhead
- **Large logos**: Consider memory limits
- **Batch processing**: Plan for cumulative usage

## Integration Examples

### ComfyUI Workflow
```
Load Image → Brand Asset Loader → Logo Overlay → Save Image
```

### Multi-Brand Workflow
```
Load Image → Brand Asset Loader → Logo Overlay → Text Overlay → Final Output
```

### Creative Workflow
```
Load Image → Gradient Overlay → Logo Overlay → Effects → Final Output
```

## Version History

- **v1.0**: Initial release with basic logo placement
- **v1.1**: Added brand asset integration
- **v1.2**: Enhanced positioning and scaling
- **v1.3**: Added rotation and advanced blending
- **v1.4**: Improved mask support and error handling

## Support and Resources

### Documentation
- Check console output for error messages
- Verify brand asset loading
- Test with different logo variants
- Review positioning and scaling parameters

### Troubleshooting
- Enable debug logging for detailed information
- Test with simple examples first
- Verify input image formats and dimensions
- Check brand asset structure and content

### Community
- Share successful logo placement examples
- Report issues with specific logo types
- Contribute improvements and optimizations
- Document best practices for different use cases

