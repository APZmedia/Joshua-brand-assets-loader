#!/usr/bin/env python3
"""
Test script to verify that the Joshua Brand Assets Loader module can be imported correctly.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """Test importing the module and its nodes."""
    try:
        print("Testing module import...")
        
        # Import the main module
        import __init__ as joshua_brand_assets
        
        print("✓ Main module imported successfully")
        
        # Check if NODE_CLASS_MAPPINGS is defined
        if hasattr(joshua_brand_assets, 'NODE_CLASS_MAPPINGS'):
            print(f"✓ NODE_CLASS_MAPPINGS found with {len(joshua_brand_assets.NODE_CLASS_MAPPINGS)} nodes")
            for node_name, node_class in joshua_brand_assets.NODE_CLASS_MAPPINGS.items():
                print(f"  - {node_name}: {node_class.__name__}")
        else:
            print("✗ NODE_CLASS_MAPPINGS not found")
            return False
        
        # Check if NODE_DISPLAY_NAME_MAPPINGS is defined
        if hasattr(joshua_brand_assets, 'NODE_DISPLAY_NAME_MAPPINGS'):
            print(f"✓ NODE_DISPLAY_NAME_MAPPINGS found with {len(joshua_brand_assets.NODE_DISPLAY_NAME_MAPPINGS)} mappings")
        else:
            print("✗ NODE_DISPLAY_NAME_MAPPINGS not found")
            return False
        
        # Test importing individual node modules
        print("\nTesting individual node imports...")
        
        from nodes import brand_asset_loader
        print("✓ brand_asset_loader imported")
        
        from nodes import logo_placement_node
        print("✓ logo_placement_node imported")
        
        from nodes import logo_overlay_node
        print("✓ logo_overlay_node imported")
        
        # Test creating instances of node classes
        print("\nTesting node class instantiation...")
        
        brand_loader = brand_asset_loader.APZmediaBrandAssetLoader()
        print("✓ APZmediaBrandAssetLoader instantiated")
        
        logo_placement = logo_placement_node.APZmediaLogoPlacement()
        print("✓ APZmediaLogoPlacement instantiated")
        
        logo_overlay = logo_overlay_node.APZmediaLogoOverlay()
        print("✓ APZmediaLogoOverlay instantiated")
        
        print("\n🎉 All tests passed! The module should work correctly in ComfyUI.")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_import()
    sys.exit(0 if success else 1) 