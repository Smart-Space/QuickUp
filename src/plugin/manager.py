"""
Plugin manager
"""
import builtins as py_builtins
import importlib.util
import os
import sys
import config
from threading import Lock
from plugin.api import PluginAPI
from plugin.manifest import load_manifest
from plugin.registry import PluginRegistry
from plugin.errors import format_plugin_error

ALLOWED_IMPORTS = {
    'json', 'os', 'subprocess', 'sys', 'time', 'datetime', 'hashlib', 'base64', 
    're', 'math', 'random', 'uuid', 'pathlib', 'urllib'
}

ALLOWED_BUILTINS = {
    'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 
    'tuple', 'set', 'range', 'enumerate', 'zip', 'map', 'filter', 
    'sorted', 'min', 'max', 'sum', 'abs', 'round', 'open', 'isinstance', 
    'hasattr', 'getattr', 'setattr', 'issubclass', 'Exception', 'BaseException',
    'SystemExit', 'ValueError', 'TypeError', 'RuntimeError', 'OSError',
    'FileNotFoundError', 'PermissionError', 'KeyError', 'AttributeError',
    'IndexError'
}

# 预加载白名单模块
_PRELOADED_MODULES = {}
for _mod in ALLOWED_IMPORTS:
    try:
        _PRELOADED_MODULES[_mod] = __import__(_mod)
    except ImportError:
        pass

# 预构建安全的内置函数字典
_SAFE_BUILTINS = {k: getattr(py_builtins, k) for k in ALLOWED_BUILTINS}


