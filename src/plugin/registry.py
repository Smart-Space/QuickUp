"""
Plugin registry for task types and permissions
"""
from typing import Dict, Callable


class PluginRegistry:
    """
    插件提供的功能注册表
    """
    def __init__(self):
        self.task_types:Dict[str, Callable] = {}
        self.permissions:Dict[str, str] = {}
        self.task_sources:Dict[str, str] = {}

    def register_task_type(self, name:str, handler:Callable, plugin_name:str=""):
        self.task_types[name] = handler
        if plugin_name:
            self.task_sources[name] = plugin_name

    def register_permission(self, name:str, description:str=""):
        """
        permission实际上是一个权限提示，程序不做限制
        """
        self.permissions[name] = description

    def get_task_handler(self, name:str):
        return self.task_types.get(name)
