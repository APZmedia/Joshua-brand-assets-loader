import importlib
import pkgutil
import traceback
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

package_dir = Path(__file__).parent.resolve()
nodes_dir = package_dir / "nodes"

# Dynamically import all node modules
for _, module_name, _ in pkgutil.iter_modules([str(nodes_dir)]):
    try:
        module = importlib.import_module(f".nodes.{module_name}", package=__name__)
        if hasattr(module, "NODE_CLASS_MAPPINGS") and hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
            NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
            print(f"[APZmedia] Successfully loaded node module: {module_name}")
        else:
            print(f"[APZmedia] Module {module_name} is missing required mappings")
    except Exception as e:
        print(f"[APZmedia] ERROR Failed to load node module {module_name}:")
        traceback.print_exc()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
