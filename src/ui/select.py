# ./ui/select.py
"""
无论设置如何，QuickUp都会开辟一段共享内存存放已启动的QuickUp工作区窗口句柄。
只有根工作区的QuickUp才会尝试监听热键，当获得大于一个窗口句柄的共享内存时，会弹出窗口选择对话框。
"""
import tkinter as tk
from tinui import BasicTinUI, ExpandPanel, HorizonPanel, VerticalPanel
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from ui.utils import set_window_dark, bind_shortcuts
import config
import datas
from cppextend.QUmodule import priority_window, window_no_icon

root = None
listview = None
theme = None
accent_color = None

def close_select(e=None):
    root.withdraw()

def load_titles():
    listview.clear()
    for title in datas.titles:
        cui, _, cuixml, _ = listview.add()
        del cuixml
        cuit = theme(cui, accent=accent_color)
        titlename = title[0]
        if titlename != "QuickUp":
            titlename = titlename[9:-1]
        cuit.add_title((endx, endy), titlename, anchor='w')

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
    priority_window(hwnd)
    close_select()

def show_select():
    global root, theme, listview, endx, endy, accent_color
    if root:
        root.deiconify()
        root.focus_force()
        load_titles()
        return
    endx = int(5*datas.scale_factor)
    endy = int(40*datas.scale_factor)
    root = tk.Toplevel()
    root.title("选择一个QuickUp工作区")
    root.attributes("-topmost", True)
    width = int(500*datas.scale_factor)
    height = int(500*datas.scale_factor)
    x = (root.winfo_screenwidth() - width) / 2
    y = (root.winfo_screenheight() - height) / 2 - int(50*datas.scale_factor)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.protocol("WM_DELETE_WINDOW", close_select)
    root.iconbitmap('./logo.ico')
    root.resizable(False, False)
    root.update_idletasks()
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        set_window_dark(root)
        accent_color = config.settings['general']['accentColorD']
    else:
        theme = TinUILight
        accent_color = config.settings['general']['accentColorL']
    root.focus_force()
    window_no_icon(root.winfo_id())

    ui = BasicTinUI(root)
    ui.set_scale(datas.scale_factor)
    ui.pack(fill=tk.BOTH, expand=True)
    uit = theme(ui, accent=accent_color)

    vp = VerticalPanel(ui)

    listviewt = uit.add_listview((0,0), linew=int(80*datas.scale_factor), num=0)
    listview = listviewt[-2]
    ep = ExpandPanel(ui, listviewt[-1], padding=(0,5,0,0))
    vp.add_child(ep, weight=1)

    hp = HorizonPanel(ui, spacing=10)
    vp.add_child(hp, 30)
    btn1 = uit.add_accentbutton((0,0), "确定", command=select_workspace)[-1]
    btn2 = uit.add_button2((0,0), "取消", command=close_select)[-1]
    bep1 = ExpandPanel(ui, btn1)
    bep2 = ExpandPanel(ui, btn2)
    hp.add_child(bep1, weight=1)
    hp.add_child(bep2, weight=1)

    vp.update_layout(int(5*datas.scale_factor), int(5*datas.scale_factor), int(495*datas.scale_factor), int(495*datas.scale_factor))

    select_shortcuts = config.get_shortcuts('select', config.DEFAULT_SHORTCUTS['select'])
    bind_shortcuts(root, select_shortcuts, {
        'next': select_next,
        'prev': select_prev,
        'confirm': select_workspace,
        'close': close_select,
    })

    root.update_idletasks()
    load_titles()
