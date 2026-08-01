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

    def run_task_by_name(self, name:str, deamon:bool=True, callback=None):
        """
        Run an existing task by its name.
        name: task name (without .json extension).
        """
        from runner.runtask import run_task
        run_task(name, deamon=deamon, callback=callback)

    def worker_size(self):
        """
        Get the screen worker area size (usable area excluding taskbar).
        return: tuple (left, top, right, bottom)
        """
        from cppextend.QUmodule import worker_size
        return worker_size()

    def run_task_built(self, name:str, tasks:list, cwd:str='', deamon:bool=True, callback=None):
        """
        Build and run a task from provided task entry data without creating a task file.
        tasks: list of task entry dicts matching editor get() output format, e.g.:
            {"type":"cmd","target":"...","args":"...","admin":False,...}
            {"type":"tip","tip":"...","wait":False,"show":True,"top":False}
            {"type":"cmds","cmds":[...],"cmd":"cmd","wait":False}
            {"type":"task","task":"..."}
            {"type":"wsp","name":"..."}
            {"type":"plugin","name":"...","args":"...","wait":False}
        """
        from runner.runtask import run_task_data
        run_task_data(name, tasks, cwd=cwd, deamon=deamon, callback=callback)
