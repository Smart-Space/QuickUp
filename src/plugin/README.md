# QuickUp Plugin Developer Guide

This guide explains the QuickUp plugin architecture, development flow, and security constraints.

## 1) Plugin Layout

Plugins must be placed in:
`%APPDATA%\QuickUp\plugins\<plugin_id>\`

Required files:
- `manifest.json`: Plugin metadata and declarations.
- `<entry>.py`: The main logic script (defined in manifest).

## 2) Manifest Specification

`manifest.json` required fields:
```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "entry": "plugin.py"
}
```

Optional fields:
- `"permissions": ["perm1", "perm2"]`: List of declared permissions.
- `"task_types": ["task1", "task2"]`: Custom task types the plugin will register.
- `"modules": ["helper1", "pkg.helper2"]`: Local modules inside the plugin directory that the entry script may import.

**Crucial:** Any task type registered via the API **must** be declared here, otherwise a `ValueError` will be raised during initialization.

## 3) Entry Module

The entry module must expose an `init` function:
```python
def init(api, manifest):
    # Register handlers here
    ...
```

## 4) Security & Sandbox

QuickUp executes plugins in a restricted environment to ensure system stability:

- **Restricted Imports**: Only modules in the `ALLOWED_IMPORTS` whitelist (e.g., `os`, `sys`, `json`, `pathlib`, `urllib`, etc.) can be imported.
- **Local Modules**: The entry script may import modules declared in `manifest.json` under `modules`, and they must live inside the plugin directory. Use `from <module> import <function>`.
- **Restricted Built-ins**: Only a subset of Python built-ins (`ALLOWED_BUILTINS`) is available.
- **Isolation**: Plugins are lazily loaded only when a registered task is triggered.

## 5) API Surface (`PluginAPI`)

- `register_task_type(name, handler)`: Registers a handler for a specific task type.
- `register_permission(name, description="")`: Declares a permission.
- `hide()` / `show()`: Controls the main application window visibility.
- `get_config()` / `set_config(data)`: Manages persistent plugin-specific configuration stored in the global settings.

### Task Handler Signature
```python
def handler(task: dict, runtime: dict) -> bool:
    # task: The task definition from JSON
    # runtime: Context containing 'name', 'cwd', 'deamon'
    return True # Return True for success, False for failure
```

or

```python
def handler(task:dict, runtime:dict, *args, **kwargs) -> bool:
    # you can also get `args:list` and `kwargs:dict` from task['args']
    return True
```

## 6) Lifecycle

1. **Discovery**: `PluginManager` scans directories and indexes `task_types` from manifests without executing code.
2. **Trigger**: When a task with a plugin-provided type is run, the manager ensures the plugin is loaded.
3. **Execution**: The entry script is executed in the sandbox $\rightarrow$ `init()` is called $\rightarrow$ the handler is retrieved and executed.

## 7) Example
See `plugin/example/` for a complete implementation.
