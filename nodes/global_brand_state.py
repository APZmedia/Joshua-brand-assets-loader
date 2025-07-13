import torch
from typing import Dict, Any, Optional
import threading

class GlobalBrandState:
    """
    Global state manager for brand assets that can be accessed by any node.
    Thread-safe singleton pattern for storing brand assets globally.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GlobalBrandState, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._state = {
            # Logo assets with masks
            "logo_vertical_color": None,
            "logo_vertical_color_mask": None,
            "logo_vertical_mono": None,
            "logo_vertical_mono_mask": None,
            "logo_horizontal_color": None,
            "logo_horizontal_color_mask": None,
            "logo_horizontal_mono": None,
            "logo_horizontal_mono_mask": None,
            "logo_icon": None,
            "logo_icon_mask": None,
            
            # Font paths
            "font_primary": "",
            "font_primary_bold": "",
            "font_primary_italic": "",
            "font_secondary": "",
            "font_secondary_bold": "",
            "font_secondary_italic": "",
            "font_tertiary": "",
            "font_tertiary_bold": "",
            "font_tertiary_italic": "",
            
            # Brand metadata
            "color_palette": "[]",
            "brand_name": "Unknown Brand",
            "status_message": "No assets loaded",
            
            # Load status
            "is_loaded": False,
            "load_timestamp": None
        }
        self._initialized = True
    
    def set_brand_assets(self, assets: Dict[str, Any]) -> None:
        """Set all brand assets in global state."""
        with self._lock:
            for key, value in assets.items():
                if key in self._state:
                    self._state[key] = value
            self._state["is_loaded"] = True
            self._state["load_timestamp"] = torch.cuda.Event() if torch.cuda.is_available() else None
    
    def get_logo(self, logo_type: str, include_mask: bool = True) -> Any:
        """Get logo by type (vertical_color, vertical_mono, horizontal_color, horizontal_mono, icon)."""
        with self._lock:
            if include_mask:
                return self._state.get(f"logo_{logo_type}"), self._state.get(f"logo_{logo_type}_mask")
            return self._state.get(f"logo_{logo_type}")
    
    def get_font(self, font_type: str, variant: str = "") -> str:
        """Get font path by type (primary, secondary, tertiary) and variant (bold, italic)."""
        with self._lock:
            key = f"font_{font_type}"
            if variant:
                key += f"_{variant}"
            return self._state.get(key, "")
    
    def get_color_palette(self) -> str:
        """Get color palette JSON string."""
        with self._lock:
            return self._state.get("color_palette", "[]")
    
    def get_brand_name(self) -> str:
        """Get brand name."""
        with self._lock:
            return self._state.get("brand_name", "Unknown Brand")
    
    def get_status_message(self) -> str:
        """Get status message."""
        with self._lock:
            return self._state.get("status_message", "No assets loaded")
    
    def is_assets_loaded(self) -> bool:
        """Check if brand assets are loaded."""
        with self._lock:
            return self._state.get("is_loaded", False)
    
    def clear_state(self) -> None:
        """Clear all brand assets from global state."""
        with self._lock:
            for key in self._state:
                if key.startswith("logo_"):
                    self._state[key] = None
                elif key.startswith("font_"):
                    self._state[key] = ""
                elif key in ["color_palette", "brand_name", "status_message"]:
                    self._state[key] = "[]" if key == "color_palette" else "Unknown Brand" if key == "brand_name" else "No assets loaded"
            self._state["is_loaded"] = False
            self._state["load_timestamp"] = None
    
    def get_all_assets(self) -> Dict[str, Any]:
        """Get all brand assets as a dictionary."""
        with self._lock:
            return self._state.copy()

# Global instance
global_brand_state = GlobalBrandState() 