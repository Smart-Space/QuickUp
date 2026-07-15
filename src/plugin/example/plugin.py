"""
Example plugin for QuickUp
"""
from testlib import add


api = None


def echo_handler(task, runtime, *args, **kwargs):
    print(f'[example_plugin] Echo task received: {task}')
    print(runtime)
    print(f"[example_plugin] args: {args}")
    print(f"[example_plugin] kwargs: {kwargs}")
    print(f"[example_plugin] add: {add(1,1)}")
    return True


def toggle_main_handler(task, runtime, action):
    """
    参数形式为Python风格，例如：
    "hide" 或者 action="hide"
    如果函数签名只有task和runtime，依然可以通过task['args']获取 *args 和 **kwargs
    """
    print(f'[example_plugin] Toggle main task received: {task}')
    print(runtime)
    if action == 'hide':
        api.hide()
    elif action == 'show':
        api.show()
    else:
        api.hide()
        api.show()
    return True


def init(_api, manifest):
    global api
    api = _api
    print(f"[example_plugin] Initialized with manifest: {manifest}")
    api.register_task_type('echo', echo_handler)
    api.register_task_type('toggle_main', toggle_main_handler)
