# ./ui/setting.py
"""
QuickUp Setting UI
"""
import tkinter as tk
from tkinter.colorchooser import askcolor
import os
import sys
import subprocess
from subprocess import list2cmdline
from webbrowser import open as webopen
from urllib.request import urlopen
from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from cppextend.QUmodule import register_start, unregister_start, have_start_value, zone_try_times,\
      check_admin, set_border_color as cpp_set_border_color

from startup_task import has_task, set_task, remove_task

import config
import datas
from ui.utils import set_window_dark, show_dialog, bind_shortcuts
from runner.update import update_program, update_QuickUp
from ui.about import open_log, open_url, open_doc
from plugin.manager import plugin_dir


def scale(x):
    return int(x*datas.scale_factor)

dialog_theme = None
accent_color = None

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
    global gUI, first_check_topmost, first_check_update, first_check_showhidden, accentc_back
    gUI = BasicTinUI(root, background="#f3f3f3")
    gUI.set_scale(datas.scale_factor)
    gUI.place(x=0, y=scale(60), width=scale(600), height=scale(540))
    gUIxml = TinUIXml(theme(gUI, accent=accent_color))
    blur_rank = list(range(101))
    for i in range(101):
        blur_rank[100-i] = str(i)
    gUIxml.datas.update({'blur_rank': blur_rank})
    gUIxml.funcs.update({'sel_theme': sel_theme, 'sel_blur': sel_blur, 'check_update': check_update,
                         "set_topmost": set_topmost, "auto_check_update": s_auto_check_update,
                         "sel_exit_mode": sel_exit_mode, 'sel_msc': sel_msc,
                         "show_hidden": set_show_hidden, 'open_log': open_log, 'sel_transparency': sel_transparency,
                         "sel_accent_color": sel_accent_color, 'set_border_color': None,
                         'open_url': open_url, 'open_doc': open_doc})
    with open("./ui-asset/setting-general.xml", "r", encoding="utf-8") as f:
        gUIxml.loadxml(f.read().replace('%VERSION%', datas.version))
    
    themeradio = gUIxml.tags["themeradio"][-2]
    accentc_back = gUIxml.tags["accentcolorbutton"][1]
    nowtheme = config.theme_original
    if nowtheme == "light":
        themeradio.select(0)
    elif nowtheme == "dark":
        themeradio.select(1)
    else:
        themeradio.select(2)
    
    accentbordercheck = gUIxml.tags["accentbordercheck"][-2]
    if config.settings['general'].get('accentBorder', True):
        accentbordercheck.on()
    gUIxml.funcs['set_border_color'] = set_border_color

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

    transparencyscale = gUIxml.tags["transparencyscale"][-2]
    transparencyscale.select(config.settings['general'].get('transparency', 0))

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
    d = Dialog(root, "question", dialog_theme)
    res = show_dialog(d, "提示", "检测到新版本，是否下载？", "msg", dialog_theme)
    if res:
        update_program(root)

def __update_ready(e):
    # 下载完成提示
    d = Dialog(root, "question", dialog_theme)
    res = show_dialog(d, "更新准备继续", "新版安装软件下载完成，是否安装？\n（需要退出软件）", "msg", dialog_theme)
    if res:
        update_QuickUp()

def __update_failed(e):
    # 下载失败提示
    d = Dialog(root, "error", dialog_theme)
    show_dialog(d, "更新失败", "新版安装软件下载失败，请稍后再试！", "msg", dialog_theme)

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
            d = Dialog(root, "info", dialog_theme)
            show_dialog(d, "提示", "当前已是最新版本！", "msg", dialog_theme)
    except:
        gUI.config(cursor="")
        d = Dialog(root, "error", dialog_theme)
        show_dialog(d, "网络错误", "检查更新失败，请稍后再试！", "msg", dialog_theme)

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
    config.settings['general']['theme'] = theme
    config.save_config()
    nowtheme = config.settings['general']['theme']
    if nowtheme == "light":
        gUI.itemconfig(accentc_back, fill=config.settings['general']['accentColorL'])
    else:
        gUI.itemconfig(accentc_back, fill=config.settings['general']['accentColorD'])
    if config.settings['general'].get('accentBorder', False):
        if nowtheme == 'light':
            cpp_set_border_color(False, config.settings['general']['accentColorL'])
        else:
            cpp_set_border_color(True, config.settings['general']['accentColorD'])

