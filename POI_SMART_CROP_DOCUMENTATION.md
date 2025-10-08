# POI Smart Crop Node Documentation

## Overview

The **POI Smart Crop** node is an advanced image cropping tool that uses intelligent saliency detection to automatically identify and preserve the most important visual elements (Points of Interest) in your images. This node is perfect for creating consistent, well-composed crops that maintain visual impact.

## Node Information

- **Node Name**: `POISmartCrop`
- **Display Name**: "POI Smart Crop (Enhanced)"
- **Category**: `image/transform`
- **Function**: `run`

## Key Features

### Intelligent Saliency Detection
- **Spectral Residual Analysis**: Uses advanced FFT-based saliency detection
- **Multi-blob Detection**: Identifies multiple points of interest
- **Adaptive Thresholding**: Automatically adjusts to image content
- **Weighted Centroid Calculation**: Combines multiple POIs intelligently

### Advanced Cropping Options
- **Aspect Ratio Control**: Maintain target aspect ratios
- **Centering Preferences**: Left, center, or right alignment
- **Padding Control**: Adjustable padding around POI
- **Multiple Resize Methods**: Fill/crop or fit scaling

### Personalization Features
- **POI Size Control**: Adjust focus area size
- **GrabCut Refinement**: Optional OpenCV-based refinement
- **Debug Overlays**: Visual feedback for POI detection
- **Fallback Options**: Graceful handling of edge cases

## Inputs

### Required Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `images` | IMAGE | Input image(s) to crop | - | - |
| `width` | INT | Target crop width | 1080 | 1-8192 |
| `height` | INT | Target crop height | 1350 | 1-8192 |
| `interpolation` | SELECT | Resize interpolation method | `lanczos` | lanczos, bicubic, bilinear, nearest |
| `method` | SELECT | Resize method | `fill / crop` | fill / crop, fit |
| `condition` | SELECT | When to apply cropping | `always` | always, if_larger, if_smaller |
| `multiple_of` | INT | Constrain dimensions to multiples | 0 | 0-64 |
| `centering_preference` | SELECT | POI alignment preference | `center` | left, center, right |
| `padding` | FLOAT | Padding around POI | 0.12 | 0.0-0.75 |

### Optional Inputs

| Input Name | Type | Description | Default | Range |
|------------|------|-------------|---------|-------|
| `poi_size_percent` | FLOAT | POI focus area size | 10.0 | 1.0-50.0 |
| `refine_with_grabcut` | BOOLEAN | Use OpenCV GrabCut refinement | False | - |
| `fallback_center_crop` | BOOLEAN | Fallback to center crop | True | - |
| `show_overlay` | BOOLEAN | Show debug overlays | False | - |

## Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `cropped` | IMAGE | Cropped image(s) |
| `box_xyxy` | BOX | Crop box coordinates (x0, y0, x1, y1) |
| `saliency_map` | IMAGE | Visual saliency map for debugging |

## Personalization Options

### 1. POI Detection Customization

#### POI Size Control
```python
# Adjust focus area size
poi_size_percent = 15.0  # 15% of image size
```

**Use Cases:**
- **Small values (5-10%)**: Focus on specific objects
- **Medium values (10-20%)**: Balanced composition
- **Large values (20-50%)**: Include more context

#### Saliency Detection Methods
The node uses multiple detection methods:

1. **Spectral Residual**: Primary method using FFT analysis
2. **Adaptive Thresholding**: Otsu, percentile, or adaptive
3. **Blob Detection**: Connected component analysis
4. **Weighted Selection**: Combines multiple POIs

### 2. Cropping Behavior Customization

#### Centering Preferences
```python
centering_preference = "left"    # Move POI to left side
centering_preference = "center"  # Keep POI centered
centering_preference = "right"   # Move POI to right side
```

**Use Cases:**
- **Left**: Text-heavy images, logos on left
- **Center**: Balanced compositions
- **Right**: Asymmetric designs, call-to-action elements

#### Padding Control
```python
padding = 0.12  # 12% padding around POI
```

**Use Cases:**
- **Low padding (0.05-0.10)**: Tight crops, focus on subject
- **Medium padding (0.10-0.20)**: Balanced composition
- **High padding (0.20-0.50)**: Include more context

### 3. Resize Method Customization

#### Fill/Crop Method
```python
method = "fill / crop"
```
- Scales image to fill target dimensions
- May crop parts of the image
- Maintains aspect ratio
- Best for: Social media posts, thumbnails

#### Fit Method
```python
method = "fit"
```
- Scales image to fit within target dimensions
- May add letterboxing/pillarboxing
- Maintains aspect ratio
- Best for: Presentations, documents

### 4. Advanced Refinement Options

#### GrabCut Refinement
```python
refine_with_grabcut = True
```
- Uses OpenCV GrabCut for precise segmentation
- Requires OpenCV installation
- Better for complex backgrounds
- Slower processing

#### Debug Overlays
```python
show_overlay = True
```
- Shows detected POI points
- Displays crop boundaries
- Visual feedback for tuning
- Red: Original POI, Blue: Adjusted POI, Green: Final crop

