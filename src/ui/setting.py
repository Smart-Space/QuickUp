# ./ui/setting.py
"""
QuickUp Setting UI
"""
import tkinter as tk
import os
import sys
import subprocess
from webbrowser import open as webopen
from urllib.request import urlopen
from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from cppextend.QUmodule import register_start, unregister_start, have_start_value, zone_try_times

import config
import datas
from ui.utils import set_window_dark, show_dialog
from runner.update import update_program, update_QuickUp


# 判断是否已经打开过设置窗口
settingwindow = False
root = None
theme = None
lastUI = None

# ==========常规设置==========
first_check_topmost = True
first_check_update = True
first_check_showhidden = True
def init_general():
    global gUI, first_check_topmost, first_check_update, first_check_showhidden
    gUI = BasicTinUI(root, background="#f3f3f3")
    gUI.place(x=0, y=60, width=600, height=540)
    gUIxml = TinUIXml(theme(gUI))
    blur_rank = list(range(101))
    for i in range(101):
        blur_rank[100-i] = str(i)
    gUIxml.datas.update({'blur_rank': blur_rank})
    gUIxml.funcs.update({'sel_theme': sel_theme, 'sel_blur': sel_blur, 'check_update': check_update,
                         "set_topmost": set_topmost, "auto_check_update": s_auto_check_update,
                         "sel_exit_mode": sel_exit_mode, 'sel_msc': sel_msc,
                         "show_hidden": set_show_hidden})
    with open("./ui-asset/setting-general.xml", "r", encoding="utf-8") as f:
        gUIxml.loadxml(f.read().replace('%VERSION%', datas.version))
    
    themeradio = gUIxml.tags["themeradio"][-2]
    nowtheme = config.theme_original
    if nowtheme == "light":
        themeradio.select(0)
    elif nowtheme == "dark":
        themeradio.select(1)
    else:
        themeradio.select(2)
    
    blurspin = gUIxml.tags["blurspin"][0]
    blurspin.delete(0, 'end')
    blurspin.insert(0, str(config.settings['general']['patternRank']))

    mscspin = gUIxml.tags["mscspin"][0]
    mscspin.delete(0, 'end')
    mscspin.insert(0, str(config.settings['general']['maxSearchCount']))
    
    tmcheck = gUIxml.tags["topmostcheck"][-2]
    isTopMost = config.settings['general'].get('topMost', False)
    if isTopMost:
        tmcheck.on()
    else:
        first_check_topmost = False
    
    hiddencheck = gUIxml.tags["hiddencheck"][-2]
    if config.settings['general']['showHidden']:
        hiddencheck.on()
    else:
        first_check_showhidden = False

    updatecheck = gUIxml.tags["updatecheck"][-2]
    if config.settings['general']['checkUpdate']:
        updatecheck.on()
    else:
        first_check_update = False
    
    exitradio = gUIxml.tags["exitradio"][-2]
    if config.settings['general'].get('closeToTray', True):
        exitradio.select(1)
    else:
        exitradio.select(0)

    root.bind("<<UpdateReady>>", __update_ready)
    root.bind("<<UpdateFailed>>", __update_failed)

def set_topmost(flag):
    # 设置窗口置顶
    global first_check_topmost
    if first_check_topmost:
        first_check_topmost = False
        return
    config.settings['general']['topMost'] = flag
    config.save_config()
    datas.root.attributes("-topmost", flag)

def s_auto_check_update(flag):
    # 自动检查更新
    global first_check_update
    if first_check_update:
        first_check_update = False
        return
    config.settings['general']['checkUpdate'] = flag
    config.save_config()

def __auto_update_available(e):
    # 自动更新提示
    d = Dialog(root, "question", config.settings['general']['theme'])
    res = show_dialog(d, "提示", "检测到新版本，是否下载？", "msg", config.settings['general']['theme'])
    if res:
        update_program(root)

def __update_ready(e):
    # 下载完成提示
    d = Dialog(root, "question", config.settings['general']['theme'])
    res = show_dialog(d, "更新准备继续", "新版安装软件下载完成，是否安装？\n（需要退出软件）", "msg", config.settings['general']['theme'])
    if res:
        update_QuickUp()