def sel_accent_color(_):
    # 切换主题色
    theme = config.settings['general']['theme']
    if theme == "light":
        init_color = config.settings['general']['accentColorL']
    else:
        init_color = config.settings['general']['accentColorD']
    color = askcolor(title='选择主题色', initialcolor=init_color, parent=root)
    if color[1]:
        gUI.itemconfig(accentc_back, fill=color[1])
        if theme == "light":
            config.settings['general']['accentColorL'] = color[1]
        else:
            config.settings['general']['accentColorD'] = color[1]
        config.save_config()
        if config.settings['general'].get('accentBorder', False):
            if theme == 'light':
                cpp_set_border_color(False, color[1])
            else:
                cpp_set_border_color(True, color[1])

def set_border_color(tag):
    config.settings['general']['accentBorder'] = tag
    config.save_config()
    if tag:
        theme = config.settings['general']['theme']
        if theme == 'light':
            color = config.settings['general']['accentColorL']
        else:
            color = config.settings['general']['accentColorD']
        cpp_set_border_color(theme == 'dark', color)
    else:
        cpp_set_border_color(False)

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

def sel_transparency(rate):
    alpha = round(1-rate/20, 2)
    datas.root.attributes("-alpha", alpha)
    config.settings['general']['transparency'] = rate
    config.save_config()


# ==========高级设置==========
first_dis_admin = True
first_auto_save = True
first_admin_start = True
checkbox = None
adminstartcheck = None
HK_CTRL = 0x0002
HK_ALT = 0x0001
HK_SHIFT = 0x0004
HK_Modifiers = []
HK_VK = 0x51 # 'Q'
def init_advanced():
    global aUI, first_dis_admin, first_auto_save, hkentry, snapretryentry, first_admin_start,\
        checkbox, adminstartcheck
    aUI = BasicTinUI(root, background="#f3f3f3")
    aUI.set_scale(datas.scale_factor)
    aUIxml = TinUIXml(theme(aUI, accent=accent_color))
    aUIxml.funcs.update({'dis_admin': dis_admin, 'start_on_boot': start_on_boot,
                         'about_start_on_boot': about_start_on_boot, 'auto_save': auto_save,
                         'copy_path': copy_path, 'open_cmd_args': open_cmd_args,
                         'toggle_hk_ctrl': None, 'toggle_hk_alt': None,
                         'toggle_hk_shift': None,
                         'apply_snap_retry': apply_snap_retry,
                         'start_on_admin': start_on_admin, 'about_start_on_admin': about_start_on_admin})
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

    adminstartcheck = aUIxml.tags["adminstartcheck"][-2]
    if config.settings['advanced']['startOnAdmin']:
        adminstartcheck.on()
    else:
        first_admin_start = False

    autosaveonoff = aUIxml.tags["autosaveonoff"][-2]
    if config.settings['advanced']['autoSave']:
        autosaveonoff.on()
    else:
        first_auto_save = False

    hkentry = aUIxml.tags["hkentry"][0]
    def __hkentry_keypress(e):
        if e.char and e.char.isascii() and e.char.isalpha():
            hkentry.delete(0, 'end')
            hkentry.insert(0, e.char.upper())
            apply_hk()
        return "break"
    hkentry.bind("<KeyPress>", __hkentry_keypress)
    if config.settings['advanced']['callUp']:
        modifier_code = config.settings['advanced']['callUp'][0]
        if modifier_code & HK_CTRL:
            aUIxml.tags['b1'][-2].on()
            HK_Modifiers.append(HK_CTRL)
        if modifier_code & HK_ALT:
            aUIxml.tags['b2'][-2].on()
            HK_Modifiers.append(HK_ALT)
        if modifier_code & HK_SHIFT:
            aUIxml.tags['b3'][-2].on()
            HK_Modifiers.append(HK_SHIFT)
        hkentry.insert(0, chr(config.settings['advanced']['callUp'][1]).upper())

    aUIxml.funcs.update({'toggle_hk_ctrl': toggle_hk_ctrl, 'toggle_hk_alt': toggle_hk_alt, 'toggle_hk_shift': toggle_hk_shift})

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
            register_start("QuickUp", f'"{os.path.abspath(sys.argv[0])}" -s')
        if config.settings['advanced']['startOnAdmin']:
            root.after(100, adminstartcheck.off)
    else:
        if have_start_value("QuickUp"):
            unregister_start("QuickUp")
    config.settings['advanced']['runWhenStart'] = flag
    config.save_config()

