# ./ui/utils.py
"""
QuickUp UI Utils
"""
import os

from cppextend.QUmodule import create_link, set_window_dark as __set_dark


def set_window_dark(root):
    __set_dark(root.winfo_id())

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
