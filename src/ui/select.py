# ./ui/select.py
"""
无论设置如何，QuickUp都会开辟一段共享内存存放已启动的QuickUp工作区窗口句柄。
只有根工作区的QuickUp才会尝试监听热键，当获得大于一个窗口句柄的共享内存时，会弹出窗口选择对话框。
"""
import tkinter as tk
import ctypes
user32 = ctypes.windll.user32
from tinui import BasicTinUI, ExpandPanel, HorizonPanel, VerticalPanel
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from ui.utils import set_window_dark
import config
import datas

root = None
listview = None
theme = None

def close_select(e=None):
    root.withdraw()

def load_titles():
    listview.clear()
    for title in datas.titles:
        cui, _, cuixml, _ = listview.add()
        del cuixml
        cuit = theme(cui)
        cuit.add_title((5,40), title[0], anchor='w')

def select_next(e):
    taskindex = listview.getsel()
    listview.select(taskindex+1)

def select_prev(e):
    taskindex = listview.getsel()
    listview.select(taskindex-1)

def select_workspace(e):
    taskindex = listview.getsel()
    if taskindex == -1:
        return
    hwnd = datas.titles[taskindex][1]
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    close_select()

def show_select():
    global root, theme, listview
    if root:
        root.deiconify()
        root.focus_force()
        load_titles()
        return
    root = tk.Toplevel()
    root.title("选择一个QuickUp工作区")
    root.attributes("-topmost", True)
    width = 500
    height = 500
    x = (root.winfo_screenwidth() - width) / 2
    y = (root.winfo_screenheight() - height) / 2 - 50
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.protocol("WM_DELETE_WINDOW", close_select)
    root.iconbitmap('./logo.ico')
    root.resizable(False, False)
    root.update_idletasks()
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        set_window_dark(root)
    else:
        theme = TinUILight
    root.focus_force()
    rootid = user32.GetParent(root.winfo_id())
    windowlong = user32.GetWindowLongW(rootid, -16)
    windowlong &= ~0x00080000
    user32.SetWindowLongW(rootid, -16, windowlong)

    ui = BasicTinUI(root)
    ui.pack(fill=tk.BOTH, expand=True)
    uit = theme(ui)

    vp = VerticalPanel(ui)

    listviewt = uit.add_listview((0,0), num=0)
    listview = listviewt[-2]
    ep = ExpandPanel(ui, listviewt[-1], padding=(0,0,0,-5))
    vp.add_child(ep, weight=1)

    hp = HorizonPanel(ui, spacing=10)
    vp.add_child(hp, 30)
    btn1 = uit.add_accentbutton((0,0), "确定", command=select_workspace)[-1]
    btn2 = uit.add_button2((0,0), "取消", command=close_select)[-1]
    bep1 = ExpandPanel(ui, btn1)
    bep2 = ExpandPanel(ui, btn2)
    hp.add_child(bep1, weight=1)
    hp.add_child(bep2, weight=1)

    vp.update_layout(5,5,495,495)

    root.bind('<Down>', select_next)
    root.bind('<Up>', select_prev)
    root.bind('<Return>', select_workspace)
    root.bind('<Escape>', close_select)

    load_titles()
