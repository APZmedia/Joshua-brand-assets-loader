# Gradient Overlay Node Documentation

## Overview

The **APZmedia Gradient Overlay** node is a powerful tool for creating sophisticated gradient overlays on images. It supports multiple gradient types, blending modes, and extensive customization options, making it perfect for creating professional-looking visual effects and brand-consistent designs.

## Node Information

- **Node Name**: `APZmediaGradientOverlay`
- **Display Name**: "APZmedia Gradient Overlay"
- **Category**: `apzmedia_brand`
- **Function**: `create_gradient_overlay`

## Key Features

### Multiple Gradient Types
- **Linear Gradients**: 4-directional linear gradients with customizable positioning
- **Radial Gradients**: Circular gradients with adjustable center and radius
- **Conical Gradients**: Angular gradients for special effects

### Advanced Blending
- **6 Blending Modes**: Normal, multiply, screen, overlay, soft light, hard light
- **Opacity Control**: Precise opacity management for start and end points
- **Position Control**: Customizable gradient start and end positions

### Personalization Options
- **Color Customization**: Full hex color support with validation
- **Gradient Positioning**: Precise control over gradient placement
- **Blend Mode Selection**: Professional blending options
- **Opacity Interpolation**: Smooth opacity transitions

## Inputs

### Required Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `background_image` | IMAGE | Background image for overlay | - | - |
| `hex_color` | STRING | Gradient color in hex format | `#0066CC` | Valid hex colors |
| `gradient_type` | SELECT | Type of gradient | `linear` | linear, radial, conical |
| `orientation` | SELECT | Direction for linear gradients | `top` | top, bottom, left, right |
| `start_position` | FLOAT | Gradient start position | 0.0 | 0.0-1.0 |
| `end_position` | FLOAT | Gradient end position | 1.0 | 0.0-1.0 |
| `start_opacity` | FLOAT | Starting opacity | 0.0 | 0.0-1.0 |
| `end_opacity` | FLOAT | Ending opacity | 0.7 | 0.0-1.0 |

### Optional Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `blend_mode` | SELECT | Blending mode | `normal` | normal, multiply, screen, overlay, soft_light, hard_light |
| `gradient_center_x` | FLOAT | Center X for radial/conical | 0.5 | 0.0-1.0 |
| `gradient_center_y` | FLOAT | Center Y for radial/conical | 0.5 | 0.0-1.0 |
| `gradient_radius` | FLOAT | Radius for radial gradients | 0.7 | 0.0-2.0 |

## Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `gradient_overlay_image` | IMAGE | Image with gradient overlay applied |

## Gradient Types and Personalization

### 1. Linear Gradients

#### Orientation Options
```python
orientation = "top"     # Top to bottom
orientation = "bottom"  # Bottom to top  
orientation = "left"    # Left to right
orientation = "right"   # Right to left
```

#### Position Control
```python
start_position = 0.0    # Where gradient starts (0.0 = start of direction)
end_position = 1.0      # Where gradient ends (1.0 = end of direction)
```

**Use Cases:**
- **start_position = 0.0, end_position = 0.5**: Gradient covers first half
- **start_position = 0.3, end_position = 0.8**: Gradient in middle section
- **start_position = 0.5, end_position = 1.0**: Gradient covers second half

#### Opacity Control
```python
start_opacity = 0.0     # Transparent at start
end_opacity = 0.7      # 70% opacity at end
```

**Use Cases:**
- **Fade in**: start_opacity = 0.0, end_opacity = 1.0
- **Fade out**: start_opacity = 1.0, end_opacity = 0.0
- **Partial overlay**: start_opacity = 0.0, end_opacity = 0.5

### 2. Radial Gradients

#### Center Positioning
```python
gradient_center_x = 0.5  # Center horizontally (0.0 = left, 1.0 = right)
gradient_center_y = 0.5  # Center vertically (0.0 = top, 1.0 = bottom)
```

