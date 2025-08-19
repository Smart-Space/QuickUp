# ./runner/hotkey.py
"""
热键监听模块，当QuickUp主界面位于托盘时启用
"""
import atexit

import config
from cppextend.QUmodule import start_hotkey, stop_hotkey

reg = None
def start_listen(command=None):
    # 开始监听热键
    global reg
    fsModifiers = config.settings['advanced']['callUp'][0]
    vk = config.settings['advanced']['callUp'][1]
    start_hotkey(fsModifiers, vk, command)
    if not reg:
        reg = atexit.register(pause_listen)

def pause_listen():
    # 暂停监听热键
    stop_hotkey()