def __update_failed(e):
    # 下载失败提示
    d = Dialog(root, "error", config.settings['general']['theme'])
    show_dialog(d, "更新失败", "新版安装软件下载失败，请稍后再试！", "msg", config.settings['general']['theme'])

def check_update(e):
    # 检查更新
    if datas.is_msix:
        return
    url = "https://quickup.smart-space.com.cn/ver.txt"
    gUI.config(cursor="wait")
    gUI.update_idletasks()
    try:
        with urlopen(url, timeout=10) as f:
            new_version = f.read().decode('utf-8').strip()
        gUI.config(cursor="")
        now1, now2 = datas.version.split('.')
        new1, new2 = new_version.split('.')
        if int(new1) > int(now1) or (int(new1) == int(now1) and int(new2) > int(now2)):
            __auto_update_available(None)
        else:
            d = Dialog(root, "info", config.settings['general']['theme'])
            show_dialog(d, "提示", "当前已是最新版本！", "msg", config.settings['general']['theme'])
    except:
        gUI.config(cursor="")
        d = Dialog(root, "error", config.settings['general']['theme'])
        show_dialog(d, "网络错误", "检查更新失败，请稍后再试！", "msg", config.settings['general']['theme'])

def sel_exit_mode(mode):
    # 切换退出模式
    if mode == "退出应用":
        config.settings['general']['closeToTray'] = False
    else:
        config.settings['general']['closeToTray'] = True
    config.save_config()

def sel_theme(theme):
    # 切换主题
    if theme == "明亮":
        theme = "light"
    elif theme == "黑暗":
        theme = "dark"
    else:
        theme = "system"
    config.theme_original = theme
    config.save_config()

def sel_blur(blur):
    # 切换模糊搜索阈值
    datas.patternRank = int(blur)
    config.settings['general']['patternRank'] = int(blur)
    config.save_config()

def sel_msc(msc):
    # 切换最大搜索匹配结果数
    datas.maxSearchCount = int(msc)
    config.settings['general']['maxSearchCount'] = int(msc)
    config.save_config()

def set_show_hidden(tag):
    # 显示隐藏文件
    global first_check_showhidden
    if first_check_showhidden:
        first_check_showhidden = False
        return
    config.settings['general']['showHidden'] = tag
    config.save_config()


# ==========高级设置==========
first_dis_admin = True
first_auto_save = True
HK_CTRL = 0x0002
HK_ALT = 0x0001
HK_SHIFT = 0x0004
HK_Modifiers = []
HK_VK = 0x51 # 'Q'
def init_advanced():
    global aUI, first_dis_admin, first_auto_save, hkentry, snapretryentry
    aUI = BasicTinUI(root, background="#f3f3f3")
    aUIxml = TinUIXml(theme(aUI))
    aUIxml.funcs.update({'dis_admin': dis_admin, 'start_on_boot': start_on_boot,
                         'about_start_on_boot': about_start_on_boot, 'auto_save': auto_save,
                         'copy_path': copy_path, 'open_cmd_args': open_cmd_args,
                         'toggle_hk_ctrl': toggle_hk_ctrl, 'toggle_hk_alt': toggle_hk_alt,
                         'toggle_hk_shift': toggle_hk_shift, 'apply_hk': apply_hk,
                         'apply_snap_retry': apply_snap_retry})
    with open("./ui-asset/setting-advanced.xml", "r", encoding="utf-8") as f:
        aUIxml.loadxml(f.read())
    checkbox = aUIxml.tags["check"][-2]
    aUI.checkbox = checkbox
    if config.settings['advanced']['runWhenStart']:
        checkbox.on()
    admincheck = aUIxml.tags["admincheck"][-2]

    if config.settings['advanced']['disAdmin']:
        admincheck.on()
    else:
        first_dis_admin = False

    autosaveonoff = aUIxml.tags["autosaveonoff"][-2]
    if config.settings['advanced']['autoSave']:
        autosaveonoff.on()
    else:
        first_auto_save = False

    modifier_code = config.settings['advanced']['callUp'][0]
    if modifier_code & HK_CTRL:
        aUIxml.tags['b1'][-2].on()
    if modifier_code & HK_ALT:
        aUIxml.tags['b2'][-2].on()
    if modifier_code & HK_SHIFT:
        aUIxml.tags['b3'][-2].on()
    hkentry = aUIxml.tags["hkentry"][0]
    hkentry.insert(0, chr(config.settings['advanced']['callUp'][1]).upper())

    snapretryentry = aUIxml.tags["snapretryentry"][0]
    snapretryentry.insert(0, str(config.settings['advanced']['zoneRetryTimes']))

