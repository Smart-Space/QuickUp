# ./runner/hotkey.py
"""
热键监听模块，当QuickUp主界面位于托盘时启用
"""
import ctypes
from ctypes import wintypes
from threading import Thread
import atexit
from time import sleep

import config

user32 = ctypes.windll.user32

ALT = 0x0001
SHIFT = 0x0002
CTRL = 0x0004
WM_HOTKEY = 0x0312


# 定义 MSG 结构体
class MSG(ctypes.Structure):
    _fields_ = [
        ('hwnd', wintypes.HWND),
        ('message', wintypes.UINT),
        ('wParam', wintypes.WPARAM),
        ('lParam', wintypes.LPARAM),
        ('time', wintypes.DWORD),
        ('pt', wintypes.POINT)
    ]
msg = MSG()

def check_hotkey_status(hotkey_id, fsModifiers, vk):
    # 检查热键是否已注册
    temp_result = user32.RegisterHotKey(None, hotkey_id, fsModifiers, vk)
    if temp_result:
        # 取消临时注册
        user32.UnregisterHotKey(None, hotkey_id)
        return False
    else:
        return True

def unregister_hotkey():
    # 注销热键
    user32.UnregisterHotKey(None, 1)

def create_hotkey():
    # 创建热键
    fsModifiers = config.settings['advanced']['callUp'][0]
    vk = config.settings['advanced']['callUp'][1]
    if check_hotkey_status(1, fsModifiers, vk):
        return None
    user32.RegisterHotKey(None, 1, fsModifiers, vk)
    atexit.register(unregister_hotkey)

running = False
task = None
def __listen_hotkey(command):
    # 监听热键
    flag = False
    create_hotkey()
    msgw = ctypes.byref(msg)
    while running:
        sleep(0.1)
        if not user32.PeekMessageW(msgw, None, 0, 0, 1):
            continue
        if msg.message == WM_HOTKEY and msg.wParam == 1:
            flag = True
        user32.TranslateMessage(msgw)
        user32.DispatchMessageW(msgw)
        if flag:
            break
    command()
    unregister_hotkey()

def start_listen(command=None):
    # 开始监听热键
    global task, running
    running = True
    task = Thread(name='listen_hotkey', target=__listen_hotkey, args=(command,))
    task.daemon = True
    task.start()

def pause_listen():
    # 暂停监听热键
    global task, running
    running = False
    if task:
        task = None