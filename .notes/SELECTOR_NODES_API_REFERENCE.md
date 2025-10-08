# Color and Font Selector Nodes - API Reference

## Overview

This document provides comprehensive API reference for the APZmedia Color Palette Selector and Font Selector nodes, including detailed method signatures, parameters, return values, and implementation details.

## APZmediaColorPaletteSelector

### Class Definition

```python
class APZmediaColorPaletteSelector:
    """Color Palette Selector Node for easy color selection from brand assets."""
```

### Node Configuration

#### INPUT_TYPES
```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "palette_json": ("STRING", {}),
            "color_selection": (["color_1", "color_2", "color_3", "color_4", "color_5", "color_6", "color_7", "first_color", "second_color", "third_color"], {"default": "color_1"}),
        },
        "optional": {
            "custom_color": ("STRING", {
                "default": "",
                "multiline": False
            }),
            "use_custom": ("BOOLEAN", {"default": False}),
        }
    }
```

#### RETURN_TYPES
```python
RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
RETURN_NAMES = ("color_hex", "color_name", "color_info", "color_palette_json")
```

#### Node Metadata
```python
FUNCTION = "select_color"
CATEGORY = "apzmedia_brand"
```

### Public Methods

#### `select_color(palette_json, color_selection, custom_color="", use_custom=False)`

**Description**: Main function for color selection from palette JSON.

**Parameters**:
- `palette_json` (str): JSON string containing color palette data
- `color_selection` (str): Selected color key from predefined options
- `custom_color` (str, optional): Custom hex color override (default: "")
- `use_custom` (bool, optional): Whether to use custom color (default: False)

**Returns**: `Tuple[str, str, str, str]`
- `color_hex` (str): Selected color in hex format (e.g., "#FF0000")
- `color_name` (str): Human-readable color name
- `color_info` (str): Detailed color information string
- `color_palette_json` (str): Original palette JSON for reference

**Raises**: No exceptions (returns error values instead)

**Example**:
```python
selector = APZmediaColorPaletteSelector()
result = selector.select_color(
    palette_json='[{"name": "Red", "hex": "#FF0000"}]',
    color_selection="color_1",
    custom_color="",
    use_custom=False
)
# Returns: ("#FF0000", "Red", "Color 1: Red", '[{"name": "Red", "hex": "#FF0000"}]')
```

### Private Methods

#### `_get_color_from_palette(palette_json: str, color_selection: str) -> str`

**Description**: Extract color from palette JSON string.

**Parameters**:
- `palette_json` (str): JSON string containing color palette
- `color_selection` (str): Selected color type (color_1, color_2, etc.)

**Returns**: `str` - Color hex string or empty string if not found

**Implementation Details**:
- Supports both array and object with colors array formats
- Handles position-based selection (color_1, color_2, etc.)
- Supports named selection (first_color, second_color, etc.)
- Includes pattern matching for color types

#### `_validate_color_hex(color_hex: str) -> bool`

**Description**: Validate that the color hex is a valid hex color.

**Parameters**:
- `color_hex` (str): Hex color string (e.g., "#FF0000" or "FF0000")

**Returns**: `bool` - True if valid, False otherwise

