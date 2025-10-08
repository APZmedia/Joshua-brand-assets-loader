# APZmedia Color Palette Selector Documentation

## Overview

The **APZmedia Color Palette Selector** is a ComfyUI node that provides an intuitive interface for selecting specific colors from brand color palettes. This node simplifies color management in AI workflows by allowing users to easily extract and use brand colors without manual color extraction.

## Node Information

- **Node Name**: `APZmediaColorPaletteSelector`
- **Display Name**: "APZmedia - Color Palette Selector"
- **Category**: `apzmedia_brand`
- **Function**: `select_color`

## Inputs

### Required Inputs

| Input Name | Type | Description | Default |
|------------|------|-------------|---------|
| `palette_json` | STRING | JSON string containing the color palette data | - |
| `color_selection` | SELECT | Predefined color selection options | `color_1` |

#### Color Selection Options

The `color_selection` dropdown provides the following options:

- `color_1` - First color in the palette
- `color_2` - Second color in the palette  
- `color_3` - Third color in the palette
- `color_4` - Fourth color in the palette
- `color_5` - Fifth color in the palette
- `color_6` - Sixth color in the palette
- `color_7` - Seventh color in the palette
- `first_color` - Alias for first color
- `second_color` - Alias for second color
- `third_color` - Alias for third color

### Optional Inputs

| Input Name | Type | Description | Default |
|------------|------|-------------|---------|
| `custom_color` | STRING | Custom hex color override (e.g., "#FF0000") | `""` |
| `use_custom` | BOOLEAN | Whether to use custom color instead of palette | `False` |

## Outputs

| Output Name | Type | Description |
|-------------|------|-------------|
| `color_hex` | STRING | Selected color in hex format (e.g., "#FF0000") |
| `color_name` | STRING | Human-readable color name |
| `color_info` | STRING | Detailed color information string |
| `color_palette_json` | STRING | Original palette JSON for reference |

## Color Palette JSON Format

The node expects color palette data in JSON format. Supported formats:

### Format 1: Array of Color Objects
```json
[
  {
    "name": "Primary Blue",
    "id": "primary",
    "hex": "#1E3A8A"
  },
  {
    "name": "Secondary Green", 
    "id": "secondary",
    "hex": "#059669"
  },
  {
    "name": "Accent Orange",
    "id": "accent", 
    "hex": "#EA580C"
  }
]
```

### Format 2: Object with Colors Array
```json
{
  "colors": [
    {
      "name": "Brand Primary",
      "hex": "#FF6B35"
    },
    {
      "name": "Brand Secondary", 
      "hex": "#004E89"
    }
  ]
}
```

## Features

### Smart Color Matching
- **Position-based selection**: Select colors by position (1st, 2nd, 3rd, etc.)
- **Name-based matching**: Automatically matches colors by name patterns
- **ID-based matching**: Matches colors by their ID field
- **Fallback handling**: Graceful fallback when specific colors aren't found

### Color Validation
- **Hex format validation**: Ensures valid hex color format (#RRGGBB or RRGGBB)
- **File existence checks**: Validates that color files exist
- **Format support**: Supports 3-digit (#RGB) and 6-digit (#RRGGBB) hex formats

### Custom Color Override
- **Custom color input**: Override palette colors with custom hex values
- **Validation**: Ensures custom colors are valid hex format
- **Fallback**: Returns to palette colors if custom color is invalid

## Usage Examples

### Basic Color Selection
```python
# Connect palette JSON from brand asset loader
# Select "color_1" from dropdown
# Output: color_hex = "#1E3A8A", color_name = "Primary Blue"
```

### Custom Color Override
```python
# Set use_custom = True
# Set custom_color = "#FF0000" 
# Output: color_hex = "#FF0000", color_name = "Red"
```

### Workflow Integration
1. Connect `APZmediaBrandAssetLoader` output to `palette_json` input
2. Select desired color from `color_selection` dropdown
3. Use `color_hex` output in other nodes (text nodes, overlay nodes, etc.)
4. Use `color_info` for debugging and verification

## Error Handling

The node includes comprehensive error handling:

- **Invalid JSON**: Returns default color with error message
- **Missing colors**: Falls back to available colors or returns error
- **Invalid hex**: Validates hex format and provides feedback
- **Empty palette**: Returns appropriate error messages

## Color Name Generation

The node automatically generates human-readable color names:

- **Exact matches**: Recognizes common colors (Red, Blue, Green, etc.)
- **Pattern matching**: Identifies color families (Red-ish, Blue-ish, etc.)
- **Fallback naming**: Uses hex code as name when no pattern matches

## Integration with Other Nodes

### Common Workflows
- **Text nodes**: Use `color_hex` for text color
- **Overlay nodes**: Use `color_hex` for overlay colors
- **Logo placement**: Use brand colors for logo backgrounds
- **Gradient generation**: Use multiple colors for gradient creation

### Output Chaining
- Connect `color_hex` to any node accepting color input
- Use `color_info` for debugging and verification
- Pass `color_palette_json` to other color selector nodes

## Performance Considerations

- **Lightweight processing**: Minimal computational overhead
- **Caching**: Efficient color lookup and validation
- **Memory efficient**: Processes JSON in-place without large data structures

## Troubleshooting

### Common Issues

1. **"No color found" error**
   - Check that palette JSON is valid
   - Verify color selection matches available colors
   - Ensure JSON structure matches expected format

2. **"Invalid color hex" error**
   - Verify hex format (#RRGGBB or RRGGBB)
   - Check for typos in hex values
   - Ensure colors are valid hexadecimal

3. **Empty color output**
   - Check palette JSON is not empty
   - Verify color selection is valid
   - Check for JSON parsing errors

### Debug Tips
- Use `color_info` output to see detailed selection information
- Check `color_palette_json` to verify input data
- Enable logging to see detailed processing information

## API Reference

### Class: APZmediaColorPaletteSelector

#### Methods

##### `select_color(palette_json, color_selection, custom_color="", use_custom=False)`
Main function for color selection.

**Parameters:**
- `palette_json` (str): JSON string containing color palette
- `color_selection` (str): Selected color key
- `custom_color` (str): Custom color hex override
- `use_custom` (bool): Whether to use custom color

**Returns:**
- Tuple of (color_hex, color_name, color_info, color_palette_json)

#### Private Methods

##### `_get_color_from_palette(palette_json, color_selection)`
Extract color from palette JSON.

##### `_validate_color_hex(color_hex)`
Validate hex color format.

##### `_extract_color_name(color_hex)`
Generate human-readable color name.

##### `_matches_color_type(color_name, color_id, color_selection)`
Match colors by type patterns.

## Version History

- **v1.0**: Initial release with basic color selection
- **v1.1**: Added custom color override functionality
- **v1.2**: Enhanced color name generation and error handling
- **v1.3**: Improved JSON parsing and validation

## Support

For issues, feature requests, or questions:
- Check the troubleshooting section above
- Review the error messages in `color_info` output
- Enable debug logging for detailed processing information
