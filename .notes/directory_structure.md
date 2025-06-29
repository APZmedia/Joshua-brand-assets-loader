# Directory Structure

## Root Level
- **`__init__.py`**: Package initialization file for the ComfyUI extension
- **`setup.py`**: Package configuration and installation setup
- **`README.md`**: Project documentation (currently minimal)
- **`.cursorrules`**: AI collaboration rules and context loading instructions
- **`.cursorignore`**: Files to exclude from AI analysis
- **`.gitignore`**: Git ignore patterns
- **`.gitattributes`**: Git attributes configuration

## Core Directories

### `nodes/`
**Purpose**: Contains all ComfyUI custom node implementations
- **`brand_asset_loader.py`**: Node for loading and managing brand assets
- **`logo_placement_node.py`**: Node for placing logos in images

### `.notes/`
**Purpose**: AI collaboration and project documentation
- **`project_overview.md`**: High-level project context and goals
- **`task_list.md`**: Actionable tasks and their status
- **`directory_structure.md`**: This file - codebase mental map
- **`meeting_notes.md`**: Interaction log and decision tracking

## File Descriptions

### Core Implementation Files
- **`nodes/brand_asset_loader.py`**: Implements `APZmediaBrandAssetLoader` class
  - Handles loading of brand assets from various sources
  - Processes and validates asset files
  - Provides asset metadata and processing options

- **`nodes/logo_placement_node.py`**: Implements `APZmediaLogoPlacement` class
  - Places logos on images with positioning controls
  - Handles logo scaling, positioning, and blending
  - Supports various output formats

### Configuration Files
- **`setup.py`**: Package configuration with entry points
  - Defines package metadata (name, version, author)
  - Registers ComfyUI nodes via entry points
  - Specifies dependencies and Python version requirements

## Development Workflow

### For AI Collaboration
1. **Context Loading**: AI reads `.notes/project_overview.md` and `.notes/task_list.md`
2. **Code Understanding**: AI reviews `.notes/directory_structure.md` for codebase map
3. **Task Execution**: AI follows `.cursorrules` for safe code changes
4. **Documentation**: AI updates `.notes/meeting_notes.md` with decisions

### For Human Developers
1. **Setup**: Install package in ComfyUI environment
2. **Development**: Modify nodes in `nodes/` directory
3. **Testing**: Test nodes in ComfyUI interface
4. **Documentation**: Update `.notes/` files as needed

## Future Structure Considerations

### Potential Additions
- **`tests/`**: Unit tests and integration tests
- **`examples/`**: Sample workflows and usage examples
- **`docs/`**: Detailed documentation and tutorials
- **`assets/`**: Sample brand assets for testing
- **`scripts/`**: Utility scripts for development and deployment

### Extension Points
- **`plugins/`**: Third-party asset provider plugins
- **`formats/`**: Additional asset format handlers
- **`presets/`**: Pre-configured logo placement presets 