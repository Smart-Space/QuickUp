# ./ui/utils.py
"""
QuickUp UI Utils
"""
import os
from ctypes import windll, byref, c_int

from cppextend.QUmodule import create_link


def set_window_dark(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    if not hwnd:
        raise Exception("无法获取窗口句柄")
    windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        20,# DWMWA_USE_IMMERSIVE_DARK_MODE
        byref(c_int(1)),  # 启用自定义颜色
        4
    )

def show_dialog(dialog, title, content, wtype="msg", theme="light", input=""):
    dialog.update_idletasks()
    if theme == "dark":
        set_window_dark(dialog)
    if wtype == "msg":
        return dialog.initial_msg(title, content)
    elif wtype == "input":
        return dialog.initial_input(title, content, input)


quickup_path = os.path.abspath(".") + "\\QuickUp.exe"
desk_path = os.path.join(os.path.expanduser("~"), "Desktop")
workspace_icon_path = os.path.join(os.path.abspath("."), "share", "workspace.ico")
task_icon_path = os.path.join(os.path.abspath("."), "share", "task.ico")

def create_workspace_lnk(workspace):
    # 创建工作区快捷方式
    wsp_name = workspace.replace('/', '.').replace('\\', '.')
    wsp_relname = workspace
    cmd = f'-w "{wsp_relname}"'
    lnk_path = os.path.join(desk_path, f"{wsp_name}.lnk")
    create_link(quickup_path, cmd, lnk_path, workspace_icon_path)

def create_task_lnk(workname, task):
    # 创建任务快捷方式
    if workname in ('', '.', None):
        workname = '.'
    cmd = f'-w "{workname}" -t "{task}"'
    lnk_path = os.path.join(desk_path, f"{task}.lnk")
    create_link(quickup_path, cmd, lnk_path, task_icon_path)
