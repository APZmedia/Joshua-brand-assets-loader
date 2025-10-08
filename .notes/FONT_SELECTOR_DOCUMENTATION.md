# APZmedia Font Selector Documentation

## Overview

The **APZmedia Font Selector** is a ComfyUI node that provides an intuitive interface for selecting and managing fonts from brand assets. This node simplifies font management in AI workflows by allowing users to easily extract and use brand fonts without manual font path management.

## Node Information

- **Node Name**: `APZmediaFontSelector`
- **Display Name**: "APZmedia - Font Selector"
- **Category**: `apzmedia_brand`
- **Function**: `select_font`

## Inputs

### Required Inputs

| Input Name | Type | Description | Default |
|------------|------|-------------|---------|
| `brand_assets` | BRAND_ASSETS | Dictionary containing all brand assets including fonts | - |
| `font_selection` | SELECT | Predefined font selection options | `font_primary` |

#### Font Selection Options

The `font_selection` dropdown provides the following options:

- `font_primary` - Primary brand font
- `font_primary_bold` - Primary font bold variant
- `font_primary_italic` - Primary font italic variant
- `font_secondary` - Secondary brand font
- `font_secondary_bold` - Secondary font bold variant
- `font_secondary_italic` - Secondary font italic variant
- `font_tertiary` - Tertiary brand font
- `font_tertiary_bold` - Tertiary font bold variant
- `font_tertiary_italic` - Tertiary font italic variant

### Optional Inputs

| Input Name | Type | Description | Default |
|------------|------|-------------|---------|
| `custom_font_path` | STRING | Custom font file path override | `""` |
| `use_custom` | BOOLEAN | Whether to use custom font instead of brand assets | `False` |

## Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `font_path` | STRING | Selected font file path |
| `font_name` | STRING | Human-readable font name |
| `font_info` | STRING | Detailed font information string |
| `font_list` | STRING | Formatted list of all available fonts |

## Brand Assets Format

The node expects brand assets in a dictionary format with the following font keys:

```python
brand_assets = {
    "font_primary": "/path/to/primary-font.ttf",
    "font_primary_bold": "/path/to/primary-bold.ttf", 
    "font_primary_italic": "/path/to/primary-italic.ttf",
    "font_secondary": "/path/to/secondary-font.ttf",
    "font_secondary_bold": "/path/to/secondary-bold.ttf",
    "font_secondary_italic": "/path/to/secondary-italic.ttf",
    "font_tertiary": "/path/to/tertiary-font.ttf",
    "font_tertiary_bold": "/path/to/tertiary-bold.ttf",
    "font_tertiary_italic": "/path/to/tertiary-italic.ttf"
}
```

## Features

### Smart Font Selection
- **Hierarchical selection**: Choose from primary, secondary, and tertiary font families
- **Style variants**: Access bold and italic variants for each font family
- **Fallback handling**: Graceful fallback when specific fonts aren't available
- **Custom override**: Use custom font paths when needed

### Font Validation
- **File existence**: Validates that font files exist on disk
- **Format support**: Supports TTF, OTF, WOFF, and WOFF2 formats
- **File integrity**: Checks file size and basic validity
- **Path validation**: Ensures font paths are accessible

### Font Information
- **Name extraction**: Automatically extracts readable font names from file paths
- **Font listing**: Provides formatted list of all available fonts
- **Debug information**: Detailed font information for troubleshooting

## Supported Font Formats

The node supports the following font formats:

- **TTF** (.ttf) - TrueType fonts
- **OTF** (.otf) - OpenType fonts  
- **WOFF** (.woff) - Web Open Font Format
- **WOFF2** (.woff2) - Web Open Font Format 2

## Usage Examples

### Basic Font Selection
```python
# Connect brand assets from APZmediaBrandAssetLoader
# Select "font_primary" from dropdown
# Output: font_path = "/path/to/primary-font.ttf", font_name = "Primary Font"
```

### Custom Font Override
```python
# Set use_custom = True
# Set custom_font_path = "/path/to/custom-font.ttf"
# Output: font_path = "/path/to/custom-font.ttf", font_name = "Custom Font"
```

### Font Variant Selection
```python
# Select "font_primary_bold" for bold text
# Select "font_secondary_italic" for italic secondary text
# Select "font_tertiary" for tertiary text styling
```