**Use Cases:**
- **Center focus**: (0.5, 0.5) - Standard center
- **Corner focus**: (0.0, 0.0) - Top-left corner
- **Side focus**: (0.5, 0.0) - Top center

#### Radius Control
```python
gradient_radius = 0.7   # 70% of image size
```

**Use Cases:**
- **Small focus**: radius = 0.3 - Tight center focus
- **Medium focus**: radius = 0.7 - Balanced coverage
- **Large focus**: radius = 1.2 - Wide coverage

### 3. Conical Gradients

#### Angular Effects
```python
gradient_center_x = 0.5  # Rotation center X
gradient_center_y = 0.5  # Rotation center Y
```

**Use Cases:**
- **Clock effects**: Center rotation for time-based visuals
- **Radial patterns**: Angular color transitions
- **Special effects**: Unique visual treatments

## Blending Modes and Personalization

### 1. Normal Blending
```python
blend_mode = "normal"
```
- **Effect**: Standard alpha blending
- **Use Case**: Standard overlays, transparency effects
- **Formula**: `result = base * (1 - alpha) + overlay * alpha`

### 2. Multiply Blending
```python
blend_mode = "multiply"
```
- **Effect**: Darkens the background
- **Use Case**: Shadow effects, darkening overlays
- **Formula**: `result = base * overlay`

### 3. Screen Blending
```python
blend_mode = "screen"
```
- **Effect**: Lightens the background
- **Use Case**: Light effects, brightening overlays
- **Formula**: `result = 1 - (1 - base) * (1 - overlay)`

### 4. Overlay Blending
```python
blend_mode = "overlay"
```
- **Effect**: Increases contrast
- **Use Case**: Dramatic effects, high contrast
- **Formula**: Combines multiply and screen based on base values

### 5. Soft Light Blending
```python
blend_mode = "soft_light"
```
- **Effect**: Subtle contrast adjustment
- **Use Case**: Gentle enhancement, subtle effects
- **Formula**: Soft version of overlay blending

### 6. Hard Light Blending
```python
blend_mode = "hard_light"
```
- **Effect**: Strong contrast adjustment
- **Use Case**: Dramatic effects, strong enhancement
- **Formula**: Hard version of overlay blending

## Color Customization

### Hex Color Support
```python
hex_color = "#FF0000"    # Red
hex_color = "#00FF00"    # Green
hex_color = "#0000FF"    # Blue
hex_color = "#FF6B35"    # Orange
hex_color = "#0066CC"    # Blue (default)
```

### Color Validation
- **Format Support**: #RRGGBB, RRGGBB, #RRGGBBAA
- **Validation**: Automatic hex format validation
- **Error Handling**: Graceful fallback for invalid colors
- **Range**: 0-255 for each RGB component

## Usage Examples

### Example 1: Brand Overlay
```python
# Brand color overlay
hex_color = "#1E3A8A"           # Brand blue
gradient_type = "linear"
orientation = "top"
start_position = 0.0
end_position = 0.6
start_opacity = 0.0
end_opacity = 0.3
blend_mode = "normal"
```

### Example 2: Dramatic Effect
```python
# High contrast overlay
hex_color = "#FF0000"           # Red
gradient_type = "radial"
gradient_center_x = 0.5
gradient_center_y = 0.5
gradient_radius = 0.8
start_opacity = 0.0
end_opacity = 0.8
blend_mode = "overlay"
```

### Example 3: Subtle Enhancement
```python
# Gentle enhancement
hex_color = "#FFFFFF"           # White
gradient_type = "linear"
orientation = "top"
start_position = 0.0
end_position = 1.0
start_opacity = 0.0
end_opacity = 0.2
blend_mode = "soft_light"
```

## Workflow Integration

### Basic Workflow
```
Background Image → Gradient Overlay → Final Image
```

### Brand Workflow
```
Background Image → Brand Color Overlay → Logo Overlay → Final Image
```

### Multi-Layer Workflow
```
Background Image → Gradient Overlay 1 → Gradient Overlay 2 → Final Image
```

