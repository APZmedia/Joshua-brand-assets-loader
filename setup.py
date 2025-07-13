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
    ],
    entry_points={
        'comfyui.nodes': [
            'brand_asset_loader = nodes.brand_asset_loader:APZmediaBrandAssetLoader',
            'logo_placement_node = nodes.logo_placement_node:APZmediaLogoPlacement',
            'logo_overlay_node = nodes.logo_overlay_node:APZmediaLogoOverlay',
        ],
    },
    author="Pablo Apiolazza",
    author_email="info@apzmedia.com",
    description="ComfyUI nodes to load brand assets and place logos dynamically.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.8',
    keywords="comfyui, brand, assets, logo, placement, ai, image-processing",
    project_urls={
        "Bug Reports": "https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets/issues",
        "Source": "https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets",
    },
)
