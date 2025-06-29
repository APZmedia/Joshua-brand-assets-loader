from setuptools import setup, find_packages

setup(
    name="apzmedia_brand_assets",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'comfyui.nodes': [
            'brand_asset_loader = nodes.brand_asset_loader:APZmediaBrandAssetLoader',
            'logo_placement_node = nodes.logo_placement_node:APZmediaLogoPlacement',
        ],
    },
    author="Pablo Apiolazza",
    author_email="info@apzmedia.com",
    description="ComfyUI nodes to load brand assets and place logos dynamically.",
    url="https://github.com/apzmedia/ComfyUI-APZmedia-brand-assets",  # Example URL
    python_requires='>=3.8',
)
