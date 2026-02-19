# ./ui/tasks.py
"""
QuickUp的任务列表视图，有两种显示模式：
1. 任务列表为空时，显示一个nonetask.xml界面元素
2. 任务列表不为空时，每个元素显示singletask.xml界面
"""
import os
# from sys import getrefcount
# def tick(something):
#     print(getrefcount(something))
# from gc import get_referrers
# def who(something):
#     print(get_referrers(something))
import json

from tinui import BasicTinUI
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import datas
from runner.runtask import run_task
from ui import editor
from ui.editor import create_editor
from ui.utils import show_dialog
import config

taskView = None
taskuixml = []# 存放子元素uixml的列表
tasknames = []# 存放任务名称的列表
theme = None
themename = ''
progress_colors = {} # 存放进展信息颜色的字典

with open('./ui-asset/singletask.xml', 'r', encoding='utf-8') as f:
    uixml_content = f.read()

def initial_tasks_view(_taskView, _root):
    # taskView::BasicTinUI.listview
    # 初始化任务列表
    global taskView, root, theme, themename, tasknames
    taskView = _taskView
    root = _root
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        themename = 'dark'
        progress_colors['text'] = '#ffffff'
        progress_colors['running'] = '#4cc2ff'
        progress_colors['success'] = '#6ccb5f'
        progress_colors['error'] = '#ff99a4'
    else:
        theme = TinUILight
        themename = 'light'
        progress_colors['text'] = '#1b1b1b'
        progress_colors['running'] = '#0078d4'
        progress_colors['success'] = '#0f7b0f'
        progress_colors['error'] = '#c42b1c'
    datas.tasks_name_initial()# 读取任务列表
    tasknames = sort_with_priority(datas.tasks_name.copy())
    for task in tasknames:
        add_task_view(task)

def refresh_tasks_view():
    # 刷新任务列表
    global tasknames
    __clear_all_tasks_ui()
    datas.__load_tasks_name()
    now_tasks = sorted(datas.tasks_name)
    tasknames = sort_with_priority(now_tasks)
    for task in tasknames:
        add_task_view(task)

