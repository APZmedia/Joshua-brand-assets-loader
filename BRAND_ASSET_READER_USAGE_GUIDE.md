# Brand Asset Reader Usage Guide

## Overview

The `APZmediaBrandAssetReader` node demonstrates how to read and extract specific fields from the brand asset loader output. This guide provides practical examples and usage patterns.

## Node Features

### Input Parameters

- **brand_assets** (BRAND_ASSETS): Input from Brand Asset Loader node
- **asset_category** (STRING): Category to read from (logo, font, color, metadata, all)
- **specific_asset** (STRING): Specific asset to extract
- **include_debug_info** (BOOLEAN): Whether to include debug information

### Output Parameters

- **asset_value** (STRING): The extracted asset value
- **asset_type** (STRING): Type of asset (image_tensor, font_path, color_palette, etc.)
- **asset_info** (STRING): Descriptive information about the asset
- **debug_info** (STRING): Debug information (if enabled)
- **status** (STRING): Success/Error status

## Usage Examples

### 1. Reading Brand Name

```
Brand Asset Loader → Brand Asset Reader
├── asset_category: "metadata"
├── specific_asset: "brand_name"
└── include_debug_info: False

Output: "My Company", "brand_name", "Brand: My Company", "", "Success"
```

### 2. Reading Font Paths

```
Brand Asset Loader → Brand Asset Reader
├── asset_category: "font"
├── specific_asset: "font_primary"
└── include_debug_info: True

Output: "/path/to/font.ttf", "font_path", "Font: font_primary, Path: /path/to/font.ttf", "Font: font_primary, Path: /path/to/font.ttf, Size: 12345 bytes", "Success"
```

### 3. Reading Color Palette

```
Brand Asset Loader → Brand Asset Reader
├── asset_category: "color"
├── specific_asset: "color_palette"
└── include_debug_info: False

Output: '{"colors": [...]}', "color_palette", "Color palette: 5 colors", "", "Success"
```

### 4. Reading Logo Information

```
Brand Asset Loader → Brand Asset Reader
├── asset_category: "logo"
├── specific_asset: "logo_vertical_color"
└── include_debug_info: True

Output: "Logo available: (1, 256, 256, 3)", "image_tensor", "Logo: logo_vertical_color, Shape: (1, 256, 256, 3), Mask: Available", "Logo: logo_vertical_color, Shape: (1, 256, 256, 3)", "Success"
```

### 5. Getting Asset Summary

```
Brand Asset Loader → Brand Asset Reader
├── asset_category: "all"
├── specific_asset: "brand_name"
└── include_debug_info: True

Output: "Logos: 5, Fonts: 9, Colors: True", "summary", "Assets: 5 logos, 9 fonts, Colors: Yes", "Brand: My Company | Status: Successfully loaded | Logos: 5/5 available | Fonts: 9/9 available | Colors: Available", "Success"
```

## Common Workflow Patterns

### Pattern 1: Font Selection Workflow

```
Brand Asset Loader → Brand Asset Reader → Font Selector
├── asset_category: "font"
├── specific_asset: "font_primary"
└── output: font_path → Font Selector input
```

### Pattern 2: Logo Processing Workflow

```
Brand Asset Loader → Brand Asset Reader → Logo Processing Node
├── asset_category: "logo"
├── specific_asset: "logo_vertical_color"
└── output: asset_info → Logo Processing Node
```

### Pattern 3: Color Processing Workflow

```
Brand Asset Loader → Brand Asset Reader → Color Processing Node
├── asset_category: "color"
├── specific_asset: "color_palette"
└── output: asset_value → Color Processing Node
```

### Pattern 4: Debug and Monitoring Workflow

```
Brand Asset Loader → Brand Asset Reader → Display Node
├── asset_category: "all"
├── specific_asset: "brand_name"
├── include_debug_info: True
└── output: debug_info → Display Node
```

## Error Handling Examples

### Missing Asset

```
Input: asset_category: "font", specific_asset: "font_primary"
Output: "", "error", "Font not found: font_primary", "", "Error"
```

### Invalid Brand Assets

```
Input: brand_assets: None
Output: "", "error", "Invalid brand assets input", "", "Error"
```

### Asset Loading Failed

```
Input: brand_assets with status_message: "Error: Failed to load assets"
Output: "", "error", "Asset loading failed: Error: Failed to load assets", "", "Error"
```

## Advanced Usage

### Custom Node Integration

```python
# In your custom node
def process_brand_assets(self, brand_assets):
    # Check if assets are loaded successfully
    status = brand_assets.get("status_message", "")
    if "Error" in status:
        return self.handle_error(status)
    
    # Extract specific assets
    logo = brand_assets.get("logo_vertical_color")
    font_path = brand_assets.get("font_primary", "")
    color_palette = brand_assets.get("color_palette", "[]")
    
    # Process assets
    if logo is not None:
        processed_logo = self.process_logo(logo)
    
    if font_path:
        font_info = self.load_font(font_path)
    
    try:
        colors = json.loads(color_palette)
        processed_colors = self.process_colors(colors)
    except json.JSONDecodeError:
        processed_colors = []
    
    return processed_logo, font_info, processed_colors
```

### Batch Asset Processing

```python
# Process multiple assets
def process_all_assets(self, brand_assets):
    results = {}
    
    # Process logos
    logo_keys = ["logo_vertical_color", "logo_horizontal_color", "logo_icon"]
    for key in logo_keys:
        logo = brand_assets.get(key)
        if logo is not None:
            results[key] = self.process_logo(logo)
    
    # Process fonts
    font_keys = ["font_primary", "font_secondary", "font_tertiary"]
    for key in font_keys:
        font_path = brand_assets.get(key, "")
        if font_path:
            results[key] = self.load_font(font_path)
    
    return results
```

## Best Practices

### 1. Always Check Status
```python
status = brand_assets.get("status_message", "")
if "Error" in status or "Failed" in status:
    # Handle error appropriately
    return
```

### 2. Validate Asset Existence
```python
logo = brand_assets.get("logo_vertical_color")
if logo is not None:
    # Process logo
    pass
```

### 3. Use Fallback Values
```python
font_path = brand_assets.get("font_primary", "")
if not font_path:
    font_path = brand_assets.get("font_secondary", "")
```

### 4. Handle JSON Parsing
```python
try:
    colors = json.loads(color_palette_json)
except json.JSONDecodeError:
    colors = []
```

### 5. Provide Meaningful Error Messages
```python
if not asset_value:
    return self.return_error(f"Asset not found: {asset_name}")
```

## Troubleshooting

### Common Issues

1. **Empty Assets**: Check if brand assets were loaded successfully
2. **Invalid Paths**: Verify font file paths exist
3. **JSON Errors**: Validate color palette JSON format
4. **Tensor Issues**: Ensure logo tensors are in correct format

### Debug Information

Enable `include_debug_info` to get detailed information about:
- Asset availability
- File paths and sizes
- Tensor shapes
- Error details

### Monitoring

Use the "all" category to monitor overall asset status:
- Total number of available assets
- Asset loading status
- Error information

## Conclusion

The Brand Asset Reader node provides a flexible way to extract and use specific fields from the brand asset loader output. Use it to:

- Extract specific assets for processing
- Monitor asset availability
- Debug asset loading issues
- Create custom workflows with brand assets

Choose the appropriate asset category and specific asset based on your workflow needs.
