

"""
Velora Agent — Plugin Dispatcher
Dynamically loads and executes plugins within secure dispatch routines.
"""

import importlib.util
import os
import traceback
from types import ModuleType
from typing import Any, Dict, Callable
from config.audit_logger import log_event

PLUGIN_DIRECTORY = "./plugins"

class PluginLoadError(Exception):
    pass

class PluginDispatcher:
    def __init__(self, plugin_dir: str = PLUGIN_DIRECTORY):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, ModuleType] = {}
        self.registry: Dict[str, Callable] = {}
        self.load_plugins()

    def load_plugins(self) -> None:
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py"):
                plugin_name = filename[:-3]
                path = os.path.join(self.plugin_dir, filename)

                try:
                    spec = importlib.util.spec_from_file_location(plugin_name, path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.plugins[plugin_name] = module

                    if hasattr(module, "register"):
                        funcs = module.register()
                        if isinstance(funcs, dict):
                            self.registry.update(funcs)

                    log_event("plugin_loaded", {"plugin": plugin_name})

                except Exception as e:
                    log_event("plugin_load_error", {
                        "plugin": plugin_name,
                        "error": str(e),
                        "trace": traceback.format_exc()
                    })
                    continue

    def invoke(self, name: str, *args, **kwargs) -> Any:
        if name not in self.registry:
            log_event("plugin_not_found", {"plugin_function": name})
            raise PluginLoadError(f"Plugin function '{name}' not found in registry.")

        try:
            result = self.registry[name](*args, **kwargs)
            log_event("plugin_invoked", {"function": name})
            return result
        except Exception as e:
            log_event("plugin_execution_error", {
                "function": name,
                "error": str(e),
                "trace": traceback.format_exc()
            })
            raise

# Example usage:
# dispatcher = PluginDispatcher()
# result = dispatcher.invoke("do_something", param1, param2)