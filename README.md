# APZmedia Brand Assets Loader for ComfyUI

A ComfyUI extension that provides nodes for loading brand assets and dynamically placing logos in AI-generated images. This enables automated brand integration into AI workflows.

## 🚀 Features

- **Brand Asset Loading**: Load and manage brand assets (logos, colors, fonts) from various sources
- **Dynamic Logo Placement**: Automatically place logos in AI-generated images with positioning controls
- **Multiple Format Support**: PNG, JPG, JPEG, WebP, BMP, TIFF for images; TTF, OTF, WOFF, WOFF2 for fonts
- **Advanced Blending**: Multiple blend modes (normal, multiply, screen, overlay) with opacity control
- **Configurable Paths**: Custom asset paths with environment variable support
- **Robust Error Handling**: Comprehensive error handling with graceful fallbacks
- **ComfyUI Integration**: Seamless integration with existing ComfyUI workflows

## 📦 Installation

### Method 1: Direct Installation
```bash
# Clone the repository
git clone https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets.git

# Navigate to the directory
cd ComfyUI-APZmedia-brand-assets

# Install the package
pip install -e .
```

### Method 2: From Source
```bash
# Clone the repository
git clone https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets.git

# Copy to ComfyUI custom_nodes directory
cp -r ComfyUI-APZmedia-brand-assets /path/to/ComfyUI/custom_nodes/
```

## 🗂️ Asset Organization

Create the following directory structure for your brand assets:

```
assets/brand_assets/
├── logos/
│   ├── company_logo.png
│   ├── product_logo.jpg
│   └── watermark.webp
├── fonts/
│   ├── brand_font.ttf
│   ├── heading_font.otf
│   └── body_font.woff
└── colors/
    ├── primary_color.txt
    ├── secondary_color.txt
    └── accent_color.txt
```

### Asset File Formats

**Images (Logos)**:
- PNG (recommended for transparency)
- JPG/JPEG
- WebP
- BMP
- TIFF

**Fonts**:
- TTF
- OTF
- WOFF
- WOFF2

**Colors**:
- Text files containing hex color codes (e.g., `#FF0000`)

## 🎯 Usage

### 1. Brand Asset Loader Node

**Purpose**: Load brand assets for use in workflows

**Inputs**:
- `asset_type`: Type of asset (logo, font, color)
- `asset_key`: Name/key of the asset file (without extension)
- `output_format`: Output format preference (local_path, url)
- `custom_asset_path`: Optional custom path override

**Outputs**:
- `logo_image`: Loaded logo as image tensor
- `logo_mask`: Logo mask/alpha channel
- `font_path_or_url`: Font file path or URL
- `color_hex`: Color hex code

**Example**:
```
Asset Type: logo
Asset Key: company_logo
Output Format: local_path
Custom Asset Path: (leave empty for default)
```

### 2. Logo Placement Node

**Purpose**: Place logos dynamically in images

**Required Inputs**:
- `background_image`: Base image to place logo on
- `logo_image`: Logo image tensor
- `logo_mask`: Logo mask tensor
- `position`: Logo position (top-left, center, bottom-right, etc.)
- `scale`: Logo scale factor (0.01 to 1.0)
- `offset_x`: Horizontal offset (-1000 to 1000)
- `offset_y`: Vertical offset (-1000 to 1000)

**Optional Inputs**:
- `blend_mode`: Blending mode (normal, multiply, screen, overlay)
- `opacity`: Logo opacity (0.0 to 1.0)

**Outputs**:
- `composited_image`: Final image with logo placed

**Example**:
```
Position: bottom-right
Scale: 0.15
Offset X: -20
Offset Y: -20
Blend Mode: normal
Opacity: 0.9
```

## 🔧 Configuration

### Environment Variables

Set the `APZMEDIA_ASSET_PATH` environment variable to customize the asset base path:

```bash
export APZMEDIA_ASSET_PATH="/path/to/your/brand/assets"
```

### Custom Asset Paths

You can specify custom asset paths per node using the `custom_asset_path` parameter in the Brand Asset Loader node.

## 📋 Sample Workflow

1. **Load Brand Assets**:
   - Add "APZmedia - Brand Asset Loader" node
   - Configure asset type and key
   - Connect to logo placement node

2. **Generate Background Image**:
   - Use any image generation node (Stable Diffusion, etc.)
   - Connect output to logo placement node

3. **Place Logo**:
   - Add "APZmedia - Logo Placement" node
   - Connect background image and logo assets
   - Configure position, scale, and blending options

4. **Save Result**:
   - Connect composited image to save node
   - Generate final branded image

## 🛠️ Troubleshooting

### Common Issues

**"Logo file not found" Error**:
- Check that the asset file exists in the correct directory
- Verify the asset key matches the filename (without extension)
- Ensure the file format is supported

**"Invalid input images" Error**:
- Make sure background image has 3 channels (RGB)
- Ensure logo image has 3 channels (RGB)
- Verify logo mask has 1 channel (grayscale)

**Performance Issues**:
- Reduce logo scale for better performance
- Use smaller image resolutions
- Consider using WebP format for logos

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/ComfyUI"
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## 🔄 Version History

### v0.1.0
- Initial release
- Brand asset loading functionality
- Logo placement with positioning controls
- Multiple format support
- Comprehensive error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets/issues)
- **Discussions**: [GitHub Discussions](https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets/discussions)
- **Email**: info@apzmedia.com

## 🙏 Acknowledgments

- ComfyUI community for the excellent framework
- PyTorch team for the powerful tensor operations
- PIL/Pillow team for image processing capabilities

---

**Made with ❤️ by APZmedia**