def about_start_on_boot(e):
    # 关于开机启动
    d = Dialog(root, "info", dialog_theme)
    show_dialog(d, "开机启动", "QuickUp将尝试以静默模式启动，如果不允许QuickUp关闭到托盘，\n" \
                "则直接显示图形界面。\n\n" \
                "具体参数为 quickup -s", "msg", dialog_theme)

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
    d = Dialog(root, "info", dialog_theme)
    show_dialog(d, "QuicUp命令行参数", cmd_args_context, "msg", dialog_theme)

def toggle_hk_ctrl(flag):
    if flag:
        HK_Modifiers.append(HK_CTRL)
    else:
        HK_Modifiers.remove(HK_CTRL)
    apply_hk()

def toggle_hk_alt(flag):
    if flag:
        HK_Modifiers.append(HK_ALT)
    else:
        HK_Modifiers.remove(HK_ALT)
    apply_hk()

def toggle_hk_shift(flag):
    if flag:
        HK_Modifiers.append(HK_SHIFT)
    else:
        HK_Modifiers.remove(HK_SHIFT)
    apply_hk()

def apply_hk():
    if len(HK_Modifiers) == 0:
        # 功能键为空，则清空entry，且保存为False
        hkentry.delete(0, 'end')
        config.settings['advanced']['callUp'] = False
        config.save_config()
        return
    ch:str = hkentry.get()
    if len(ch) > 1:
        d = Dialog(root, "error", dialog_theme)
        show_dialog(d, "错误", "热键只能是一个字符！", "msg", dialog_theme)
        return
    if len(ch) == 0:
        hkentry.insert(0, 'Q') # 默认热键为Q
        ch = 'Q'
    if ch.lower() >= 'a' and ch.lower() <= 'z':
        HK_VK = ord(ch.upper())
        hkentry.delete(0, 'end')
        hkentry.insert(0, ch.upper())
    else:
        d = Dialog(root, "error", dialog_theme)
        show_dialog(d, "错误", "热键只能是一个字母！", "msg", dialog_theme)
        return
    modifers = 0x0000
    for m in HK_Modifiers:
        modifers |= m
    config.settings['advanced']['callUp'] = (modifers, HK_VK)
    config.save_config()

def apply_snap_retry(_):
    # 重试布局次数
    res = snapretryentry.get()
    if res.isdigit() and int(res) >= 0:
        config.settings['advanced']['zoneRetryTimes'] = int(res)
        config.save_config()
        zone_try_times(int(res))
    else:
        d = Dialog(root, "error", dialog_theme)
        show_dialog(d, "错误", "重试次数需要为正整数", "msg", dialog_theme)

def start_on_admin(flag):
    if flag and not check_admin():
        d = Dialog(root, "error", dialog_theme)
        show_dialog(d, "错误", "当前没有管理员权限，无法启用此选项！", "msg", dialog_theme)
        adminstartcheck.off()
        return
    if flag:
        if not has_task("QuickUp"):
            exe_path = os.path.abspath(sys.argv[0])
            cmd = list2cmdline([exe_path, "-s"])
            set_task("QuickUp", cmd)
        if config.settings['advanced']['runWhenStart']:
            root.after(100, checkbox.off)
    elif not flag and has_task("QuickUp"):
        remove_task("QuickUp")
    config.settings['advanced']['startOnAdmin'] = flag
    config.save_config()

