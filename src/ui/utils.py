# ./ui/utils.py
"""
QuickUp UI Utils
"""
import os
import subprocess
import ctypes
from ctypes import windll, byref, c_int

kernel32 = ctypes.windll.kernel32


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

workspace_lnk_command = """$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut("$env:USERPROFILE\\Desktop\\%wsp_name%.lnk")
$shortcut.TargetPath = "`"%quickup_path%\\QuickUp.exe`""
$shortcut.Arguments = "-w `"%wsp_relname%`""
$shortcut.IconLocation = "%quickup_path%\\share\\workspace.ico"
$shortcut.Save()
exit 0
"""
def create_workspace_lnk(workspace):
    # 创建工作区快捷方式
    cmd = workspace_lnk_command.replace("%wsp_name%", workspace.replace('/','.')).replace("%wsp_relname%", workspace).replace("%quickup_path%", os.path.abspath("."))
    kernel32.AllocConsole()
    p = subprocess.Popen('powershell -NoExit -Command chcp 65001', stdin=subprocess.PIPE, shell=True)
    p.communicate(cmd.encode('utf-8'))
    p.wait()
    kernel32.FreeConsole()

task_lnk_command = """$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut("$env:USERPROFILE\\Desktop\\%task_name%.lnk")
$shortcut.TargetPath = "`"%quickup_path%\\QuickUp.exe`""
$shortcut.Arguments = "-w `"%wsp_relname%`" -t `"%task_name%`""
$shortcut.IconLocation = "%quickup_path%\\share\\task.ico"
$shortcut.Save()
exit 0
"""
def create_task_lnk(workspace, task):
    # 创建任务快捷方式
    if workspace == "./tasks/":
        workspace = '.'
    else:
        workspace = workspace[8:-1]
    cmd = task_lnk_command.replace("%task_name%", task).replace("%wsp_relname%", workspace).replace("%quickup_path%", os.path.abspath("."))
    kernel32.AllocConsole()
    p = subprocess.Popen('powershell -NoExit -Command chcp 65001', stdin=subprocess.PIPE, shell=True)
    p.communicate(cmd.encode('utf-8'))
    p.wait()
    kernel32.FreeConsole()
