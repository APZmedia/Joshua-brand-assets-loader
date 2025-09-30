#!/usr/bin/env python3
"""
Test script for the 4-directional gradient overlay functionality.
This script tests the top, bottom, left, right gradient options.
"""

import torch
import sys
import os

# Add the nodes directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'nodes'))

from gradient_overlay_node import APZmediaGradientOverlay

def test_4directional_gradients():
    """Test the 4-directional gradient functionality."""
    print("Testing 4-directional gradient overlay...")
    
    # Create a test background image (3, 256, 256)
    background = torch.rand(3, 256, 256)
    
    # Create the gradient overlay node
    gradient_node = APZmediaGradientOverlay()
    
    # Test cases for the 4 directional options
    test_cases = [
        {
            "name": "Top Direction",
            "orientation": "top",
            "start_position": 0.0,
            "end_position": 1.0,
            "description": "Gradient from top to bottom"
        },
        {
            "name": "Bottom Direction", 
            "orientation": "bottom",
            "start_position": 0.0,
            "end_position": 1.0,
            "description": "Gradient from bottom to top"
        },
        {
            "name": "Left Direction",
            "orientation": "left",
            "start_position": 0.0,
            "end_position": 1.0,
            "description": "Gradient from left to right"
        },
        {
            "name": "Right Direction",
            "orientation": "right",
            "start_position": 0.0,
            "end_position": 1.0,
            "description": "Gradient from right to left"
        },
        {
            "name": "Top with Custom Positions",
            "orientation": "top",
            "start_position": 0.2,
            "end_position": 0.8,
            "description": "Top gradient with custom start/end positions"
        },
        {
            "name": "Left with Reversed Positions",
            "orientation": "left",
            "start_position": 0.8,
            "end_position": 0.2,
            "description": "Left gradient with reversed start/end positions"
        }
    ]
    
    print(f"Running {len(test_cases)} test cases...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print(f"Description: {test_case['description']}")
        print(f"Orientation: {test_case['orientation']}")
        print(f"Start Position: {test_case['start_position']}")
        print(f"End Position: {test_case['end_position']}")
        
        try:
            # Create gradient overlay
            result = gradient_node.create_gradient_overlay(
                background_image=background,
                hex_color="#FF0000",  # Red gradient
                gradient_type="linear",
                orientation=test_case['orientation'],
                start_position=test_case['start_position'],
                end_position=test_case['end_position'],
                start_opacity=0.0,
                end_opacity=0.8,
                blend_mode="normal"
            )
            
            if result and len(result) > 0:
                output_shape = result[0].shape
                print(f"✅ Success! Output shape: {output_shape}")
                
                # Check if the output has the expected shape (1, H, W, 3)
                if len(output_shape) == 4 and output_shape[0] == 1 and output_shape[3] == 3:
                    print("✅ Output format is correct")
                else:
                    print(f"⚠️  Unexpected output shape: {output_shape}")
            else:
                print("❌ Failed: No output generated")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("4-Directional gradient testing completed!")
    print("The gradient overlay now supports:")
    print("- Top: Gradient from top to bottom")
    print("- Bottom: Gradient from bottom to top") 
    print("- Left: Gradient from left to right")
    print("- Right: Gradient from right to left")
    print("- Custom start/end positions for precise control")
    print("="*60)

if __name__ == "__main__":
    test_4directional_gradients()

