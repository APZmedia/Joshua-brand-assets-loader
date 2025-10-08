# POI, Color Overlay, and Logo Nodes - Usage Workflow Guide

## Overview

This comprehensive guide demonstrates how to use the POI Smart Crop, Gradient Overlay, and Logo nodes together to create professional, brand-consistent designs. These nodes work synergistically to provide complete control over image composition, branding, and visual effects.

## Workflow Architecture

### Core Workflow Pattern
```
Input Image → POI Smart Crop → Gradient Overlay → Logo Overlay → Final Output
```

### Extended Workflow Pattern
```
Input Image → POI Smart Crop → Gradient Overlay → Logo Overlay → Text Overlay → Final Output
```

## Node Integration Guide

### 1. POI Smart Crop Integration

#### Purpose
- **Intelligent cropping** based on visual importance
- **Consistent composition** across different images
- **Aspect ratio control** for target platforms
- **Content preservation** of key visual elements

#### Personalization Options
```python
# Basic POI settings
width = 1080
height = 1080
centering_preference = "center"
padding = 0.12
poi_size_percent = 10.0
method = "fill / crop"
```

#### Use Cases
- **Social media posts**: Consistent 1:1 aspect ratio
- **Website headers**: Maintain visual focus
- **Product images**: Highlight key features
- **Portrait crops**: Focus on subjects

### 2. Gradient Overlay Integration

#### Purpose
- **Brand color application** for consistent branding
- **Visual enhancement** and mood setting
- **Background modification** for better text readability
- **Creative effects** and artistic expression

#### Personalization Options
```python
# Brand gradient settings
hex_color = "#1E3A8A"  # Brand primary color
gradient_type = "linear"
orientation = "top"
start_position = 0.0
end_position = 0.6
start_opacity = 0.0
end_opacity = 0.3
blend_mode = "normal"
```

#### Use Cases
- **Brand overlays**: Apply brand colors consistently
- **Text readability**: Darken/lighten backgrounds
- **Mood setting**: Create specific atmospheres
- **Visual hierarchy**: Guide viewer attention

### 3. Logo Overlay Integration

#### Purpose
- **Brand placement** for consistent branding
- **Professional appearance** with proper positioning
- **Brand recognition** through logo visibility
- **Design completion** with final branding elements

#### Personalization Options
```python
# Logo placement settings
logo_selection = "vertical_color"
logo_type = "auto"
position = "bottom-right"
scale_percentage = 12.0
padding_percentage = 5.0
rotation_degrees = 0.0
opacity = 1.0
blend_mode = "normal"
```

#### Use Cases
- **Brand watermarks**: Subtle brand presence
- **Prominent branding**: Main brand placement
- **Creative placement**: Artistic logo positioning
- **Multi-logo designs**: Multiple brand elements

## Complete Workflow Examples

### Example 1: Social Media Post

#### Workflow
```
Input Image → POI Smart Crop → Brand Gradient → Logo Overlay → Social Media Post
```

#### Node Configuration
```python
# POI Smart Crop
width = 1080
height = 1080
centering_preference = "center"
padding = 0.15
poi_size_percent = 12.0
method = "fill / crop"

# Gradient Overlay
hex_color = "#1E3A8A"  # Brand blue
gradient_type = "linear"
orientation = "top"
start_position = 0.0
end_position = 0.5
start_opacity = 0.0
end_opacity = 0.4
blend_mode = "normal"

# Logo Overlay
logo_selection = "vertical_color"
position = "bottom-right"
scale_percentage = 10.0
padding_percentage = 5.0
opacity = 1.0
```

#### Result
- **Consistent composition** with POI-based cropping
- **Brand color overlay** for visual consistency
- **Professional logo placement** for brand recognition
- **Social media optimized** dimensions and composition

### Example 2: Website Header

#### Workflow
```
Input Image → POI Smart Crop → Gradient Overlay → Logo Overlay → Website Header
```

#### Node Configuration
```python
# POI Smart Crop
width = 1920
height = 600
centering_preference = "left"
padding = 0.20
poi_size_percent = 15.0
method = "fill / crop"

# Gradient Overlay
hex_color = "#000000"  # Black overlay
gradient_type = "linear"
orientation = "left"
start_position = 0.0
end_position = 0.7
start_opacity = 0.0
end_opacity = 0.6
blend_mode = "multiply"

# Logo Overlay
logo_selection = "horizontal_color"
position = "top-left"
scale_percentage = 15.0
padding_percentage = 8.0
opacity = 1.0
```