class PluginManager:
    """
    插件加载和管理
    """
    def __init__(self, base_dir:str):
        self.base_dir = base_dir
        self.registry = PluginRegistry()
        self.plugins = {}
        self.errors = {}
        self._manifests = {}
        self._discovered = False
        # 保护 self.plugins 和 self.errors 的写入
        self._lock = Lock()

    def _discover_plugins(self):
        """
        仅加载插件清单，不执行插件代码
        """
        if self._discovered:
            return

        plugins_to_index = []
        for name in os.listdir(self.base_dir):
            plugin_dir = os.path.join(self.base_dir, name)
            if os.path.isdir(plugin_dir):
                manifest_path = os.path.join(plugin_dir, 'manifest.json')
                if os.path.exists(manifest_path):
                    plugins_to_index.append((name, plugin_dir, manifest_path))

        for item in plugins_to_index:
            self._index_one(*item)

        self._discovered = True

    def _index_one(self, name:str, plugin_dir:str, manifest_path:str):
        manifest = load_manifest(manifest_path)
        plugin_name = manifest.get('name', name)

        with self._lock:
            self._manifests[plugin_name] = {
                'name': name,
                'plugin_dir': plugin_dir,
                'manifest_path': manifest_path,
                'manifest': manifest,
            }

        for task_type in manifest.get('task_types', []):
            self.registry.task_sources[task_type] = plugin_name

    def _ensure_loaded(self, plugin_name:str, task_type:str=""):
        """
        确保插件已加载
        """
        with self._lock:
            if plugin_name in self.plugins:
                return

        plugin_info = self._manifests.get(plugin_name)
        if plugin_info is None:
            self._discover_plugins()
            plugin_info = self._manifests.get(plugin_name)
            if plugin_info is None:
                return

        try:
            self._load_one(plugin_info['name'], plugin_info['plugin_dir'], plugin_info['manifest_path'])
        except Exception as e:
            if task_type:
                with self._lock:
                    self.errors[task_type] = format_plugin_error(e)

    def _load_one(self, name:str, plugin_dir:str, manifest_path:str):
        manifest = load_manifest(manifest_path)
        plugin_name = manifest.get('name', name)
        if not self._is_enabled(plugin_name):
            return
        # 原子性检查与加入
        with self._lock:
            if plugin_name in self.plugins:
                return

        entry = manifest['entry']
        entry_path = os.path.join(plugin_dir, entry)
        # 执行沙箱代码
        module_dict = self._exec_sandbox(plugin_name, plugin_dir, entry_path, manifest)
        
        api = PluginAPI(self.registry, plugin_name, manifest)
        self._apply_permissions(plugin_name, manifest)

        if 'init' in module_dict:
            module_dict['init'](api, manifest)

        # 最终写入
        with self._lock:
            self.plugins[plugin_name] = {
                'manifest': manifest,
                'module': module_dict,
            }

    def _exec_sandbox(self, name:str, plugin_dir:str, path:str, manifest:dict) -> dict:
        # 纯沙箱执行，返回包含插件定义的字典
        if not os.path.exists(path):
            raise FileNotFoundError(f"plugin entry not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        allowed_local_modules = set(manifest.get('modules', []))

        safe_globals = {
            '__name__': f"plugin_{name}",
            '__file__': path,
            '__builtins__': {
                **_SAFE_BUILTINS,
                '__import__': self._restricted_import_factory(plugin_dir, allowed_local_modules),
            },
        }
        # 注入预加载的安全模块
        safe_globals.update(_PRELOADED_MODULES)

        # 执行代码并将结果存入局部字典
        exec(code, safe_globals)
        return safe_globals

    @staticmethod
    def _restricted_import_factory(plugin_dir:str, allowed_local_modules:set[str]):
        def _restricted_import(name:str, globals=None, locals=None, fromlist=(), level=0):
            if level == 0 and name in ALLOWED_IMPORTS:
                return py_builtins.__import__(name, globals, locals, fromlist, level)

            if level == 0 and name in allowed_local_modules:
                module = PluginManager._load_local_module(plugin_dir, name)
                if fromlist:
                    return module
                top_level = name.split('.', 1)[0]
                return sys.modules.get(top_level, module)

            raise ImportError(f"plugin cannot import: {name}")

        return _restricted_import

    @staticmethod
    def _load_local_module(plugin_dir:str, module_name:str):
        module_path = os.path.join(plugin_dir, *module_name.split('.')) + '.py'
        if not os.path.exists(module_path):
            # 尝试加载包形式的模块
            package_init = os.path.join(plugin_dir, *module_name.split('.'), '__init__.py')
            if os.path.exists(package_init):
                module_path = package_init
            else:
                raise ImportError(f"plugin local module not found: {module_name}")

        qualified_name = f"plugin_local_{os.path.basename(plugin_dir)}_{module_name}"
        cached = sys.modules.get(qualified_name)
        if cached is not None:
            return cached

        spec = importlib.util.spec_from_file_location(qualified_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"plugin local module cannot be loaded: {module_name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified_name] = module
        spec.loader.exec_module(module)
        return module

    def _apply_permissions(self, plugin_name:str, manifest:dict):
        permissions = manifest.get('permissions', [])
        for perm in permissions:
            self.registry.register_permission(perm, f"{plugin_name}: {perm}")

    def _is_enabled(self, plugin_name:str) -> bool:
        plugin_cfg = config.settings['storage'].get('plugins', {})
        state = plugin_cfg.get(plugin_name, {})
        return state.get('enabled', True)

    def get_task_handler(self, task_type:str):
        handler = self.registry.get_task_handler(task_type)
        if handler is None:
            owner = self.registry.task_sources.get(task_type)
            if owner is None:
                self._discover_plugins()
                owner = self.registry.task_sources.get(task_type)
            if owner is None:
                self.errors[task_type] = "plugin not found for task type"
                return None
            self._ensure_loaded(owner, task_type)
            handler = self.registry.get_task_handler(task_type)
            if handler is None:
                if self.errors.get(task_type) is None:
                    self.errors[task_type] = "plugin failed to load or register task type"
                return None
        owner = self.registry.task_sources.get(task_type)
        if owner and not self._is_enabled(owner):
            self.errors[task_type] = "plugin not enabled for task type"
            return None
        return handler


plugin_dir = os.path.join(os.path.expandvars('%APPDATA%'), 'QuickUp', 'plugins')
plugin_manager = PluginManager(plugin_dir)
