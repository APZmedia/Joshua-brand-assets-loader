from .nodes.brand_asset_loader import APZmediaBrandAssetLoader
from .nodes.logo_placement_node import APZmediaLogoPlacement
from .nodes.logo_overlay_node import APZmediaLogoOverlay

NODE_CLASS_MAPPINGS = {
    "APZmediaBrandAssetLoader": APZmediaBrandAssetLoader,
    "APZmediaLogoPlacement": APZmediaLogoPlacement,
    "APZmediaLogoOverlay": APZmediaLogoOverlay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "APZmediaBrandAssetLoader": "APZmedia - Brand Asset Loader",
    "APZmediaLogoPlacement": "APZmedia - Logo Placement",
    "APZmediaLogoOverlay": "APZmedia - Logo Overlay",
}
