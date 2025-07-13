# Nodes package for Joshua Brand Assets Loader
# This file makes the nodes directory a Python package

# Import all node modules
from .brand_asset_loader import NODE_CLASS_MAPPINGS as BRAND_LOADER_MAPPINGS
from .brand_asset_loader import NODE_DISPLAY_NAME_MAPPINGS as BRAND_LOADER_DISPLAY_MAPPINGS
from .global_brand_access import NODE_CLASS_MAPPINGS as GLOBAL_ACCESS_MAPPINGS
from .global_brand_access import NODE_DISPLAY_NAME_MAPPINGS as GLOBAL_ACCESS_DISPLAY_MAPPINGS

# Combine all node mappings
NODE_CLASS_MAPPINGS = {**BRAND_LOADER_MAPPINGS, **GLOBAL_ACCESS_MAPPINGS}
NODE_DISPLAY_NAME_MAPPINGS = {**BRAND_LOADER_DISPLAY_MAPPINGS, **GLOBAL_ACCESS_DISPLAY_MAPPINGS} 