**Validation Rules**:
- Supports 3-digit (#RGB) and 6-digit (#RRGGBB) formats
- Validates hex characters (0-9, A-F, a-f)
- Handles optional # prefix

#### `_extract_color_name(color_hex: str) -> str`

**Description**: Extract color name from hex color.

**Parameters**:
- `color_hex` (str): Hex color string

**Returns**: `str` - Human-readable color name

**Color Name Mapping**:
- Exact matches for common colors (Red, Blue, Green, etc.)
- Pattern-based naming (Red-ish, Blue-ish, etc.)
- Fallback to hex code format

#### `_matches_color_type(color_name: str, color_id: str, color_selection: str) -> bool`

**Description**: Check if a color matches the selected type based on name patterns.

**Parameters**:
- `color_name` (str): Color name from palette
- `color_id` (str): Color ID from palette
- `color_selection` (str): Selected color type

**Returns**: `bool` - True if color matches the selection type

**Pattern Matching**:
- Primary: ["primary", "main", "brand", "logo"]
- Secondary: ["secondary", "second", "support"]
- Accent: ["accent", "highlight", "emphasis"]
- Background: ["background", "bg", "base"]
- Text: ["text", "foreground", "content"]

#### `_return_default_color(error_message: str) -> Tuple`

**Description**: Return default values when color selection fails.

**Parameters**:
- `error_message` (str): Error message to include in color_info

**Returns**: `Tuple[str, str, str, str]` - Default color values

## APZmediaFontSelector

### Class Definition

```python
class APZmediaFontSelector:
    """Font Selector Node for easy font switching from brand assets."""
```

### Node Configuration

#### INPUT_TYPES
```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "brand_assets": ("BRAND_ASSETS", {}),
            "font_selection": (["font_primary", "font_primary_bold", "font_primary_italic", "font_secondary", "font_secondary_bold", "font_secondary_italic", "font_tertiary", "font_tertiary_bold", "font_tertiary_italic"], {"default": "font_primary"}),
        },
        "optional": {
            "custom_font_path": ("STRING", {
                "default": "",
                "multiline": False
            }),
            "use_custom": ("BOOLEAN", {"default": False}),
        }
    }
```

#### RETURN_TYPES
```python
RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
RETURN_NAMES = ("font_path", "font_name", "font_info", "font_list")
```

#### Node Metadata
```python
FUNCTION = "select_font"
CATEGORY = "apzmedia_brand"
```

### Public Methods

#### `select_font(brand_assets, font_selection, custom_font_path="", use_custom=False)`

**Description**: Select and return the appropriate font path from brand assets.

**Parameters**:
- `brand_assets` (dict): Dictionary containing all brand assets
- `font_selection` (str): Selected font key (font_primary, font_primary_bold, etc.)
- `custom_font_path` (str, optional): Custom font path override (default: "")
- `use_custom` (bool, optional): Whether to use custom font path (default: False)

**Returns**: `Tuple[str, str, str, str]`
- `font_path` (str): Selected font file path
- `font_name` (str): Human-readable font name
- `font_info` (str): Detailed font information string
- `font_list` (str): Formatted list of all available fonts

**Raises**: No exceptions (returns error values instead)

**Example**:
```python
selector = APZmediaFontSelector()
result = selector.select_font(
    brand_assets={"font_primary": "/path/to/font.ttf"},
    font_selection="font_primary",
    custom_font_path="",
    use_custom=False
)
# Returns: ("/path/to/font.ttf", "Font Name", "Primary: Font Name", "Available Fonts: ...")
```

### Private Methods

#### `_get_font_from_assets(brand_assets: Dict[str, Any], font_selection: str) -> str`

**Description**: Extract font path from brand assets dictionary.

**Parameters**:
- `brand_assets` (dict): Dictionary containing brand assets
- `font_selection` (str): Selected font key

**Returns**: `str` - Font path string or empty string if not found

**Implementation Details**:
- Direct key lookup in brand assets dictionary
- Handles missing or empty font paths
- Returns empty string for invalid selections

#### `_validate_font_path(font_path: str) -> bool`

**Description**: Validate that the font path exists and is a valid font file.

**Parameters**:
- `font_path` (str): Path to font file

**Returns**: `bool` - True if valid, False otherwise

**Validation Rules**:
- File existence check
- Supported extensions: .ttf, .otf, .woff, .woff2
- Non-zero file size validation
- Path accessibility check

#### `_extract_font_name(font_path: str) -> str`

**Description**: Extract font name from file path.

**Parameters**:
- `font_path` (str): Path to font file

**Returns**: `str` - Human-readable font name

**Name Processing**:
- Removes file extension
- Replaces underscores and hyphens with spaces
- Capitalizes words properly
- Fallback to "Unknown Font" if extraction fails

#### `_generate_font_list(brand_assets: Dict[str, Any]) -> str`

**Description**: Generate a formatted list of available fonts from brand assets.

**Parameters**:
- `brand_assets` (dict): Dictionary containing brand assets

**Returns**: `str` - Formatted string list of available fonts

**Output Format**:
```
Available Fonts:
• Primary: Font Name
• Primary Bold: Font Name
• Primary Italic: Font Name
...
```

#### `_return_default_font(error_message: str, font_list: str = "") -> tuple`

**Description**: Return default values when font selection fails.

**Parameters**:
- `error_message` (str): Error message to include in font_info
- `font_list` (str, optional): Font list string to return

**Returns**: `tuple` - Default font values

## Node Mappings

### Color Palette Selector
```python
NODE_CLASS_MAPPINGS = {
    "APZmediaColorPaletteSelector": APZmediaColorPaletteSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaColorPaletteSelector": "APZmedia - Color Palette Selector",
}
```

### Font Selector
```python
NODE_CLASS_MAPPINGS = {
    "APZmediaFontSelector": APZmediaFontSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaFontSelector": "APZmedia - Font Selector",
}
```

## Data Types and Formats

### Color Palette JSON Format

#### Array Format
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
  }
]
```

#### Object Format
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

### Brand Assets Format

#### Font Asset Structure
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

## Error Handling

### Color Selector Errors
- **Invalid JSON**: Returns default color with error message
- **Missing colors**: Falls back to available colors or returns error
- **Invalid hex**: Validates hex format and provides feedback
- **Empty palette**: Returns appropriate error messages

### Font Selector Errors
- **Missing fonts**: Returns appropriate error messages when fonts aren't found
- **Invalid paths**: Validates font file paths and accessibility
- **Format errors**: Checks font file format and integrity
- **Custom font validation**: Validates custom font paths and formats

## Performance Considerations

### Color Selector
- **Lightweight processing**: Minimal computational overhead
- **Caching**: Efficient color lookup and validation
- **Memory efficient**: Processes JSON in-place without large data structures

### Font Selector
- **Lightweight processing**: Minimal computational overhead
- **File validation**: Efficient font file checking
- **Memory efficient**: Processes font paths without loading font data
- **Caching**: Efficient font lookup and validation

## Integration Examples

### Basic Integration
```python
# Color selector
color_selector = APZmediaColorPaletteSelector()
color_result = color_selector.select_color(
    palette_json=palette_data,
    color_selection="color_1"
)