def auto_save(flag):
    # 自动保存
    global first_auto_save
    if first_auto_save:
        first_auto_save = False
        return
    config.settings['advanced']['autoSave'] = flag
    config.save_config()

def dis_admin(flag):
    # 禁用管理员权限
    global first_dis_admin
    if first_dis_admin:
        first_dis_admin = False
        return
    config.settings['advanced']['disAdmin'] = flag
    config.save_config()

def start_on_boot(flag):
    # 开机启动
    if flag:
        if not have_start_value("QuickUp"):
            register_start("QuickUp", f'"{sys.argv[0]}" -s')
    else:
        if have_start_value("QuickUp"):
            unregister_start("QuickUp")
    config.settings['advanced']['runWhenStart'] = flag
    config.save_config()

def about_start_on_boot(e):
    # 关于开机启动
    d = Dialog(root, "info", config.settings['general']['theme'])
    show_dialog(d, "开机启动", "QuickUp将尝试以静默模式启动，如果不允许QuickUp关闭到托盘，\n" \
                "则直接显示图形界面。\n\n" \
                "具体参数为 quickup -s", "msg", config.settings['general']['theme'])

def copy_path(e):
    # 复制路径
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    root.clipboard_clear()
    root.clipboard_append(path)

cmd_args_context = """
quickup [-w|--workspace] [-t|--task] [-s|--silent]\n
-w,--workspace: 打开指定工作区\n
-t,--task: 打开指定任务\n
-s,--silent: 静默模式启动（仅在可缩小到托盘时可用）
"""
def open_cmd_args(e):
    d = Dialog(root, "info", config.settings['general']['theme'])
    show_dialog(d, "QuicUp命令行参数", cmd_args_context, "msg", config.settings['general']['theme'])

def toggle_hk_ctrl(flag):
    if flag:
        HK_Modifiers.append(HK_CTRL)
    else:
        HK_Modifiers.remove(HK_CTRL)

def toggle_hk_alt(flag):
    if flag:
        HK_Modifiers.append(HK_ALT)
    else:
        HK_Modifiers.remove(HK_ALT)

def toggle_hk_shift(flag):
    if flag:
        HK_Modifiers.append(HK_SHIFT)
    else:
        HK_Modifiers.remove(HK_SHIFT)

def apply_hk(e):
    if len(HK_Modifiers) == 0:
        d = Dialog(root, "error", config.settings['general']['theme'])
        show_dialog(d, "错误", "热键功能键不能为空！", "msg", config.settings['general']['theme'])
        return
    ch:str = hkentry.get()
    if len(ch) != 1:
        d = Dialog(root, "error", config.settings['general']['theme'])
        show_dialog(d, "错误", "热键只能是一个字符！", "msg", config.settings['general']['theme'])
        return
    if ch.lower() >= 'a' and ch.lower() <= 'z':
        HK_VK = ord(ch.upper())
        hkentry.delete(0, 'end')
        hkentry.insert(0, ch.upper())
    else:
        d = Dialog(root, "error", config.settings['general']['theme'])
        show_dialog(d, "错误", "热键只能是一个字母！", "msg", config.settings['general']['theme'])
        return
    modifers = 0x0000
    for m in HK_Modifiers:
        modifers |= m
    config.settings['advanced']['callUp'] = (modifers, HK_VK)
    config.save_config()

