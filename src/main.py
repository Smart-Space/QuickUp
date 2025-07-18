# QuickUp main file (main.py)
"""
QuickUp - a simple, fast, and easy to use applications starter kit.
Copyright (C) 2024-present <Smart-Space>(smart-space@qq.com|tsan-zane@outlook.com)
version: {datas.version}
license:
    Closed source before 3.0 version
    GPLv3 and LGPLv3 since 3.0 version
author: smart-space(https://smart-space.com.cn/)

Licensed under the GPLv3 and LGPLv3 Licenses. (since 3.0 version)
	<QuickUp - a simple, fast, and easy to use applications starter kit.>
    Copyright (C) <2025-present>  <Smart-Space>(smart-space@qq.com|tsan-zane@outlook.com)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU (Lesser) General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU (Lesser) General Public License for more details.

    You should have received a copy of the GNU (Lesser) General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tkinter as tk
import sys
import os
import ctypes
import signal
import argparse

from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import ui.tasks as taskslib
from ui.tasks import initial_tasks_view, create_task, search_tasks, refresh_tasks_view
from ui.about import show_about
from ui.setting import show_setting
import config
from ui import editor
from ui import utils
import datas
from runner.runtask import run_task
from runner.runtip import init_tip
from runner.update import installerexe, auto_check_update, update_program, update_QuickUp
from runner import create_lnk, hotkey

from cppextend.QUmodule import init_tray, remove_tray

# 设置程序所在目录为工作目录
rootpath=sys.path[0]
os.chdir(rootpath)

parser = argparse.ArgumentParser(description='QuickUp - a simple, fast, and easy to use applications starter kit.')
parser.add_argument('-w', '--workspace', type=str, default='.', help='工作目录')
parser.add_argument('-t', '--task', type=str, default='', help='运行任务')
parser.add_argument('-s', '--silent', action='store_true', help='静默模式，不显示UI（仅可缩小化到托盘时可用）')
args = parser.parse_args()

if args.workspace in ('', '.', None):
    workspace = './tasks/'
    workname = ''
else:
    workspace = './tasks/' + args.workspace + '/'
    # 判断目录是否存在
    if not os.path.exists(workspace):
        sys.exit()
    workname = ' {' + args.workspace + '}'
datas.workspace = workspace

if args.task not in ('', None):
    # 存在任务，则直接执行任务，然后退出
    taskPath = workspace + args.task + '.json'
    if not os.path.exists(taskPath):
        sys.exit()
    # 若存在子线程，不保护退出
    run_task(args.task, deamon=False)
    sys.exit()

thisName = "QuickUp" + workname
hwnd = ctypes.windll.user32.FindWindowW(None, thisName)
if hwnd:
    ctypes.windll.user32.ShowWindow(hwnd, 9)
    ctypes.windll.user32.SetForegroundWindow(hwnd)
    sys.exit()

def about_workspace(e):
    d = Dialog(root, "info", config.settings['general']['theme'])
    utils.show_dialog(d, "关于工作区", "当前工作区：" + args.workspace, "msg", config.settings['general']['theme'])


if os.path.exists(installerexe):
    os.remove(installerexe)

config.init_config()
init_tip()


def close_root():
    config.save_config()
    remove_tray()
    root.destroy()
datas.root_callback = close_root

def close_root_check():
    if config.settings['general']['closeToTray']:
        root.withdraw()
        if workname == '':
            hotkey.start_listen(show_from_tray)
    else:
        close_root()

def show_from_tray():
    root.deiconify()
    root.attributes("-topmost", True)
    root.update()
    root.attributes("-topmost", False)
    root.focus_set()
    taskEntry.focus_set()

def show_window():
    root.deiconify()
    if workname == '':
        hotkey.pause_listen()

def signal_handler(signal, frame):
    close_root()
signal.signal(signal.SIGINT, signal_handler)


def run_this_task(e):
    # 运行选中的任务
    taskindex = taskView.getsel()
    if taskindex != -1:
        run_task(taskslib.tasknames[taskindex])

def edit_this_task(e):
    # 编辑选中的任务
    taskindex = taskView.getsel()
    if taskindex != -1:
        taskslib.edit_task(taskslib.tasknames[taskindex])

def next_task_view(e):
    # 选中下一个任务
    taskindex = taskView.getsel()
    taskView.select(taskindex+1)

def prev_task_view(e):
    # 选中上一个任务
    taskindex = taskView.getsel()
    taskView.select(taskindex-1)


def show_task_error(e):
    # 显示任务执行错误
    d = Dialog(root, "error", config.settings['general']['theme'])
    utils.show_dialog(d, f"任务执行错误", datas.root_error_message, "msg", config.settings['general']['theme'])
    datas.root_error_message = None


loading = False
original_text = ''
search_timer = None
def if_taskEntry_empty(text):
    # 任务列表搜索
    global original_text, loading, search_timer
    if loading:
        return
    if search_timer is not None:
        search_timer.cancel()
    loading = True
    if text == '' and original_text != '':
        search_tasks('')
    else:
        root.after(700, lambda text=text: go_search_tasks(text))
    original_text = text
    loading = False

def go_search_tasks(text:str):
    if taskVar.get() == text:
        search_tasks(text, True)


root = tk.Tk()
datas.root = root

width = 500
height = 700
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2 - 50)
root.geometry(geometry)
if args.silent and config.settings['general']['closeToTray']:
    # 静默模式，不显示UI，最小化到托盘
    close_root_check()
else:
    root.attributes("-topmost", True)
    root.update()
    root.focus_set()
    root.attributes("-topmost", False)

root.iconbitmap('./logo.ico')
root.title(thisName)
root.resizable(False, False)
root.update()
if config.settings['general']['topMost']:
    root.attributes("-topmost", True)

ui = BasicTinUI(root)
ui.pack(fill=tk.BOTH, expand=True)
if config.settings['general']['theme'] == 'dark':
    utils.set_window_dark(root)
    theme = TinUIDark(ui)
else:
    theme = TinUILight(ui)
uixml = TinUIXml(theme)
uixml.environment({
    'create_task': create_task,
    'setting': show_setting,
    'about': show_about,
    'about_workspace': about_workspace,
    'create_workspace_lnk': lambda e: create_lnk.create_workspace_lnk(root, args.workspace),
})
if thisName == "QuickUp":
    with open("./ui-asset/main.xml", "r", encoding="utf-8") as f:
        uixml.loadxml(f.read())
else:
    with open("./ui-asset/main-part.xml", "r", encoding="utf-8") as f:
        uixml.loadxml(f.read())
taskEntry = uixml.tags["taskEntry"][0]
taskEntry.focus_set()
taskEntry.bind("<Return>", lambda e: search_tasks(taskEntry.get()))
taskVar = taskEntry.var
taskVar.trace_add("write", lambda *args: if_taskEntry_empty(taskVar.get()))
taskView = uixml.tags["taskView"][-2]# listview functions
# settingbutton = uixml.tags["settingbutton"][-2]

editor.init_editor()
root.protocol("WM_DELETE_WINDOW", close_root_check)

if config.settings['general']['checkUpdate']:
    def __auto_update_available(e):
        # 自动更新提示
        update_program(root)
    def __update_ready(e):
        # 下载完成提示
        d = Dialog(root, "question", config.settings['general']['theme'])
        res = utils.show_dialog(d, "更新准备就绪", "新版安装软件下载完成，是否安装？\n（需要退出软件）", "msg", config.settings['general']['theme'])
        if res:
            update_QuickUp()
    root.update()
    root.bind("<<UpdateAvailable>>", __auto_update_available)
    root.bind("<<UpdateReady>>", __update_ready)
    auto_check_update(root)

def regeometry(e):
    # 应对从最小化到恢复正常
    root.unbind("<Visibility>")
    root.geometry('500x700')
    try:
        root.bind("<Visibility>", regeometry)
    except:
        pass
root.bind("<Visibility>", regeometry)

init_tray(root.winfo_id(), thisName, show_window, show_about, close_root)

initial_tasks_view(taskView, root)# 初始化任务列表

root.bind("<Control-r>", lambda e: refresh_tasks_view())
root.bind("<Control-n>", create_task)
root.bind("<Control-i>", show_setting)
root.bind("<Control-q>", lambda e: close_root_check())
root.bind("<Shift-Return>", run_this_task)
root.bind("<Control-e>", edit_this_task)
root.bind("<Up>", prev_task_view)
root.bind("<Down>", next_task_view)

root.bind("<<RunCmdError>>", show_task_error)

root.mainloop()
