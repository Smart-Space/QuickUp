"""
QuickUp Plugin API
"""
from typing import Callable, Dict, Any

import config
import datas


class PluginAPI:
    """
    插件使用的API接口
    """
    def __init__(self, registry, plugin_name:str, manifest:Dict[str, Any]):
        self._registry = registry
        self._plugin_name = plugin_name
        self._manifest = manifest

    def register_task_type(self, name:str, handler:Callable):
        """
        Register a custom task type handler.
        handler signature: handler(task:dict, runtime:dict) -> bool
        """
        if self._manifest.get('task_types'):
            if name not in self._manifest.get('task_types', []):
                raise ValueError(f"task type not declared in manifest: {name}")
        self._registry.register_task_type(name, handler, self._plugin_name)

    def register_permission(self, name:str, description:str=""):
        """
        Register a permission name and description.
        """
        if self._manifest.get('permissions'):
            if name not in self._manifest.get('permissions', []):
                raise ValueError(f"permission not declared in manifest: {name}")
        self._registry.register_permission(name, description)

    def hide(self):
        """
        Request app hide.
        """
        if datas.app_controller:
            datas.app_controller.hide()

    def show(self):
        """
        Request app show.
        """
        if datas.app_controller:
            datas.app_controller.show()

    def get_config(self) -> Dict[str, Any]:
        """
        Read plugin config storage (shared storage dict).
        """
        all_cfg = config.settings['storage'].get('plugins', {})
        return all_cfg.get(self._plugin_name, {})

    def set_config(self, data:Dict[str, Any]):
        """
        Replace plugin config storage (shared storage dict).
        """
        all_cfg = config.settings['storage'].get('plugins', {})
        all_cfg[self._plugin_name] = data
        config.settings['storage']['plugins'] = all_cfg
        config.save_config()