def about_start_on_admin(_):
    d = Dialog(root, "info", dialog_theme)
    show_dialog(d, "管理员权限启动", "QuickUp将尝试以管理员权限启动，但需要管理员权限。\n" \
                "如果不允许QuickUp关闭到托盘，则直接显示图形界面。\n\n" \
                "具体参数为 quickup -s", "msg", dialog_theme)


# ==========存储设置==========
storageTree = None
nowselected = None
storageContent = None
def init_storage():
    global sUI, sthemeUI, sUIxml
    sUI = BasicTinUI(root, background="#f3f3f3")
    sUI.set_scale(datas.scale_factor)
    sthemeUI = theme(sUI, accent=accent_color)
    sUIxml = TinUIXml(sthemeUI)
    sUIxml.funcs.update({'refresh_storage': refresh_storage, 'open_selected': open_selected,
                         'edit_selected': edit_selected, 'about_top_task': about_top_task,
                         'plugin_location': plugin_location})
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
    storageTree = sthemeUI.add_treeview((0,0), width=scale(585), height=scale(470), content=storageContent, command=__select_storage)
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

def plugin_location(e):
    # 打开插件位置
    subprocess.Popen(f'explorer "{plugin_dir.replace("/", "\\")}"', shell=True)

def about_top_task(e):
    # 打开关于priority.txt的链接页面
    webopen('https://quickup.smart-space.com.cn/priority-of-task/')


# 快捷键
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
    ('Ctrl+Shift+C','复制选中栏目'),
    ('Ctrl+Shift+V','粘贴任务栏目'),
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
    scUI.set_scale(datas.scale_factor)
    scUIxml = TinUIXml(theme(scUI, accent=accent_color))
    scUIxml.datas.update({'tdata1': tdata1, 'tdata2': tdata2, 'tdata3': tdata3, 'tdata4': tdata4})
    with open("./ui-asset/setting-shortcut.xml", "r", encoding="utf-8") as f:
        scUIxml.loadxml(f.read())


# 页面切换
def open_page(flag):
    global lastUI
    if flag == 'general':
        lastUI.place_forget()
        lastUI = gUI
    elif flag == 'advanced':
        lastUI.place_forget()
        lastUI = aUI
    elif flag =='storage':
        lastUI.place_forget()
        lastUI = sUI
    elif flag =='shortcut':
        lastUI.place_forget()
        lastUI = scUI
    lastUI.place(x=0, y=scale(60), width=scale(600), height=scale(540))

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
    global settingwindow, root, theme, lastUI, pivot, dialog_theme, accent_color
    if settingwindow:
        root.deiconify()
        return
    settingwindow = True
    dialog_theme = config.settings['general']['theme']
    root = tk.Toplevel()
    root.title("QuickUp设置")
    width = int(600*datas.scale_factor)
    height = int(600*datas.scale_factor)
    x = (root.winfo_screenwidth() - width) / 2
    y = (root.winfo_screenheight() - height) / 2
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", close_setting)
    root.iconbitmap("./logo.ico")
    root.update_idletasks()
    if dialog_theme == "light":
        theme = TinUILight
        accent_color = config.settings['general']['accentColorL']
    else:
        theme = TinUIDark
        set_window_dark(root)
        accent_color = config.settings['general']['accentColorD']
    root.focus_set()

    ui = BasicTinUI(root, background="#f3f3f3")
    ui.set_scale(datas.scale_factor)
    ui.pack(fill=tk.BOTH, expand=True)
    uixml = TinUIXml(theme(ui, accent=accent_color))
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

    setting_shortcuts = config.get_shortcuts('setting', config.DEFAULT_SHORTCUTS['setting'])
    bind_shortcuts(root, setting_shortcuts, {
        'page_general': lambda e: select_page('general'),
        'page_advanced': lambda e: select_page('advanced'),
        'page_storage': lambda e: select_page('storage'),
        'page_shortcut': lambda e: select_page('shortcut'),
        'check_update': check_update,
        'close': lambda e: close_setting(),
    })
