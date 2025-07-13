#!/usr/bin/env python3
"""
Test script for the APZmediaGradientOverlay node.
This script tests the gradient overlay functionality with different parameters.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nodes.gradient_overlay_node import APZmediaGradientOverlay
import torch

def test_hex_color_parsing():
    """Test hex color parsing functionality."""
    print("Testing hex color parsing...")
    
    node = APZmediaGradientOverlay()
    
    # Test valid hex colors
    test_cases = [
        "#000000",  # Black
        "FFFFFF",   # White (no #)
        "#FF0000",  # Red
        "#00FF00",  # Green
        "#0000FF",  # Blue
        "#FF6600",  # Orange
    ]
    
    for hex_color in test_cases:
        result = node._parse_hex_color(hex_color)
        if result:
            r, g, b = result
            print(f"✓ {hex_color} -> RGB({r}, {g}, {b})")
        else:
            print(f"✗ {hex_color} -> Invalid")

def test_gradient_mask_creation():
    """Test gradient mask creation for different types."""
    print("\nTesting gradient mask creation...")
    
    node = APZmediaGradientOverlay()
    
    # Create a dummy background image (3, 256, 256)
    background_image = torch.ones(3, 256, 256, dtype=torch.float32)
    
    # Test linear gradients
    linear_tests = [
        ("horizontal", "left", "right", 0.0, 1.0, "Horizontal gradient"),
        ("vertical", "top", "bottom", 0.0, 1.0, "Vertical gradient"),
        ("diagonal_tl_br", "top-left", "bottom-right", 0.0, 1.0, "Diagonal TL-BR gradient"),
    ]
    
    for orientation, start_pos, end_pos, start_alpha, end_alpha, description in linear_tests:
        try:
            mask = node._create_linear_gradient_mask(256, 256, orientation, start_pos, end_pos, start_alpha, end_alpha)
            print(f"✓ {description}: shape={mask.shape}, min={mask.min().item():.3f}, max={mask.max().item():.3f}")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")
    
    # Test radial gradient
    try:
        mask = node._create_radial_gradient_mask(256, 256, 0.5, 0.5, 0.5, 0.0, 1.0)
        print(f"✓ Radial gradient: shape={mask.shape}, min={mask.min().item():.3f}, max={mask.max().item():.3f}")
    except Exception as e:
        print(f"✗ Radial gradient: Error - {e}")
    
    # Test conical gradient
    try:
        mask = node._create_conical_gradient_mask(256, 256, 0.5, 0.5, 0.0, 1.0)
        print(f"✓ Conical gradient: shape={mask.shape}, min={mask.min().item():.3f}, max={mask.max().item():.3f}")
    except Exception as e:
        print(f"✗ Conical gradient: Error - {e}")

def test_gradient_overlay_creation():
    """Test full gradient overlay creation."""
    print("\nTesting gradient overlay creation...")
    
    node = APZmediaGradientOverlay()
    
    # Create a dummy background image (1, 256, 256, 3) for ComfyUI format
    background_image = torch.ones(1, 256, 256, 3, dtype=torch.float32) * 0.5  # Gray background
    
    # Test different gradient types
    test_cases = [
        ("#000000", "linear", "horizontal", "left", "right", 0.0, 1.0, "Black horizontal gradient"),
        ("#FF0000", "linear", "vertical", "top", "bottom", 0.0, 1.0, "Red vertical gradient"),
        ("#0000FF", "radial", "horizontal", "center", "center", 0.0, 1.0, "Blue radial gradient"),
    ]
    
    for hex_color, grad_type, orientation, start_pos, end_pos, start_alpha, end_alpha, description in test_cases:
        try:
            result = node.create_gradient_overlay(
                background_image, hex_color, grad_type, orientation,
                start_pos, end_pos, start_alpha, end_alpha
            )
            if result and len(result) == 1:
                image_tensor = result[0]
                print(f"✓ {description}: shape={image_tensor.shape}")
                
                # Check tensor properties
                if image_tensor.dim() == 4 and image_tensor.shape[0] == 1:
                    print(f"  - Correct ComfyUI format: (1, H, W, 3)")
                else:
                    print(f"  - Warning: Unexpected shape format")
                
                # Check value range
                min_val = image_tensor.min().item()
                max_val = image_tensor.max().item()
                print(f"  - Value range: {min_val:.3f} to {max_val:.3f}")
                
            else:
                print(f"✗ {description}: Unexpected result format")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")

def test_blend_modes():
    """Test different blend modes."""
    print("\nTesting blend modes...")
    
    node = APZmediaGradientOverlay()
    
    # Create test tensors
    background = torch.ones(3, 64, 64, dtype=torch.float32) * 0.5  # Gray background
    gradient_overlay = torch.ones(3, 64, 64, dtype=torch.float32) * 0.8  # Light overlay
    gradient_mask = torch.ones(64, 64, dtype=torch.float32) * 0.5  # 50% alpha
    
    blend_modes = ["normal", "multiply", "screen", "overlay", "soft_light", "hard_light"]
    
    for blend_mode in blend_modes:
        try:
            result = node._blend_gradient(background, gradient_overlay, gradient_mask, blend_mode)
            print(f"✓ {blend_mode}: shape={result.shape}, min={result.min().item():.3f}, max={result.max().item():.3f}")
        except Exception as e:
            print(f"✗ {blend_mode}: Error - {e}")

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTesting error handling...")
    
    node = APZmediaGradientOverlay()
    
    # Create a valid background image
    background_image = torch.ones(1, 256, 256, 3, dtype=torch.float32)
    
    # Test invalid hex color
    try:
        result = node.create_gradient_overlay(
            background_image, "invalid", "linear", "horizontal",
            "left", "right", 0.0, 1.0
        )
        print("✓ Handled invalid hex color correctly")
    except Exception as e:
        print(f"✗ Unexpected error with invalid hex: {e}")
    
    # Test invalid gradient type
    try:
        result = node.create_gradient_overlay(
            background_image, "#000000", "invalid_type", "horizontal",
            "left", "right", 0.0, 1.0
        )
        print("✓ Handled invalid gradient type correctly")
    except Exception as e:
        print(f"✗ Unexpected error with invalid gradient type: {e}")

if __name__ == "__main__":
    print("APZmediaGradientOverlay Node Test Suite")
    print("=" * 45)
    
    test_hex_color_parsing()
    test_gradient_mask_creation()
    test_gradient_overlay_creation()
    test_blend_modes()
    test_error_handling()
    
    print("\nTest suite completed!") 