# ./ui/utils.py
"""
QuickUp UI Utils
"""
import os
import subprocess
import ctypes
from ctypes import windll, byref, Structure, c_int
from ctypes.wintypes import COLORREF, DWORD
from runner.runwcmd import run_wcmd

kernel32 = ctypes.windll.kernel32

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_TOPMOST = 0x8
WS_EX_APPWINDOW = 0x40000
WS_EX_TOOLWINDOW = 0x80

# 定义窗口扩展样式
class DWMNCRENDERINGPOLICY:
    DWMNCRP_USEWINDOWSTYLE = 0
    DWMNCRP_DISABLED = 1
    DWMNCRP_ENABLED = 2
    DWMNCRP_LAS = 3

# 定义窗口颜色属性结构
class DWMWINDOWATTRIBUTE:
    DWMWA_NCRENDERING_ENABLED = 1
    DWMWA_NCRENDERING_POLICY = 2
    DWMWA_TRANSITIONS_FORCEDISABLED = 3
    DWMWA_ALLOW_NCPAINT = 4
    DWMWA_CAPTION_BUTTON_BOUNDS = 5
    DWMWA_NONCLIENT_RTL_LAYOUT = 6
    DWMWA_FORCE_ICONIC_REPRESENTATION = 7
    DWMWA_FLIP3D_POLICY = 8
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    DWMWA_HAS_ICONIC_BITMAP = 10
    DWMWA_DISALLOW_PEEK = 11
    DWMWA_EXCLUDED_FROM_PEEK = 12
    DWMWA_CLOAK = 13
    DWMWA_CLOAKED = 14
    DWMWA_FREEZE_REPRESENTATION = 15
    DWMWA_PASSIVE_UPDATE_MODE = 16
    DWMWA_USE_HOSTBACKDROPBRUSH = 17
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36
    DWMWA_BORDER_COLOR = 34

# 定义 DWM_COLORIZATION_PARAMS 结构
class DWM_COLORIZATION_PARAMS(Structure):
    _fields_ = [
        ("clrColor", DWORD),
        ("clrAfterGlow", DWORD),
        ("nIntensity", DWORD),
        ("clrAfterGlowBalance", DWORD),
        ("clrBlurBalance", DWORD),
        ("clrGlassReflectionIntensity", DWORD),
        ("nOpaqueBlend", DWORD)
    ]

# 定义窗口句柄
hwnd = None

def set_title_bar_color(root, color: int, text_color: int):
    global hwnd
    hwnd = windll.user32.GetParent(root.winfo_id())
    if not hwnd:
        raise Exception("无法获取窗口句柄")

    # 启用自定义非客户端区域渲染
    windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE,
        byref(c_int(2)),  # 启用自定义颜色
        4
    )

    # 设置标题栏颜色
    color_ref = COLORREF(color)
    windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWINDOWATTRIBUTE.DWMWA_CAPTION_COLOR,
        byref(color_ref),
        4
    )

    # 设置标题栏文本颜色
    text_color = COLORREF(text_color)  # 白色文本
    windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWINDOWATTRIBUTE.DWMWA_TEXT_COLOR,
        byref(text_color),
        4
    )

def on_ui_destroy(uixml):
    del uixml

def show_dialog(dialog, title, content, wtype="msg", theme="light", input=""):
    dialog.update_idletasks()
    if theme == "dark":
        set_title_bar_color(dialog, 0x202020, 0xFFFFFF)
    else:
        set_title_bar_color(dialog, 0xf3f3f3, 0x000000)
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