def apply_snap_retry(e):
    # 重试布局次数
    res = snapretryentry.get()
    if res.isdigit() and int(res) >= 0:
        config.settings['advanced']['zoneRetryTimes'] = int(res)
        config.save_config()
        zone_try_times(int(res))
    else:
        d = Dialog(root, "error", config.settings['general']['theme'])
        show_dialog(d, "错误", "重试次数需要为正整数", "msg", config.settings['general']['theme'])


# ==========存储设置==========
storageTree = None
nowselected = None
storageContent = None
def init_storage():
    global sUI, sthemeUI, sUIxml
    sUI = BasicTinUI(root, background="#f3f3f3")
    sthemeUI = theme(sUI)
    sUIxml = TinUIXml(sthemeUI)
    sUIxml.funcs.update({'refresh_storage': refresh_storage, 'open_selected': open_selected,
                         'edit_selected': edit_selected, 'about_top_task': about_top_task})
    with open("./ui-asset/setting-storage.xml", "r", encoding="utf-8") as f:
        sUIxml.loadxml(f.read())
    refresh_storage(None)

def __select_storage(cid):
    global nowselected
    nowselectedPart = []
    for id in cid:
        nowselectedPart.append(storageTree[2].itemcget(storageTree[0][id][0], 'text'))
    nowselected = datas.workspace + '/'.join(nowselectedPart) + '.json'

def __get_storage(tasks_path=None):
    # 获取 ./tasks/ 目录下的所有文件，包括子文件夹
    tasks_list = []
    tasks_dir = []
    substring = '.json'
    if not tasks_path:
        tasks_path = datas.workspace
    # 主目录文件在最前面，子目录文件在后面
    for file in os.listdir(tasks_path):
        if os.path.isfile(os.path.join(tasks_path, file)):
            pos = file.rfind(substring)
            if pos != -1:
                task_name = file[:pos]
                tasks_list.append(task_name)
        elif os.path.isdir(os.path.join(tasks_path, file)):
            tasks_dir.append(file)
    for task_dir in tasks_dir:
        child = __get_storage(os.path.join(tasks_path, task_dir))
        if len(child) > 0:
            tasks_list.append((task_dir, child))
    return tasks_list

def refresh_storage(e):
    global storageTree, storageContent, nowselected
    if storageTree is not None:
        sUI.delete(storageTree[-1])
    storageContent = __get_storage()
    if len(storageContent) == 0:
        # 无存储
        sthemeUI.add_label((5,5), text="无存储", font=("微软雅黑", 16))
        nowselected = None
        return
    storageTree = sthemeUI.add_treeview((0,0), width=585, height=470, content=storageContent, command=__select_storage)
    nowselected = None

def open_selected(e):
    if nowselected is not None:
        if os.path.isfile(nowselected):
            subprocess.Popen(f'explorer /select,"{nowselected.replace("/", "\\")}"')
        else:
            path = nowselected[:-5]
            # 打开文件夹
            subprocess.Popen(f'explorer "{path.replace("/", "\\")}"')

def edit_selected(e):
    if nowselected is not None:
        if os.path.isfile(nowselected):
            subprocess.Popen(f'start "" "{nowselected}"', shell=True)

def about_top_task(e):
    # 打开关于priority.txt的链接页面
    webopen('https://quickup.smart-space.com.cn/priority-of-task/')


# 快捷键（暂不提供设置working...）
tdata1 = (
    ('快捷键','说明'),
    ('Ctrl+R','刷新任务视图'),
    ('Ctrl+N','新建任务'),
    ('Ctrl+I','打开设置'),
    ('Ctrl+Q','退出主窗口'),
    ('Up/Down','选择任务'),
    ('Shift+回车','运行任务'),
    ('Ctrl+E','编辑任务'),
    ('PageUp\nPageDown','向上翻页\n向下翻页'),
    ('Home\nEnd','第一个任务\n最后一个任务')
)

