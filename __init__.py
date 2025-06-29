from .nodes.brand_asset_loader import APZmediaBrandAssetLoader
from .nodes.logo_placement_node import APZmediaLogoPlacement

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
    "APZmediaLogoPlacement": APZmediaLogoPlacement,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
    "APZmediaLogoPlacement": "APZmedia - Logo Placement",
}
