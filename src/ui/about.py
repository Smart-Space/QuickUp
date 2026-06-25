# ./ui/about.py
"""
QuickUp关于界面
release
- https://github.com/Smart-Space/QuickUp/releases/
- https://gitee.com/captorking/QuickUp/releases/
"""
import tkinter as tk
from webbrowser import open as webopen
import subprocess

from tinui import BasicTinUI, TinUIXml
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from ui.utils import set_window_dark
import config
import datas

aboutwindow = False
root = None

def close_about():
    root.withdraw()

def open_url(_):
    url = "https://quickup.smart-space.com.cn/"
    webopen(url)

def open_doc(_):
    url = "https://quickup.smart-space.com.cn/document/"
    webopen(url)

def open_log(_):
    subprocess.Popen(f'start "" ./NEWS.txt', shell=True)

def show_about(e=None):
    global aboutwindow, root
    if aboutwindow:
        root.deiconify()
        return
    aboutwindow = True
    root = tk.Toplevel()
    root.title("关于QuickUp")
    # 居中显示
    width = int(500*datas.scale_factor)
    height = int(300*datas.scale_factor)
    x = (root.winfo_screenwidth() - width) / 2
    y = (root.winfo_screenheight() - height) / 2
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.protocol("WM_DELETE_WINDOW", close_about)
    root.iconbitmap('./logo.ico')
    root.resizable(False, False)
    root.update_idletasks()
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        set_window_dark(root)
    else:
        theme = TinUILight
    root.focus_force()

    ui = BasicTinUI(root, background='#f3f3f3')
    ui.set_scale(datas.scale_factor)
    ui.pack(fill=tk.BOTH, expand=True)
    uixml = TinUIXml(theme(ui, accent=config.settings['general']['accentColorD'] if config.settings['general']['theme'] == 'dark' else config.settings['general']['accentColorL']))
    uixml.funcs.update({"open_url": open_url, "open_doc": open_doc, 'open_log': open_log})
    with open('./ui-asset/about.xml', 'r', encoding='utf-8') as f:
        uixml.loadxml(f.read())
