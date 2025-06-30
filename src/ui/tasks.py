# ./ui/tasks.py
"""
QuickUp的任务列表视图，有两种显示模式：
1. 任务列表为空时，显示一个nonetask.xml界面元素
2. 任务列表不为空时，每个元素显示singletask.xml界面
"""
import os
import json

from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import datas
from runner.runtask import run_task
from ui import editor
from ui.editor import create_editor
from ui.utils import on_ui_destroy, show_dialog
import config

taskView = None
taskuixml = []# 存放子元素uixml的列表
tasknames = []# 存放任务名称的列表
theme = None
themename = ''

def initial_tasks_view(_taskView, _root):
    # taskView::BasicTinUI.listview
    # 初始化任务列表
    global taskView, root, uixml_content, theme, themename, tasknames
    taskView = _taskView
    root = _root
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        themename = 'dark'
    else:
        theme = TinUILight
        themename = 'light'
    datas.tasks_name_initial()# 读取任务列表
    tasknames = sort_with_priority(datas.tasks_name.copy())
    for i in range(1, len(tasknames)):
        taskView.add()
    with open('./ui-asset/singletask.xml', 'r', encoding='utf-8') as f:
        uixml_content = f.read()
    i = 0
    for task in tasknames:
        ui, _, uixml, _ = taskView.getui(i)
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e, uixml=uixml: on_ui_destroy(uixml))
        taskuixml.append(uixml)
        uixml.environment({
            'run_task': lambda e, task=task: run_task(task),
            'edit_task': lambda e, task=task: edit_task(task),
            'delete_task': lambda e, task=task: delete_task_view(task),
        })
        uixml.loadxml(str.replace(uixml_content, '%TITLENAME%', task))
        i += 1

def refresh_tasks_view():
    # 刷新任务列表
    global tasknames
    taskuixml.clear()
    taskView.clear()
    now_tasks = sorted(datas.tasks_name)
    tasknames = sort_with_priority(now_tasks)
    for i in range(0, len(tasknames)):
        taskView.add()
    with open('./ui-asset/singletask.xml', 'r', encoding='utf-8') as f:
        uixml_content = f.read()
    i = 0
    for task in tasknames:
        ui, _, uixml, _ = taskView.getui(i)
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e, uixml=uixml: on_ui_destroy(uixml))
        taskuixml.append(uixml)
        uixml.environment({
            'run_task': lambda e, task=task: run_task(task),
            'edit_task': lambda e, task=task: edit_task(task),
            'delete_task': lambda e, task=task: delete_task_view(task),
        })
        uixml.loadxml(str.replace(uixml_content, '%TITLENAME%', task))
        i += 1

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

def add_task_view(task:str):
    # task::Task
    # 后端添加任务
    datas.tasks_name_add(task)
    # 前端添加任务
    cui, _, cuixml, _ = taskView.add()
    del cuixml.ui
    cuixml.ui = theme(cui)
    cui.bind('<Destroy>', lambda e, cuixml=cuixml: on_ui_destroy(cuixml))
    taskuixml.append(cuixml)
    cuixml.environment({
        'run_task': lambda e, task=task: start_task(task),
        'edit_task': lambda e, task=task: edit_task(task),
        'delete_task': lambda e, task=task: delete_task_view(task),
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
            del taskuixml[index]
            # 前端删除任务
            taskView.delete(index)
        datas.tasks_name_delete(task)
        os.remove(datas.workspace + task + '.json')

def start_task(task:str):
    # task::Task
    run_task(task)

def edit_task(task:str):
    # task::Task
    create_editor(task, lambda oldtask, newtask: change_task_name(oldtask, newtask))

def change_task_name(task:str, newname:str):
    # 修改已经存在的任务的名称
    if task in datas.tasks_name:
        index1 = datas.tasks_name.index(task)
        datas.tasks_name[index1] = newname
        uixml = taskuixml[index1]
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
        taskView.clear()
        taskuixml.clear()
        tasknames = sort_with_priority(tasknames.copy())
        for task in tasknames:
            cui, _, cuixml, _ = taskView.add()
            del cuixml.ui
            cuixml.ui = theme(cui)
            cui.bind('<Destroy>', lambda e, uixml=cuixml: on_ui_destroy(uixml))
            taskuixml.append(cuixml)
            cuixml.environment({
                'run_task': lambda e, task=task: start_task(task),
                'edit_task': lambda e, task=task: edit_task(task),
                'delete_task': lambda e, task=task: delete_task_view(task),
            })
            cuixml.loadxml(str.replace(uixml_content, '%TITLENAME%', task))
