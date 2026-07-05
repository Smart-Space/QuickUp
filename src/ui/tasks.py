# ./ui/tasks.py
"""
QuickUp的任务列表视图，有两种显示模式：
1. 任务列表为空时，显示一个nonetask.xml界面元素
2. 任务列表不为空时，每个元素显示singletask.xml界面
"""
import os
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
from labels import labelsmng

taskView = None
taskuis = []# 存放子元素theme(ui)的列表
tasknames = []# 存放任务名称的列表
theme = None
themename = ''
progress_colors = {} # 存放进展信息颜色的字典
accent_color = None
_task_rate_cache = {} # task -> (mtime, rate)

def initial_tasks_view(_taskView, _root):
    # taskView::BasicTinUI.listview
    # 初始化任务列表
    global taskView, root, theme, themename, tasknames, accent_color
    taskView = _taskView
    root = _root
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        themename = 'dark'
        progress_colors['text'] = '#ffffff'
        progress_colors['running'] = '#4cc2ff'
        progress_colors['success'] = '#6ccb5f'
        progress_colors['error'] = '#ff99a4'
        accent_color = config.settings['general']['accentColorD']
    else:
        theme = TinUILight
        themename = 'light'
        progress_colors['text'] = '#1b1b1b'
        progress_colors['running'] = '#0078d4'
        progress_colors['success'] = '#0f7b0f'
        progress_colors['error'] = '#c42b1c'
        accent_color = config.settings['general']['accentColorL']
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
    for task in list(tasks):
        task_json = os.path.join(datas.workspace, task + '.json')
        if not os.path.exists(task_json):
            # 若被删除，保证程序能够正常运行，但是任务的删除仍应当通过QuickUp进行
            tasks.remove(task)
            _task_rate_cache.pop(task, None)
            continue
        mtime = os.path.getmtime(task_json)
        cached = _task_rate_cache.get(task)
        if cached and cached[0] == mtime:
            rate = cached[1]
        else:
            with open(task_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rate = data.get('rate', False)
            _task_rate_cache[task] = (mtime, rate)
        if rate:
            res_list.append(task)
    res_cmp_list = datas.read_priority()
    for task in res_cmp_list:
        if task in res_list:
            res_tasks.append(task)
    if not res_tasks:
        res_tasks = res_list
    for task in res_tasks:
        if task in tasks:
            tasks.remove(task)
    res_tasks += tasks
    return res_tasks

def create_task(_):
    # 由外部调用，创建任务
    # 后端添加任务
    create_editor('', add_task_view, "NEW")

ui_stack_num = 0
def add_task_view(task:str, add_back=False):
    # task::Task
    global ui_stack_num
    # 后端添加任务
    if add_back:
        if task in tasknames:
            return
        if task not in datas.all_tasks_name:
            datas.tasks_name_add(task)
        else:
            if task not in datas.tasks_name:
                datas.tasks_name.append(task)
        tasknames.append(task)
    # 前端添加任务
    _cui, _, _, _ = taskView.add()
    cui = theme(_cui, accent=accent_color)
    taskuis.append(cui)
    cui.add_title((datas.mul_scale_factor(5),datas.mul_scale_factor(40)), text=task, anchor='w')
    cui.add_accentbutton((datas.mul_scale_factor(362),datas.mul_scale_factor(40)), icon="\uE724", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=task: start_task(_cui, task))
    cui.add_button2((datas.mul_scale_factor(402),datas.mul_scale_factor(40)), icon="\uE70F", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=task: edit_task(task))
    cui.add_button2((datas.mul_scale_factor(442),datas.mul_scale_factor(40)), icon="\uE74D", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=task: delete_task_view(task))
    ui_stack_num += 1
    if ui_stack_num > 8:
        ui_stack_num = 0
        _cui.update_idletasks()

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
            datas.remove_priority(task)
            index = tasknames.index(task)
            tasknames.remove(task)
            taskuis[index].ui.delete('all')
            del taskuis[index]
            labelsmng.delete_task(task) # 删除任务相关标签
            # 前端删除任务
            taskView.delete(index)
        datas.tasks_name_delete(task)
        os.remove(datas.workspace + task + '.json')

def __draw_task_progress(ui:BasicTinUI):
    back = ui._BasicTinUI__ui_polygon(((datas.mul_scale_factor(360),datas.mul_scale_factor(25)),(datas.mul_scale_factor(470),datas.mul_scale_factor(55))), fill=ui.cget('background'), outline=ui.cget('background'), width=9)
    icon = ui.add_paragraph((datas.mul_scale_factor(360), datas.mul_scale_factor(40)), anchor='w', text='\uF16A', font='{Segoe Fluent Icons} 16', fg=progress_colors['running'])
    info = ui.add_paragraph((datas.mul_scale_factor(430), datas.mul_scale_factor(40)), anchor='center', text='', font='{Segoe UI} 12', fg=progress_colors['text'])
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
        cui = taskuis[index2]
        tags = set()
        for i in cui.ui.find_all():
            tags.update(cui.ui.gettags(i))
        for tag in tags:
            cui.ui.delete(tag)
        cui.add_title((datas.mul_scale_factor(5),datas.mul_scale_factor(40)), text=newname, anchor='w')
        cui.add_accentbutton((datas.mul_scale_factor(362),datas.mul_scale_factor(40)), icon="\uE724", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=newname: start_task(cui.ui, task))
        cui.add_button2((datas.mul_scale_factor(402),datas.mul_scale_factor(40)), icon="\uE70F", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=newname: edit_task(task))
        cui.add_button2((datas.mul_scale_factor(442),datas.mul_scale_factor(40)), icon="\uE74D", text='', font='{Segoe Fluent Icons} 16', anchor='w', command=lambda _, task=newname: delete_task_view(task))
    index2 = datas.all_tasks_name.index(task)
    datas.all_tasks_name[index2] = newname

last_search_keyword = ''
def search_tasks(keyword:str, silence=False):
    # 搜索任务
    global last_search_keyword, tasknames
    if keyword == last_search_keyword:
        return
    _old_keyword = last_search_keyword
    last_search_keyword = keyword
    if keyword.startswith('|'):
        keyword = keyword[1:]
        if keyword == '':
            return
        # 搜索标签
        new_tasknames = []
        for label in labelsmng.get_labels():
            if keyword[1:] in label:
                new_tasknames.extend(labelsmng.find_tasks_by_label(label))
        new_tasknames = list(dict.fromkeys(new_tasknames)) # 去重
    else:
        new_tasknames = datas.tasks_name_find(keyword)
    if len(new_tasknames) == 0:
        # 没有找到相关任务
        if not silence:
            # 显示提示信息
            d = Dialog(root, 'info', themename)
            show_dialog(d, '没有找到相关任务', f'未找到关于<{keyword}>的任务', "msg", themename)
        last_search_keyword = _old_keyword # 恢复搜索关键字
    else:
        new_tasknames = sort_with_priority(new_tasknames)
        __clear_all_tasks_ui()
        tasknames = new_tasknames
        for task in tasknames:
            add_task_view(task)

def __clear_all_tasks_ui():
    # 清空所有任务(UI only)
    for one in taskuis:
        one.ui.delete('all')
    taskView.clear()
    taskuis.clear()