## Usage Examples

### Example 1: Social Media Post
```python
# Settings for Instagram post
width = 1080
height = 1080
centering_preference = "center"
padding = 0.15
poi_size_percent = 12.0
method = "fill / crop"
```

### Example 2: Product Thumbnail
```python
# Settings for e-commerce thumbnail
width = 300
height = 300
centering_preference = "center"
padding = 0.08
poi_size_percent = 8.0
method = "fill / crop"
```

### Example 3: Presentation Slide
```python
# Settings for presentation
width = 1920
height = 1080
centering_preference = "left"
padding = 0.20
poi_size_percent = 15.0
method = "fit"
```

## Workflow Integration

### Basic Workflow
```
Input Image → POI Smart Crop → Output Image
```

### Advanced Workflow
```
Input Image → POI Smart Crop → Logo Overlay → Final Output
```

### Batch Processing
```
Multiple Images → POI Smart Crop → Consistent Crops
```

## Best Practices

### 1. POI Detection Tuning
- **Start with default settings** and adjust based on results
- **Use debug overlays** to understand POI detection
- **Adjust poi_size_percent** for different content types
- **Test with various image types** to find optimal settings

### 2. Cropping Strategy
- **Choose appropriate centering** based on design needs
- **Adjust padding** for composition balance
- **Select resize method** based on output requirements
- **Use condition settings** to avoid unnecessary processing

### 3. Performance Optimization
- **Disable GrabCut** for faster processing
- **Use appropriate interpolation** (lanczos for quality, nearest for speed)
- **Set multiple_of** to optimize for target platform
- **Batch process** similar images together

## Troubleshooting

### Common Issues

#### 1. Poor POI Detection
**Symptoms**: Crops miss important elements
**Solutions**:
- Increase `poi_size_percent` for broader focus
- Enable `refine_with_grabcut` for better segmentation
- Use `show_overlay` to debug detection
- Adjust `padding` to include more context

#### 2. Incorrect Centering
**Symptoms**: POI not positioned as expected
**Solutions**:
- Check `centering_preference` setting
- Verify `offset_x` and `offset_y` values
- Use debug overlays to visualize positioning
- Adjust `padding` for fine-tuning

#### 3. Aspect Ratio Issues
**Symptoms**: Distorted or unexpected crop shapes
**Solutions**:
- Verify target `width` and `height` values
- Check `method` setting (fill/crop vs fit)
- Ensure `multiple_of` constraints are appropriate
- Test with different `interpolation` methods

### Debug Tips
1. **Enable show_overlay** to visualize POI detection
2. **Check saliency_map output** for detection quality
3. **Use box_xyxy output** to verify crop coordinates
4. **Test with different images** to validate settings

## Advanced Features

### 1. Multi-POI Detection
The node can detect and combine multiple points of interest:
- **Saliency-based selection**: Chooses most salient regions
- **Area-based selection**: Prioritizes larger regions
- **Combined scoring**: Balances saliency and area
- **Weighted averaging**: Combines multiple POIs intelligently

### 2. Adaptive Thresholding
- **Otsu's method**: Automatic threshold selection
- **Percentile-based**: Top N% of saliency values
- **Adaptive**: Based on local statistics
- **Fallback handling**: Graceful degradation

### 3. Blob Analysis
- **Connected components**: Identifies distinct regions
- **Area filtering**: Removes small noise
- **Centroid calculation**: Finds region centers
- **Bounding box extraction**: Defines region boundaries

## Performance Considerations

### Processing Speed
- **Basic mode**: Fast processing, good results
- **GrabCut mode**: Slower but more accurate
- **Debug mode**: Additional overhead for visualization
- **Batch processing**: Efficient for multiple images

### Memory Usage
- **Large images**: May require more memory
- **Batch processing**: Consider memory limits
- **Debug overlays**: Additional memory overhead
- **Saliency maps**: Stored for visualization

## Integration Examples

### ComfyUI Workflow
```
Load Image → POI Smart Crop → Logo Overlay → Save Image
```

### Batch Processing
```
Load Images → POI Smart Crop → Apply Effects → Save All
```

### Dynamic Sizing
```
Load Image → POI Smart Crop → Resize → Final Output
```

## Version History

- **v1.0**: Initial release with basic POI detection
- **v1.1**: Added GrabCut refinement
- **v1.2**: Enhanced saliency detection
- **v1.3**: Added debug overlays and improved centering
- **v1.4**: Multi-POI detection and weighted averaging

## Support and Resources

### Documentation
- Check debug overlays for visual feedback
- Use saliency_map output for detection analysis
- Review box_xyxy coordinates for positioning
- Test with various image types for optimization

### Troubleshooting
- Enable debug mode for visual feedback
- Check console output for error messages
- Verify input image format and dimensions
- Test with simpler images first

### Community
- Share successful parameter combinations
- Report issues with specific image types
- Contribute improvements and optimizations
- Document best practices for different use cases