### Workflow Integration
1. Connect `APZmediaBrandAssetLoader` output to `brand_assets` input
2. Select desired font from `font_selection` dropdown
3. Use `font_path` output in text nodes, logo nodes, etc.
4. Use `font_info` for debugging and verification
5. Use `font_list` to see all available fonts

## Error Handling

The node includes comprehensive error handling:

- **Missing fonts**: Returns appropriate error messages when fonts aren't found
- **Invalid paths**: Validates font file paths and accessibility
- **Format errors**: Checks font file format and integrity
- **Custom font validation**: Validates custom font paths and formats

## Font Name Generation

The node automatically generates human-readable font names:

- **Path extraction**: Extracts font name from file path
- **Name cleaning**: Removes underscores, hyphens, and file extensions
- **Capitalization**: Properly capitalizes font names
- **Fallback naming**: Uses "Unknown Font" when name extraction fails

## Integration with Other Nodes

### Common Workflows
- **Text nodes**: Use `font_path` for text rendering
- **Logo nodes**: Use brand fonts for logo text
- **Typography nodes**: Apply consistent font styling
- **Text overlay**: Use fonts for image text overlays

### Output Chaining
- Connect `font_path` to any node accepting font input
- Use `font_info` for debugging and verification
- Use `font_list` to display available fonts to users
- Pass `brand_assets` to other font selector nodes

## Performance Considerations

- **Lightweight processing**: Minimal computational overhead
- **File validation**: Efficient font file checking
- **Memory efficient**: Processes font paths without loading font data
- **Caching**: Efficient font lookup and validation

## Troubleshooting

### Common Issues

1. **"No font found" error**
   - Check that brand assets contain font data
   - Verify font selection matches available fonts
   - Ensure font keys are properly named in brand assets

2. **"Invalid font path" error**
   - Verify font file exists at specified path
   - Check file permissions and accessibility
   - Ensure font format is supported

3. **Empty font output**
   - Check brand assets are not empty
   - Verify font selection is valid
   - Check for file path issues

### Debug Tips
- Use `font_info` output to see detailed selection information
- Use `font_list` to see all available fonts
- Check `brand_assets` input for proper font data
- Enable logging to see detailed processing information

## Font List Output Format

The `font_list` output provides a formatted list of available fonts:

```
Available Fonts:
• Primary: Primary Font Name
• Primary Bold: Primary Bold Font Name
• Primary Italic: Primary Italic Font Name
• Secondary: Secondary Font Name
• Secondary Bold: Secondary Bold Font Name
• Secondary Italic: Secondary Italic Font Name
• Tertiary: Tertiary Font Name
• Tertiary Bold: Tertiary Bold Font Name
• Tertiary Italic: Tertiary Italic Font Name
```

## API Reference

### Class: APZmediaFontSelector

#### Methods

##### `select_font(brand_assets, font_selection, custom_font_path="", use_custom=False)`
Main function for font selection.

**Parameters:**
- `brand_assets` (dict): Dictionary containing brand assets
- `font_selection` (str): Selected font key
- `custom_font_path` (str): Custom font path override
- `use_custom` (bool): Whether to use custom font

**Returns:**
- Tuple of (font_path, font_name, font_info, font_list)

#### Private Methods

##### `_get_font_from_assets(brand_assets, font_selection)`
Extract font path from brand assets dictionary.

##### `_validate_font_path(font_path)`
Validate font file path and format.

##### `_extract_font_name(font_path)`
Generate human-readable font name from path.

##### `_generate_font_list(brand_assets)`
Generate formatted list of available fonts.

##### `_return_default_font(error_message, font_list)`
Return default values when font selection fails.

## Font Hierarchy Best Practices

### Primary Fonts
- Use for main headings and important text
- Should be the most recognizable brand font
- Include bold and italic variants

### Secondary Fonts
- Use for body text and secondary information
- Should complement the primary font
- Include bold and italic variants

### Tertiary Fonts
- Use for captions, footnotes, and less important text
- Should be readable but less prominent
- Include bold and italic variants

## Version History

- **v1.0**: Initial release with basic font selection
- **v1.1**: Added custom font path override functionality
- **v1.2**: Enhanced font name generation and error handling
- **v1.3**: Improved font validation and format support
- **v1.4**: Added font list output and better debugging

## Support

For issues, feature requests, or questions:
- Check the troubleshooting section above
- Review the error messages in `font_info` output
- Use `font_list` to verify available fonts
- Enable debug logging for detailed processing information