def sort_with_priority(tasks:list):
    # 按优先级排序
    res_list = []
    res_tasks = []
    for task in tasks:
        task_json = os.path.join(datas.workspace, task + '.json')
        if not os.path.exists(task_json):
            # 若被删除，保证程序能够正常运行，但是任务的删除仍应当通过QuickUp进行
            tasks.remove(task)
            continue
        with open(task_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('rate', False):
            res_list.append(task)
    priority_txt = os.path.join(datas.workspace, 'priority.txt')
    if os.path.exists(priority_txt):
        with open(priority_txt, 'r', encoding='utf-8') as f:
            res_cmp_list = f.read().strip().split('\n')
        for task in res_cmp_list:
            if task in res_list:
                res_tasks.append(task)
    else:
        res_tasks = res_list
    for task in res_tasks:
        tasks.remove(task)
    res_tasks += tasks
    return res_tasks

def create_task(e):
    # 由外部调用，创建任务
    # 后端添加任务
    create_editor('', add_task_view, "NEW")

def add_task_view(task:str, add_back=False):
    # task::Task
    # 后端添加任务
    if add_back:
        datas.tasks_name_add(task)
        tasknames.append(task)
    # 前端添加任务
    cui, _, cuixml, _ = taskView.add()
    del cuixml.ui
    cuixml.ui = theme(cui)
    taskuixml.append(cuixml)
    cuixml.environment({
        'run_task': lambda _, task=task: start_task(cui, task),
        'edit_task': lambda _, task=task: edit_task(task),
        'delete_task': lambda _, task=task: delete_task_view(task),
    })
    cuixml.loadxml(str.replace(uixml_content, '%TITLENAME%', task))

def delete_task_view(task:str):
    # task::Task
    # 询问是否删除任务
    if task in editor.task_editors:
        d = Dialog(root, 'info', themename)
        show_dialog(d, '任务正在编辑中', '请先关闭任务编辑器', "msg", themename)
        return
    d = Dialog(root, 'question', themename)
    res = show_dialog(d, '确认删除任务', '删除任务后无法恢复\n请确认删除 ' + task, "msg", themename)
    if res:
        if task in datas.tasks_name:
            # 后端删除任务
            if os.path.exists(datas.workspace + 'priority.txt'):
                # 删除置顶
                with open(datas.workspace + 'priority.txt', 'a+', encoding='utf-8') as f:
                    f.seek(0)
                    lines = f.readlines()
                    lines = [line.rstrip() for line in lines]
                    if task in lines:
                        lines.remove(task)
                    f.seek(0)
                    f.truncate()
                    f.write('\n'.join(lines))
                    if len(lines) != 0:
                        f.write('\n')
            index = tasknames.index(task)
            tasknames.remove(task)
            del taskuixml[index]
            # 前端删除任务
            taskView.delete(index)
        datas.tasks_name_delete(task)
        os.remove(datas.workspace + task + '.json')

def __draw_task_progress(ui:BasicTinUI):
    back = ui._BasicTinUI__ui_polygon(((360,25),(470,55)), fill=ui.cget('background'), outline=ui.cget('background'), width=9)
    icon = ui.add_paragraph((360, 40), anchor='w', text='\uF16A', font='{Segoe Fluent Icons} 16', fg=progress_colors['running'])
    info = ui.add_paragraph((430, 40), anchor='center', text='', font='{Segoe UI} 12', fg=progress_colors['text'])
    return back, icon, info

def start_task(ui:BasicTinUI, task:str):
    # task::Task
    # 以下仅为UI交互效果改进，仍可以通过快捷键进行控制
    task_total = 0
    back, icon, info = __draw_task_progress(ui)
    def __clean():
        nonlocal back, icon, info
        ui.delete(back)
        ui.delete(icon)
        ui.delete(info)
        back = icon = info = None
    def __callback(status, val=1):
        nonlocal task_total, back, icon, info
        match status:
            case 'running':
                ui.itemconfig(icon, text='\uF16A', fill=progress_colors['running'])
                ui.itemconfig(info, text=f'{val}/{task_total}')
            case 'success':
                ui.itemconfig(icon, text='\uE930', fill=progress_colors['success'])
                if val == task_total:
                    ui.after(200, __clean)
            case 'error':
                ui.itemconfig(icon, text='\uEA39', fill=progress_colors['error'])
                if val == task_total:
                    ui.after(200, __clean)
            case 'set':
                task_total = val
                ui.itemconfig(info, text=f'0/{task_total}')
        ui.update_idletasks()
    def callback(status, val=1):
        if status == 'running':
            ui.after(200, __callback, status, val)
        else:
            __callback(status, val)

    run_task(task, callback=callback)

def edit_task(task:str):
    # task::Task
    create_editor(task, lambda oldtask, newtask: change_task_name(oldtask, newtask))

def change_task_name(task:str, newname:str):
    # 修改已经存在的任务的名称
    if task in datas.tasks_name:
        index1 = datas.tasks_name.index(task)
        datas.tasks_name[index1] = newname
        index2 = tasknames.index(task)
        tasknames[index2] = newname
        uixml = taskuixml[index2]
        uixml.realui.delete('all')
        uixml.clean()
        uixml.environment({
            'run_task': lambda e, task=newname: start_task(task),
            'edit_task': lambda e, task=newname: edit_task(task),
            'delete_task': lambda e, task=newname: delete_task_view(task),
        })
        uixml.loadxml(str.replace(uixml_content, '%TITLENAME%', newname))
    index2 = datas.all_tasks_name.index(task)
    datas.all_tasks_name[index2] = newname

last_search_keyword = ''
def search_tasks(keyword:str, silence=False):
    # 搜索任务
    global last_search_keyword, tasknames
    if keyword == last_search_keyword:
        return
    last_search_keyword = keyword
    tasknames = datas.tasks_namn_find(keyword)
    if len(tasknames) == 0:
        if not silence:
            # 没有找到相关任务
            d = Dialog(root, 'info', themename)
            show_dialog(d, '没有找到相关任务', f'未找到关于<{keyword}>的任务', "msg", themename)
    else:
        __clear_all_tasks_ui()
        tasknames = sort_with_priority(tasknames.copy())
        for task in tasknames:
            add_task_view(task)

def __clear_all_tasks_ui():
    # 清空所有任务(UI only)
    taskView.clear()
    taskuixml.clear()
    