tdata2 = (
    ('快捷键','说明'),
    ('Alt+1','常规设置'),
    ('Alt+2','高级设置'),
    ('Alt+3','存储设置'),
    ('Alt+4','快捷键设置'),
    ('Ctrl+U','检查更新'),
    ('Ctrl+W','关闭窗口'),
)

tdata3 = (
    ('快捷键','说明'),
    ('Ctrl+W','关闭编辑器'),
    ('Ctrl+S','保存当前任务'),
    ('Ctrl+R','运行任务'),
    ('Ctrl+E','更改环境目录'),
    ('Alt+A','切换标星状态'),
    ('Alt+F','打开任务位置'),
    ('Alt+C','添加命令'),
    ('Alt+S','添加命令集'),
    ('Alt+T','添加子任务'),
    ('Alt+W','添加子工作区'),
    ('Alt+I','添加备注'),
)

tdata4 = (
    ('快捷键','说明'),
    ('Up/Down','选择工作区'),
    ('回车','确定工作区'),
    ('Esc','取消选择'),
)

def init_shortcut():
    global scUI, scUIxml
    scUI = BasicTinUI(root, background="#f3f3f3")
    scUIxml = TinUIXml(theme(scUI))
    scUIxml.datas.update({'tdata1': tdata1, 'tdata2': tdata2, 'tdata3': tdata3, 'tdata4': tdata4})
    with open("./ui-asset/setting-shortcut.xml", "r", encoding="utf-8") as f:
        scUIxml.loadxml(f.read())


# 页面切换
def open_page(flag):
    global lastUI
    if flag == 'general':
        lastUI.place_forget()
        gUI.place(x=0, y=60, width=600, height=540)
        lastUI = gUI
    elif flag == 'advanced':
        lastUI.place_forget()
        aUI.place(x=0, y=60, width=600, height=540)
        lastUI = aUI
    elif flag =='storage':
        lastUI.place_forget()
        sUI.place(x=0, y=60, width=600, height=540)
        lastUI = sUI
    elif flag =='shortcut':
        lastUI.place_forget()
        scUI.place(x=0, y=60, width=600, height=540)
        lastUI = scUI

def select_page(flag):
    if flag == 'general':
        pivot.select(0)
        open_page('general')
    elif flag == 'advanced':
        pivot.select(1)
        open_page('advanced')
    elif flag =='storage':
        pivot.select(2)
        open_page('storage')
    elif flag =='shortcut':
        pivot.select(3)
        open_page('shortcut')


def close_setting():
    root.withdraw()

def show_setting(e):
    global settingwindow, root, theme, lastUI, pivot
    if settingwindow:
        root.deiconify()
        return
    settingwindow = True
    root = tk.Toplevel()
    root.title("QuickUp设置")
    width = 600
    height = 600
    x = (root.winfo_screenwidth() - width) / 2
    y = (root.winfo_screenheight() - height) / 2
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", close_setting)
    root.iconbitmap("./logo.ico")
    root.update_idletasks()
    if config.settings['general']['theme'] == "light":
        theme = TinUILight
    else:
        theme = TinUIDark
        set_window_dark(root)
    root.focus_set()

    ui = BasicTinUI(root, background="#f3f3f3")
    ui.pack(fill=tk.BOTH, expand=True)
    uixml = TinUIXml(theme(ui))
    uixml.funcs.update({
        "open_page": open_page,
    })
    with open("./ui-asset/setting.xml", "r", encoding="utf-8") as f:
        uixml.loadxml(f.read())
    pivot = uixml.tags["pivot"][-2]
    
    init_general()
    init_advanced()
    init_storage()
    init_shortcut()
    lastUI = gUI
    open_page('general')

    root.bind("<Alt-KeyPress-1>", lambda e: select_page('general'))
    root.bind("<Alt-KeyPress-2>", lambda e: select_page('advanced'))
    root.bind("<Alt-KeyPress-3>", lambda e: select_page('storage'))
    root.bind("<Alt-KeyPress-4>", lambda e: select_page('shortcut'))
    root.bind("<Control-u>", check_update)
    root.bind("<Control-w>", lambda e: close_setting())
