# ./labels/labelsui.py
"""
工作区标签管理
"""
import tkinter as tk

from tinui import BasicTinUI, ExpandPanel, VerticalPanel, HorizonPanel
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

from ui.utils import show_dialog
from labels import labelsmng
import config
import datas


def refresh_labels(_=None):
    global now_label
    now_label = None
    if textbox:
        textbox.delete('1.0', 'end')
    listbox.clear()
    labels = labelsmng.get_labels()
    for label in labels:
        listbox.add(label)

def add_label(_):
    d = Dialog(labelswindow, "input", config.settings['general']['theme'])
    res = show_dialog(d, "添加标签", "请输入新标签名称：", "input", config.settings['general']['theme'])
    if res:
        label = res.strip()
        if label:
            if labelsmng.add_label(label):
                listbox.add(label)
            else:
                d = Dialog(labelswindow, "error", config.settings['general']['theme'])
                show_dialog(d, "错误", "标签已存在！", "msg", config.settings['general']['theme'])

def delete_label(_):
    global now_label
    if not now_label:
        return
    d = Dialog(labelswindow, "question", config.settings['general']['theme'])
    res = show_dialog(d, "删除标签", f"是否删除标签 {now_label} ？", "msg", config.settings['general']['theme'])
    if res is None or res == False:
        return
    labelsmng.delete_label(now_label)
    now_label = None
    refresh_labels()

def modify_label(_):
    global now_label
    if not now_label:
        return
    d = Dialog(labelswindow, "input", config.settings['general']['theme'])
    res = show_dialog(d, "修改标签", "请输入新标签名称：", "input", config.settings['general']['theme'], now_label)
    if res:
        new_label = res.strip()
        if new_label:
            if labelsmng.rename_label(now_label, new_label):
                now_label = new_label
                refresh_labels()
            else:
                d = Dialog(labelswindow, "error", config.settings['general']['theme'])
                show_dialog(d, "错误", "标签已存在！", "msg", config.settings['general']['theme'])

now_label = None
_instruction_tail = '(Alt+↑/↓ 调整任务顺序)'

def __textbox_block_edit(event):
    nav_keys = {
        'Left', 'Right', 'Up', 'Down', 'Home', 'End', 'Prior', 'Next',
        'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'
    }
    if event.keysym in nav_keys:
        return
    if (event.state & 0x0004) and event.keysym.lower() in ('c', 'a'):
        return
    return 'break'

def __textbox_block_paste(_):
    return 'break'

def __move_task_line(delta):
    if textbox is None or now_label is None:
        return 'break'
    insert_index = textbox.index('insert')
    line = int(insert_index.split('.')[0])
    last_line = int(textbox.index('end-1c').split('.')[0])
    if line <= 1 or line >= last_line:
        return 'break'
    target_line = line + delta
    if target_line <= 1 or target_line >= last_line:
        return 'break'
    if delta < 0:
        block_start = f"{target_line}.0"
        block_end = f"{line}.end+1c"
        new_line = target_line
    else:
        block_start = f"{line}.0"
        block_end = f"{target_line}.end+1c"
        new_line = target_line
    block_text = textbox.get(block_start, block_end)
    lines = block_text.splitlines(True)
    if len(lines) < 2:
        return 'break'
    lines[0], lines[1] = lines[1], lines[0]
    textbox.delete(block_start, block_end)
    textbox.insert(block_start, ''.join(lines))
    textbox.mark_set('insert', f"{new_line}.0")
    labelsmng.move_task_line(now_label, line-2, target_line-2)
    return 'break'

def __select_label(label):
    global now_label
    now_label = label
    tasks = labelsmng.find_tasks_by_label(label)
    textbox.delete('1.0', 'end')
    textbox.insert('end', f'标签 |{label}| 共关联{len(tasks)}个任务\n')
    for task in tasks:
        textbox.insert('end', f'- {task}\n')
    textbox.insert('end', _instruction_tail)


labelswindow:BasicTinUI = None
labels_parent = None
labels_rootpanel = None
labels_close_callback = None
listbox = None
textbox:tk.Text = None

