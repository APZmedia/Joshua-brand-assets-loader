# Import node modules
from .nodes import brand_asset_loader
from .nodes import logo_placement_node
from .nodes import logo_overlay_node

# Combine all node mappings
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(brand_asset_loader.NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(logo_placement_node.NODE_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(logo_overlay_node.NODE_CLASS_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(brand_asset_loader.NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(logo_placement_node.NODE_DISPLAY_NAME_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(logo_overlay_node.NODE_DISPLAY_NAME_MAPPINGS)