## Best Practices

### 1. Color Selection
- **Use brand colors** for consistent branding
- **Test color combinations** for visual harmony
- **Consider contrast** for readability
- **Validate hex formats** before use

### 2. Gradient Positioning
- **Start with center positioning** for radial gradients
- **Use position controls** for precise placement
- **Test different orientations** for linear gradients
- **Adjust radius** for coverage control

### 3. Blending Mode Selection
- **Normal**: Standard overlays and transparency
- **Multiply**: Darkening and shadow effects
- **Screen**: Lightening and glow effects
- **Overlay**: Contrast enhancement
- **Soft Light**: Subtle enhancement
- **Hard Light**: Dramatic effects

### 4. Opacity Management
- **Start with low opacity** (0.1-0.3) for subtle effects
- **Use higher opacity** (0.5-0.8) for dramatic effects
- **Test opacity ranges** for optimal results
- **Consider content visibility** when setting opacity

## Troubleshooting

### Common Issues

#### 1. Color Not Appearing
**Symptoms**: Gradient color not visible
**Solutions**:
- Check hex color format (#RRGGBB)
- Verify opacity values (start_opacity, end_opacity)
- Ensure blend_mode is appropriate
- Check gradient positioning

#### 2. Incorrect Positioning
**Symptoms**: Gradient in wrong location
**Solutions**:
- Verify gradient_center_x and gradient_center_y values
- Check orientation for linear gradients
- Adjust start_position and end_position
- Test with different gradient types

#### 3. Blending Issues
**Symptoms**: Unexpected blending results
**Solutions**:
- Try different blend_mode options
- Adjust opacity values
- Check color contrast
- Test with different background images

### Debug Tips
1. **Start with normal blending** to verify basic functionality
2. **Use high opacity** (0.8-1.0) to see gradient clearly
3. **Test with simple colors** (#FF0000, #00FF00, #0000FF)
4. **Check console output** for error messages

## Advanced Features

### 1. Position Interpolation
- **Smooth transitions** between start and end positions
- **Customizable ranges** for gradient coverage
- **Reversed gradients** when end < start
- **Solid colors** when start = end

### 2. Opacity Interpolation
- **Linear interpolation** between start and end opacity
- **Smooth transitions** for natural effects
- **Customizable ranges** for transparency control
- **Edge case handling** for extreme values

### 3. Mathematical Blending
- **Precise formulas** for each blend mode
- **Proper alpha handling** for transparency
- **Value clamping** to prevent overflow
- **Error handling** for edge cases

## Performance Considerations

### Processing Speed
- **Linear gradients**: Fastest processing
- **Radial gradients**: Medium processing time
- **Conical gradients**: Most complex processing
- **Blend modes**: Vary in computational complexity

### Memory Usage
- **Large images**: May require more memory
- **Multiple overlays**: Cumulative memory usage
- **High resolution**: Consider memory limits
- **Batch processing**: Plan for memory requirements

## Integration Examples

### ComfyUI Workflow
```
Load Image → Gradient Overlay → Logo Overlay → Save Image
```

### Brand Workflow
```
Load Image → Brand Color Overlay → Text Overlay → Final Output
```

### Multi-Effect Workflow
```
Load Image → Gradient 1 → Gradient 2 → Logo Overlay → Final Output
```

## Version History

- **v1.0**: Initial release with basic gradient support
- **v1.1**: Added multiple blend modes
- **v1.2**: Enhanced position control
- **v1.3**: Added radial and conical gradients
- **v1.4**: Improved blending algorithms and error handling

## Support and Resources

### Documentation
- Check console output for error messages
- Verify input parameters and ranges
- Test with simple examples first
- Review blend mode formulas for understanding

### Troubleshooting
- Enable debug logging for detailed information
- Test with different image sizes and formats
- Verify color format and validation
- Check gradient positioning and parameters

### Community
- Share successful gradient combinations
- Report issues with specific blend modes
- Contribute improvements and optimizations
- Document best practices for different use cases

