#!/usr/bin/env python3
"""
Local installation script for Joshua Brand Assets Loader
This script helps install the private custom node in your ComfyUI installation.
"""

import os
import sys
import shutil
from pathlib import Path

def find_comfyui_custom_nodes():
    """Find ComfyUI custom_nodes directory."""
    possible_paths = [
        # Common ComfyUI installation paths
        "custom_nodes",
        "../custom_nodes",
        "../../custom_nodes",
        # Windows portable paths
        "ComfyUI_windows_portable/ComfyUI/custom_nodes",
        "../ComfyUI_windows_portable/ComfyUI/custom_nodes",
        # Linux/Mac paths
        "ComfyUI/custom_nodes",
        "../ComfyUI/custom_nodes",
        # User home directory
        os.path.expanduser("~/ComfyUI/custom_nodes"),
        os.path.expanduser("~/Desktop/ComfyUI/custom_nodes"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    return None

def install_node():
    """Install the node in ComfyUI custom_nodes directory."""
    print("🔧 Joshua Brand Assets Loader - Local Installation")
    print("=" * 50)
    
    # Find ComfyUI custom_nodes directory
    custom_nodes_dir = find_comfyui_custom_nodes()
    
    if not custom_nodes_dir:
        print("❌ Could not find ComfyUI custom_nodes directory.")
        print("\nPlease manually copy this folder to your ComfyUI custom_nodes directory:")
        print("   ComfyUI/custom_nodes/Joshua-brand-assets-loader/")
        print("\nOr run this script from within your ComfyUI directory.")
        return False
    
    print(f"✅ Found ComfyUI custom_nodes directory: {custom_nodes_dir}")
    
    # Current directory (where this script is located)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    node_name = "Joshua-brand-assets-loader"
    target_dir = os.path.join(custom_nodes_dir, node_name)
    
    print(f"📁 Installing from: {current_dir}")
    print(f"📁 Installing to: {target_dir}")
    
    # Check if already installed
    if os.path.exists(target_dir):
        print(f"⚠️  Node already exists at {target_dir}")
        response = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if response != 'y':
            print("❌ Installation cancelled.")
            return False
        shutil.rmtree(target_dir)
    
    try:
        # Copy the entire directory
        shutil.copytree(current_dir, target_dir, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', '.gitignore', 'install_local.py'
        ))
        
        print("✅ Node installed successfully!")
        print(f"📁 Location: {target_dir}")
        
        # Install dependencies
        print("\n📦 Installing dependencies...")
        requirements_file = os.path.join(target_dir, "requirements.txt")
        if os.path.exists(requirements_file):
            os.system(f"pip install -r {requirements_file}")
            print("✅ Dependencies installed!")
        else:
            print("⚠️  No requirements.txt found, skipping dependency installation.")
        
        print("\n🎉 Installation complete!")
        print("\nNext steps:")
        print("1. Restart ComfyUI")
        print("2. Look for 'apzmedia_brand' category in the node menu")
        print("3. Add 'APZmedia - Brand Asset Loader' node to your workflow")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {str(e)}")
        return False

def uninstall_node():
    """Uninstall the node from ComfyUI custom_nodes directory."""
    print("🗑️  Joshua Brand Assets Loader - Uninstall")
    print("=" * 40)
    
    custom_nodes_dir = find_comfyui_custom_nodes()
    if not custom_nodes_dir:
        print("❌ Could not find ComfyUI custom_nodes directory.")
        return False
    
    node_name = "Joshua-brand-assets-loader"
    target_dir = os.path.join(custom_nodes_dir, node_name)
    
    if not os.path.exists(target_dir):
        print(f"❌ Node not found at {target_dir}")
        return False
    
    print(f"📁 Found node at: {target_dir}")
    response = input("Do you want to uninstall it? (y/N): ").lower().strip()
    
    if response == 'y':
        try:
            shutil.rmtree(target_dir)
            print("✅ Node uninstalled successfully!")
            return True
        except Exception as e:
            print(f"❌ Uninstall failed: {str(e)}")
            return False
    else:
        print("❌ Uninstall cancelled.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_node()
    else:
        install_node() 