#### Result
- **Wide format** suitable for website headers
- **Left-aligned composition** for text overlay space
- **Dark overlay** for text readability
- **Horizontal logo** for header branding

### Example 3: Product Showcase

#### Workflow
```
Input Image → POI Smart Crop → Brand Gradient → Logo Overlay → Product Image
```

#### Node Configuration
```python
# POI Smart Crop
width = 800
height = 800
centering_preference = "center"
padding = 0.10
poi_size_percent = 8.0
method = "fill / crop"

# Gradient Overlay
hex_color = "#FF6B35"  # Brand accent color
gradient_type = "radial"
gradient_center_x = 0.5
gradient_center_y = 0.5
gradient_radius = 0.8
start_opacity = 0.0
end_opacity = 0.2
blend_mode = "soft_light"

# Logo Overlay
logo_selection = "icon"
position = "bottom-right"
scale_percentage = 8.0
padding_percentage = 3.0
opacity = 0.8
```

#### Result
- **Square format** for product images
- **Centered composition** highlighting product
- **Subtle brand accent** for visual enhancement
- **Small logo** for brand presence without distraction

## Advanced Workflow Patterns

### Pattern 1: Multi-Brand Campaign

#### Workflow
```
Input Image → POI Smart Crop → Brand Gradient → Primary Logo → Secondary Logo → Final Output
```

#### Configuration
```python
# POI Smart Crop (same for all)
width = 1080
height = 1350
centering_preference = "center"
padding = 0.12

# Brand Gradient
hex_color = "#1E3A8A"  # Primary brand color
gradient_type = "linear"
orientation = "top"
start_opacity = 0.0
end_opacity = 0.3

# Primary Logo
logo_selection = "vertical_color"
position = "bottom-right"
scale_percentage = 12.0
opacity = 1.0

# Secondary Logo (different node)
logo_selection = "icon"
position = "top-left"
scale_percentage = 6.0
opacity = 0.7
```

### Pattern 2: Seasonal Variations

#### Workflow
```
Input Image → POI Smart Crop → Seasonal Gradient → Logo Overlay → Seasonal Output
```

#### Configuration
```python
# POI Smart Crop (consistent)
width = 1080
height = 1080
centering_preference = "center"

# Seasonal Gradient (varies by season)
# Spring
hex_color = "#4CAF50"  # Green
gradient_type = "radial"
start_opacity = 0.0
end_opacity = 0.2

# Summer
hex_color = "#FF9800"  # Orange
gradient_type = "linear"
orientation = "top"
start_opacity = 0.0
end_opacity = 0.3

# Fall
hex_color = "#8D6E63"  # Brown
gradient_type = "linear"
orientation = "bottom"
start_opacity = 0.0
end_opacity = 0.4

# Winter
hex_color = "#2196F3"  # Blue
gradient_type = "radial"
start_opacity = 0.0
end_opacity = 0.2
```

### Pattern 3: Platform-Specific Optimization

#### Workflow
```
Input Image → POI Smart Crop → Platform Gradient → Logo Overlay → Platform Output
```

#### Configuration
```python
# Instagram (1:1)
width = 1080
height = 1080
centering_preference = "center"
padding = 0.15

# Facebook (1.91:1)
width = 1200
height = 630
centering_preference = "center"
padding = 0.12

# Twitter (16:9)
width = 1200
height = 675
centering_preference = "center"
padding = 0.10

# LinkedIn (1.91:1)
width = 1200
height = 627
centering_preference = "left"
padding = 0.15
```

## Best Practices for Workflow Design

### 1. Node Order Optimization
- **POI Smart Crop first**: Establish composition
- **Gradient Overlay second**: Apply brand colors
- **Logo Overlay last**: Add final branding
- **Text Overlay final**: Complete design

### 2. Parameter Consistency
- **Use brand guidelines**: Consistent colors and positioning
- **Maintain proportions**: Scale logos appropriately
- **Test variations**: Try different combinations
- **Document settings**: Save successful configurations

