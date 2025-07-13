# Project Overview

## Goal
Build a ComfyUI extension that provides nodes for loading brand assets and dynamically placing logos in AI-generated images. This enables automated brand integration into AI workflows.

## Architecture

- **Framework:** ComfyUI (Python-based node system)
- **Extension Type:** Custom nodes for asset management and logo placement
- **Core Components:** 
  - Brand Asset Loader Node
  - Logo Placement Node
- **Dependencies:** Python 3.8+, ComfyUI core
- **Distribution:** Python package via pip/setuptools

## Key Features

- **Brand Asset Loading:** Load and manage brand assets (logos, colors, fonts) from various sources
- **Dynamic Logo Placement:** Automatically place logos in AI-generated images with positioning controls
- **ComfyUI Integration:** Seamless integration with existing ComfyUI workflows
- **Extensible Design:** Modular node architecture for easy extension

## Core Nodes

### APZmediaBrandAssetLoader
- **Purpose:** Comprehensive brand asset loader that handles all asset types in one node
- **Inputs:** 
  - API mode: Brand ID, API URL, authentication token (optional)
  - Manual mode: File paths for logos, fonts, and color palette JSON
- **Outputs:** All brand assets (5 logo variations, 3 font paths, color palette, brand metadata)
- **Features:** Dual loading modes (API/Manual), optional authentication, comprehensive error handling, consistent return types

### APZmediaLogoPlacement
- **Purpose:** Place logos dynamically in images
- **Inputs:** Base image, logo asset, placement parameters
- **Outputs:** Image with integrated logo

## Sample User Flow

### API Mode (Recommended)
1. User installs the extension in ComfyUI
2. User adds Brand Asset Loader node to workflow
3. User configures API settings (Brand ID, API URL, token optional)
4. Node automatically loads all brand assets (logos, fonts, colors)
5. User adds Logo Placement/Overlay nodes to workflow
6. User connects brand assets to logo placement nodes
7. Workflow generates images with integrated brand assets

### Manual Mode
1. User installs the extension in ComfyUI
2. User adds Brand Asset Loader node to workflow
3. User provides file paths for logos, fonts, and color palette JSON
4. Node loads and validates all provided assets
5. User adds Logo Placement/Overlay nodes to workflow
6. User connects brand assets to logo placement nodes
7. Workflow generates images with integrated brand assets

## Development Philosophy

- **AI-First:** Designed for AI collaboration and rapid iteration
- **ComfyUI Native:** Follows ComfyUI patterns and conventions
- **Extensible:** Easy to add new asset types and placement strategies
- **User-Friendly:** Intuitive node interfaces with clear documentation

## Target Users

- **Brand Managers:** Need consistent brand integration in AI workflows
- **Content Creators:** Want automated logo placement in generated content
- **Marketing Teams:** Require branded AI-generated materials
- **ComfyUI Developers:** Looking to extend workflows with brand capabilities 