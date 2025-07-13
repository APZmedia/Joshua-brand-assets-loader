# Joshua Brand Assets Loader - Private Custom Node

**⚠️ This is a private custom node for ComfyUI - not published in the registry**

A comprehensive brand asset loader for ComfyUI that handles logos, fonts, and color palettes with dual loading modes (API and manual).

## Features

- **Dual Loading Modes**: API integration or manual file loading
- **Comprehensive Asset Support**: 5 logo variations, 3 font types, color palettes
- **Security-First**: Built-in protection against common vulnerabilities
- **Flexible Authentication**: Works with or without API tokens
- **Error Handling**: Robust error handling with clear status messages

## Installation (Local)

### Method 1: Direct Copy (Recommended)
1. Copy this entire folder to your ComfyUI custom nodes directory:
   ```
   ComfyUI/custom_nodes/Joshua-brand-assets-loader/
   ```

2. Restart ComfyUI

3. The nodes will appear in the "apzmedia_brand" category

### Method 2: Git Clone (Development)
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/Joshua-brand-assets-loader.git
cd Joshua-brand-assets-loader
pip install -r requirements.txt
```

## Usage

### Manual Mode
1. Add "APZmedia - Brand Asset Loader" node to your workflow
2. Set `load_method` to "manual"
3. Provide file paths for your brand assets:
   - Logo files (PNG, JPG, etc.)
   - Font files (TTF, OTF, etc.)
   - Color palette JSON

### API Mode
1. Add "APZmedia - Brand Asset Loader" node to your workflow
2. Set `load_method` to "api"
3. Configure API settings:
   - `brand_id`: Your brand identifier
   - `api_base_url`: Your API endpoint
   - `api_token`: Authentication token (optional for public APIs)

## Node Outputs

The node provides 11 outputs:
- **5 Logo Images**: vertical_color, vertical_mono, horizontal_color, horizontal_mono, icon
- **3 Font Paths**: primary, secondary, tertiary fonts
- **Color Palette**: JSON string with brand colors
- **Brand Name**: Name of the loaded brand
- **Status Message**: Operation status and error information

## Security

This node includes comprehensive security measures:
- Input validation and sanitization
- Path traversal protection
- File size and dimension limits
- URL validation and SSRF protection
- Secure logging practices

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## Development

### Project Structure
```
Joshua-brand-assets-loader/
├── nodes/
│   ├── __init__.py
│   ├── brand_asset_loader.py      # Main asset loader
│   ├── logo_placement_node.py     # Logo placement node
│   └── logo_overlay_node.py       # Logo overlay node
├── assets/                        # Sample brand assets
├── .notes/                        # Project documentation
├── __init__.py                    # Node registration
├── setup.py                       # Package configuration
├── requirements.txt               # Dependencies
├── SECURITY.md                    # Security documentation
└── README.md                      # This file
```

### Dependencies
- torch >= 1.9.0
- pillow >= 8.0.0
- numpy >= 1.19.0
- requests >= 2.25.0

## License

Private use only - not for public distribution.

## Support

For internal support, contact your development team.

---

**Note**: This is a private custom node. Do not distribute or publish without explicit permission.

