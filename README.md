# APZmedia Brand Assets Loader for ComfyUI

A ComfyUI extension that provides nodes for loading brand assets and dynamically placing logos in AI-generated images. This enables automated brand integration into AI workflows.

## 🚀 Features

- **Brand Asset Loading**: Load and manage brand assets (logos, colors, fonts) from file paths
- **Dynamic Logo Placement**: Automatically place logos in AI-generated images with positioning controls
- **Multiple Format Support**: PNG, JPG, JPEG, WebP, BMP, TIFF for images; TTF, OTF, WOFF, WOFF2 for fonts
- **Advanced Blending**: Multiple blend modes (normal, multiply, screen, overlay) with opacity control
- **File Path Input**: Direct file path input for maximum flexibility
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

## 🗂️ Asset File Formats

### Supported Image Formats (Logos)
- **PNG** (recommended for transparency)
- **JPG/JPEG**
- **WebP**
- **BMP**
- **TIFF/TIF**

### Supported Font Formats
- **TTF** (TrueType)
- **OTF** (OpenType)
- **WOFF** (Web Open Font Format)
- **WOFF2** (Web Open Font Format 2.0)

### Supported Color Formats
- **TXT** files containing hex color codes (e.g., `#FF0000`)
- **COLOR** files containing hex color codes
- **HEX** files containing hex color codes

## 🎯 Usage

### 1. Brand Asset Loader Node

**Purpose**: Load brand assets from file paths for use in workflows

**Inputs**:
- `asset_type`: Type of asset (logo, font, color)
- `file_path`: Full path to the asset file

**Outputs**:
- `logo_image`: Loaded logo as image tensor
- `logo_mask`: Logo mask/alpha channel
- `font_path_or_url`: Font file path
- `color_hex`: Color hex code

**Example**:
```
Asset Type: logo
File Path: C:\BrandAssets\company_logo.png
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

## 📋 Sample Workflow

1. **Load Brand Assets**:
   - Add "APZmedia - Brand Asset Loader" node
   - Set asset type to "logo"
   - Enter the full file path to your logo (e.g., `C:\BrandAssets\logo.png`)
   - Connect outputs to logo placement node

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

**"File not found" Error**:
- Check that the file path is correct and complete
- Ensure the file exists at the specified location
- Use absolute paths for best compatibility
- Verify file permissions

**"Invalid image file format" Error**:
- Ensure the file has a supported extension (.png, .jpg, etc.)
- Check that the file is not corrupted
- Try opening the file in an image editor to verify it's valid

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
- Brand asset loading from file paths
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