def __update_layout():
    if labelswindow is None or labels_rootpanel is None:
        return
    labelswindow.update_idletasks()
    labels_rootpanel.update_layout(5, 5, labelswindow.winfo_width()-5, labelswindow.winfo_height()-5)

def init_labels_ui(parent, close_callback=None):
    global labelswindow, listbox, textbox, labels_parent, labels_rootpanel, labels_close_callback
    if labelswindow:
        return labelswindow
    labels_parent = parent
    labels_close_callback = close_callback
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        bottombg = '#252525'
        bottomline = '#323232'
    else:
        theme = TinUILight
        bottombg = '#fbfbfb'
        bottomline = '#e5e5e5'

    labelswindow = BasicTinUI(parent)
    labelswindow.set_scale(datas.scale_factor)
    uitheme = theme(labelswindow, accent=config.settings['general']['accentColorD'] if config.settings['general']['theme'] == 'dark' else config.settings['general']['accentColorL'])

    labels_rootpanel = ExpandPanel(labelswindow)

    vp = VerticalPanel(labelswindow, spacing=10)
    labels_rootpanel.set_child(vp)

    top = HorizonPanel(labelswindow, padding=(5,10,5,10), spacing=10)
    vp.add_child(top, 40)
    top.add_child(uitheme.add_toolbutton((0,0), text='返回', icon='\uE830', command=hide_labels_window, anchor='w')[-1], 100)
    top.add_child(uitheme.add_back((0,0)), weight=1)
    top.add_child(uitheme.add_title((0,0), text='标签管理', size=2, anchor='e'), 100)

    hp = HorizonPanel(labelswindow, padding=(5,5,5,5), spacing=10)
    vp.add_child(hp, weight=1)
    ep1 = ExpandPanel(labelswindow)
    listboxs = uitheme.add_listbox((0,0), command=__select_label)
    listbox = listboxs[-2]
    refresh_labels()
    ep1.set_child(listboxs[-1])
    hp.add_child(ep1, weight=3)
    ep2 = ExpandPanel(labelswindow)
    textboxs = uitheme.add_textbox((0,0), scrollbar=True)
    textbox = textboxs[0]
    if config.settings['general']['theme'] == 'dark':
        textbox.config(insertbackground='#ffffff')
    textbox.bind('<Key>', __textbox_block_edit)
    textbox.bind('<Control-v>', __textbox_block_paste)
    textbox.bind('<Control-V>', __textbox_block_paste)
    textbox.bind('<Control-x>', __textbox_block_paste)
    textbox.bind('<Control-X>', __textbox_block_paste)
    textbox.bind('<<Paste>>', __textbox_block_paste)
    textbox.bind('<<Cut>>', __textbox_block_paste)
    textbox.bind('<<Undo>>', __textbox_block_paste)
    textbox.bind('<<Redo>>', __textbox_block_paste)
    textbox.bind('<Alt-Up>', lambda e: __move_task_line(-1))
    textbox.bind('<Alt-Down>', lambda e: __move_task_line(1))
    ep2.set_child(textboxs[-1])
    hp.add_child(ep2, weight=5)

    hp2 = HorizonPanel(labelswindow, spacing=20, bg=bottombg, line=bottomline, linew=1)
    vp.add_child(hp2, 50)

    hp2.add_child(uitheme.add_back((0,0)), weight=1)
    hp2.add_child(uitheme.add_button2((0,0), text='刷新', command=refresh_labels, anchor='center')[-1])
    hp2.add_child(uitheme.add_button2((0,0), text='添加标签', command=add_label, anchor='center')[-1])
    hp2.add_child(uitheme.add_button2((0,0), text='删除标签', command=delete_label, anchor='center')[-1])
    hp2.add_child(uitheme.add_button2((0,0), text='修改标签', command=modify_label, anchor='center')[-1])
    hp2.add_child(uitheme.add_back((0,0)), weight=1)

    return labelswindow

def show_labels_window(_=None):
    if labelswindow is None:
        return
    labelswindow.pack(fill='both', expand=True)
    __update_layout()
    labelswindow.focus_set()

def hide_labels_window(_=None):
    if labelswindow is None:
        return
    labelswindow.pack_forget()
    if labels_close_callback:
        labels_close_callback()