# Font selector
font_selector = APZmediaFontSelector()
font_result = font_selector.select_font(
    brand_assets=brand_data,
    font_selection="font_primary"
)
```

### Custom Override Integration
```python
# Custom color
color_result = color_selector.select_color(
    palette_json=palette_data,
    color_selection="color_1",
    custom_color="#FF0000",
    use_custom=True
)

# Custom font
font_result = font_selector.select_font(
    brand_assets=brand_data,
    font_selection="font_primary",
    custom_font_path="/path/to/custom.ttf",
    use_custom=True
)
```

## Version History

### Color Palette Selector
- **v1.0**: Initial release with basic color selection
- **v1.1**: Added custom color override functionality
- **v1.2**: Enhanced color name generation and error handling
- **v1.3**: Improved JSON parsing and validation

### Font Selector
- **v1.0**: Initial release with basic font selection
- **v1.1**: Added custom font path override functionality
- **v1.2**: Enhanced font name generation and error handling
- **v1.3**: Improved font validation and format support
- **v1.4**: Added font list output and better debugging

## Support and Troubleshooting

### Common Issues
1. **Data format errors**: Check JSON structure and font asset format
2. **File path issues**: Validate file existence and permissions
3. **Selection errors**: Verify selection options match available data
4. **Integration errors**: Check node input/output types and connections

### Debug Information
- Use `color_info` and `font_info` outputs for detailed information
- Check `font_list` output for available fonts
- Enable logging for detailed processing information
- Validate input data formats before processing
