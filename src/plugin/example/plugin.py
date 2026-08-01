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


def built_task_callback(state, val=1):
    print(f'[example_plugin] Built task callback: state={state}, val={val}')

def run_my_task(task, runtime):
    # Test run_task_by_name: run existing task "test" if it exists
    try:
        api.run_task_by_name("test", callback=built_task_callback)
    except Exception as e:
        print(f"[example_plugin] run_task_by_name skipped: {e}")
    # Test run_task_built
    x1, y1, x2, y2 = api.worker_size()
    task_entries = [
        {"type": "wcmd", "target": "explorer", "args": "", "admin": False, "max": False, "min": False, "pos": [x1,y1,(x2-x1)//2,y2-y1], "zone_round": True},
        {"type": "tip", "tip": "Hello from plugin built task!", "wait": False, "show": True, "top": False},
    ]
    try:
        api.run_task_built("plugin_demo_built", task_entries, callback=built_task_callback)
    except Exception as e:
        print(f"[example_plugin] run_task_built error: {e}")


def init(_api, manifest):
    global api
    api = _api
    print(f"[example_plugin] Initialized with manifest: {manifest}")
    api.register_task_type('echo', echo_handler)
    api.register_task_type('toggle_main', toggle_main_handler)
    api.register_task_type('my_task', run_my_task)