### 3. Quality Assurance
- **Test with different images**: Ensure robustness
- **Verify brand compliance**: Check against guidelines
- **Optimize for platforms**: Consider target audiences
- **Review final output**: Quality check before delivery

### 4. Performance Optimization
- **Batch processing**: Process multiple images together
- **Reuse settings**: Save successful configurations
- **Optimize parameters**: Use minimal necessary settings
- **Monitor memory**: Watch for resource usage

## Troubleshooting Workflows

### Common Issues

#### 1. Composition Problems
**Symptoms**: Poor cropping, misaligned elements
**Solutions**:
- Adjust POI Smart Crop parameters
- Check centering preferences
- Verify aspect ratios
- Test with different images

#### 2. Brand Consistency Issues
**Symptoms**: Inconsistent colors, logo placement
**Solutions**:
- Use brand asset loader for colors
- Standardize logo selection
- Check gradient settings
- Verify brand guidelines

#### 3. Performance Issues
**Symptoms**: Slow processing, memory errors
**Solutions**:
- Optimize image sizes
- Reduce batch sizes
- Check memory usage
- Use appropriate interpolation

### Debug Strategies
1. **Test individual nodes** before combining
2. **Use debug overlays** for POI detection
3. **Check console output** for errors
4. **Verify input formats** and dimensions

## Workflow Templates

### Template 1: Standard Brand Post
```python
# POI Smart Crop
width = 1080
height = 1080
centering_preference = "center"
padding = 0.12

# Gradient Overlay
hex_color = "#1E3A8A"  # Brand primary
gradient_type = "linear"
orientation = "top"
start_opacity = 0.0
end_opacity = 0.3

# Logo Overlay
logo_selection = "vertical_color"
position = "bottom-right"
scale_percentage = 12.0
opacity = 1.0
```

### Template 2: Watermark Effect
```python
# POI Smart Crop
width = 1080
height = 1080
centering_preference = "center"
padding = 0.10

# Gradient Overlay
hex_color = "#000000"  # Black overlay
gradient_type = "radial"
start_opacity = 0.0
end_opacity = 0.2

# Logo Overlay
logo_selection = "icon"
position = "center"
scale_percentage = 20.0
opacity = 0.3
```

### Template 3: Creative Design
```python
# POI Smart Crop
width = 1080
height = 1350
centering_preference = "left"
padding = 0.15

# Gradient Overlay
hex_color = "#FF6B35"  # Brand accent
gradient_type = "conical"
start_opacity = 0.0
end_opacity = 0.4

# Logo Overlay
logo_selection = "horizontal_color"
position = "top-left"
scale_percentage = 15.0
rotation_degrees = 15.0
opacity = 0.9
```

## Integration with Other Nodes

### ComfyUI Ecosystem
- **Text nodes**: Add text overlays after logo placement
- **Effect nodes**: Apply filters and effects
- **Save nodes**: Export final results
- **Batch processing**: Handle multiple images

### External Tools
- **Brand asset management**: Integrate with brand systems
- **Content management**: Connect to CMS platforms
- **Social media**: Direct publishing capabilities
- **Analytics**: Track performance and engagement

## Version History and Updates

### Recent Updates
- **Enhanced POI detection**: Improved saliency analysis
- **Better gradient blending**: More accurate color mixing
- **Logo positioning**: Enhanced placement algorithms
- **Performance optimization**: Faster processing

### Future Enhancements
- **AI-powered composition**: Automatic layout suggestions
- **Brand compliance**: Automated guideline checking
- **Template system**: Pre-built workflow templates
- **Cloud integration**: Remote asset management

## Support and Resources

### Documentation
- **Individual node guides**: Detailed parameter documentation
- **Workflow examples**: Step-by-step tutorials
- **Best practices**: Optimization recommendations
- **Troubleshooting**: Common issues and solutions

### Community
- **Workflow sharing**: Exchange successful configurations
- **Issue reporting**: Report bugs and request features
- **Contribution**: Help improve documentation and examples
- **Feedback**: Share experiences and suggestions

### Training
- **Video tutorials**: Visual learning resources
- **Workshop materials**: Hands-on training guides
- **Certification**: Professional training programs
- **Support forums**: Community help and discussion

