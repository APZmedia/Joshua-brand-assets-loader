#!/usr/bin/env python3
"""
Test script to verify backward compatibility of enhanced POI smart crop.
This ensures the node interface remains unchanged while improving the internal algorithm.
"""

import sys
import os
import numpy as np
import torch

# Add the nodes directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'nodes'))

from poi_smart_crop import POISmartCrop

def test_backward_compatibility():
    """Test that the node works with the original interface."""
    print("Testing POI Smart Crop backward compatibility...")
    
    # Create a test image tensor [B, H, W, C]
    test_image = torch.rand(1, 256, 256, 3)  # Single image, 256x256, RGB
    
    # Initialize the node
    node = POISmartCrop()
    
    # Test with minimal parameters (original interface)
    try:
        result = node.run(
            images=test_image,
            width=128,
            height=128,
            interpolation="lanczos",
            method="fill / crop",
            condition="always",
            multiple_of=0,
            centering_preference="center",
            padding=0.12
        )
        
        print("✅ Basic interface test passed")
        print(f"   Output shapes: {[tensor.shape for tensor in result]}")
        
        # Test with optional parameters
        result_with_options = node.run(
            images=test_image,
            width=128,
            height=128,
            interpolation="lanczos",
            method="fill / crop",
            condition="always",
            multiple_of=0,
            centering_preference="center",
            padding=0.12,
            poi_size_percent=15.0,
            refine_with_grabcut=False,
            fallback_center_crop=True,
            show_overlay=False
        )
        
        print("✅ Optional parameters test passed")
        print(f"   Output shapes: {[tensor.shape for tensor in result_with_options]}")
        
        # Verify output types
        cropped, box, saliency_map = result
        assert cropped.dim() == 4, "Cropped should be [B,H,W,C]"
        assert isinstance(box, tuple), "Box should be tuple"
        assert saliency_map.dim() == 4, "Saliency map should be [B,H,W,C]"
        
        print("✅ Output type validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_enhanced_functionality():
    """Test that the enhanced functionality works internally."""
    print("\nTesting enhanced POI detection functionality...")
    
    try:
        from poi_smart_crop import enhanced_poi_detection, adaptive_threshold_saliency, find_saliency_blobs
        
        # Create a test grayscale image
        test_gray = np.random.randint(0, 255, (128, 128), dtype=np.uint8)
        
        # Test enhanced POI detection
        poi_x, poi_y, saliency_map, blob_info = enhanced_poi_detection(test_gray)
        
        print(f"✅ Enhanced POI detection: POI at ({poi_x}, {poi_y})")
        print(f"   Found {blob_info['total_blobs']} blobs, selected {blob_info['selected_blobs']}")
        
        # Test adaptive thresholding
        thresholded = adaptive_threshold_saliency(saliency_map, method="otsu")
        print(f"✅ Adaptive thresholding: {np.sum(thresholded)} active pixels")
        
        # Test blob detection
        blobs = find_saliency_blobs(thresholded, min_area=50)
        print(f"✅ Blob detection: Found {len(blobs)} blobs")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("POI Smart Crop Backward Compatibility Test")
    print("=" * 50)
    
    # Test backward compatibility
    compat_test = test_backward_compatibility()
    
    # Test enhanced functionality
    enhanced_test = test_enhanced_functionality()
    
    print("\n" + "=" * 50)
    if compat_test and enhanced_test:
        print("🎉 All tests passed! Backward compatibility maintained.")
    else:
        print("❌ Some tests failed.")
        sys.exit(1)
