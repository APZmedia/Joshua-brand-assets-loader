from setuptools import setup, find_packages

setup(
    name="joshua-brand-assets-loader",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "torch>=1.9.0",
        "pillow>=8.0.0",
        "numpy>=1.19.0",
        "requests>=2.25.0",
    ],
    entry_points={
        'comfyui.nodes': [
            'brand_asset_loader = nodes.brand_asset_loader:APZmediaBrandAssetLoader',
            'logo_placement_node = nodes.logo_placement_node:APZmediaLogoPlacement',
            'logo_overlay_node = nodes.logo_overlay_node:APZmediaLogoOverlay',
            'url_image_loader = nodes.url_image_loader:APZmediaURLImageLoader',
            'font_selector = nodes.font_selector_node:APZmediaFontSelector',
            'brand_asset_reader = nodes.brand_asset_reader_node:APZmediaBrandAssetReader',
            'color_palette_selector = nodes.color_palette_selector_node:APZmediaColorPaletteSelector',
            'color_palette = nodes.color_palette_node:APZmediaColorPalette',
        ],
    },
    author="Pablo Apiolazza",
    author_email="info@apzmedia.com",
    description="Private ComfyUI nodes to load brand assets and place logos dynamically.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",  # Private package - no public URL
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Private :: Do Not Upload",
    ],
    python_requires='>=3.8',
    keywords="comfyui, brand, assets, logo, placement, ai, image-processing, private",
    project_urls={
        "Private": "Internal use only",
    },
)
