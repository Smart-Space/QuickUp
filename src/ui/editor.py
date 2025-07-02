# ./ui/editor.py
"""
QuickUp的任务编辑器模块
"""
import os
import subprocess
import json
import tkinter as tk
from typing import Union
from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog
from tinui.theme.tinuidark import TinUIDark
from tinui.theme.tinuilight import TinUILight

import datas
from datas import is_valid_windows_filename
from runner.runtask import run_task, run_cmd
import config
from ui.utils import set_window_dark, on_ui_destroy, show_dialog
from runner.create_lnk import create_task_lnk


def init_editor():
    global theme, themename
    if config.settings['general']['theme'] == 'dark':
        theme = TinUIDark
        themename = 'dark'
    else:
        theme = TinUILight
        themename = 'light'


task_editors = dict()# 任务编辑器字典，用于存储所有任务编辑器实例


class CmdEditor:
    # 命令编辑器

    def __init__(self, uixml:TinUIXml, editor):
        self.uixml = uixml
        self.type = 'cmd'
        self.target = ''
        self.args = ''
        self.admin = False
        self.runMAX = False
        self.runMIN = False
        self.contentChanged = None
        self.editor = editor
    
    def init(self, target:str="", args:str="", admin:bool=False, wait:bool=False, runMAX:bool=False, runMIN:bool=False):
        # 初始化ui接管
        self.targetEntry = self.uixml.tags['targetEntry'][0]
        self.argsEntry = self.uixml.tags['argsEntry'][0]
        self.flyoutui:BasicTinUI = self.uixml.tags['flyout'][0]
        flyoutuixml:TinUIXml = self.uixml.tags['flyout'][1]
        del flyoutuixml.ui
        flyoutuixml.ui = theme(self.flyoutui)
        flyoutuixml.funcs.update({
            'if_wait': self.change_wait_state,
            'run_as_admin': lambda tag, task=self: self.editor.cmd_run_as_admin(task, tag),
            'run_max': self.run_max,
            'run_min': self.run_min,
        })
        with open('./ui-asset/editor-cmd-flyout.xml', 'r', encoding='utf-8') as f:
            flyoutuixml.loadxml(f.read())
        self.checkbox = flyoutuixml.tags['checkbox'][-2]
        self.wbutton = flyoutuixml.tags['wbutton'][-2]
        self.wbuttont = flyoutuixml.tags['wbutton'][0]
        self.maxcheckbox = flyoutuixml.tags['maxcheckbox'][-2]
        self.mincheckbox = flyoutuixml.tags['mincheckbox'][-2]
        if admin:
            self.checkbox.on()
        else:
            self.checkbox.off()
        if wait:
            self.wbutton.on()
        else:
            pass
        if runMAX:
            self.maxcheckbox.on()
        else:
            pass
        if runMIN:
            self.mincheckbox.on()
        else:
            pass
        self.target = target
        self.args = args
        self.admin = admin
        self.targetEntry.insert(0, target)
        self.argsEntry.insert(0, args)
    
    def change_wait_state(self, flag):
        # 单线/并行切换
        if flag:
            self.type = 'wcmd'
            self.flyoutui.itemconfig(self.wbuttont, text='单线')
        else:
            self.type = 'cmd'
            self.flyoutui.itemconfig(self.wbuttont, text='并行')
        self.contentChanged(None)
    
    def run_max(self, tag):
        # 最大化运行
        self.runMAX = tag
        self.contentChanged(None)
    
    def run_min(self, tag):
        # 最小化运行
        self.runMIN = tag
        self.contentChanged(None)
    
    def get(self):
        # 获取命令数据
        self.target = self.targetEntry.get()
        self.args = self.argsEntry.get()
        return {
            "type": self.type,
            "target": self.target,
            "args": self.args,
            "admin": self.admin,
            "max": self.runMAX,
            "min": self.runMIN,
        }


class CmdsEditor:

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'cmds'
        self.cmds = []
        self.cmd = 'cmd'# cmd or powershell
        self.wait = False
        self.contentChanged = None
    
    def init(self, cmds:list=[], cmd:str='cmd', wait:bool=False):
        # 初始化ui接管
        self.uixml.funcs['if_wait'] = self.change_wait_state
        self.uixml.funcs['set_shell'] = self.set_shell
        self.textbox = self.uixml.tags['textbox'][0]
        self.radiobox = self.uixml.tags['radiobox'][-2]
        self.wbutton = self.uixml.tags['wbutton'][-2]
        self.wbuttont = self.uixml.tags['wbutton'][0]
        if cmd == 'powershell':
            self.radiobox.select(2)
            self.cmd = 'powershell'
        else:
            self.radiobox.select(0)
            self.cmd = 'cmd'
        if wait:
            self.wbutton.on()
            self.wait = True
        else:
            pass
        self.cmds = cmds
        self.textbox.delete('1.0', 'end')
        if themename == 'dark':
            self.textbox.config(insertbackground='#ffffff')
        for cmd in self.cmds:
            self.textbox.insert('end', cmd + '\n')
        self.textbox.update()
        self.textbox.bind('<<Modified>>', self.textContentChanged)
    
    def textContentChanged(self, e):
        # 文本内容变化
        self.textbox.edit_modified(False)
        self.contentChanged(None)
    
    def change_wait_state(self, flag):
        # 单线/并行切换
        if flag:
            self.uixml.realui.itemconfig(self.wbuttont, text='单线')
            self.wait = True
        else:
            self.uixml.realui.itemconfig(self.wbuttont, text='并行')
            self.wait = False
        self.contentChanged(None)
    
    def set_shell(self, cmd):
        # 设置shell类型
        self.cmd = cmd
        self.contentChanged(None)
    
    def get(self):
        # 获取命令数据
        cmds = self.textbox.get('1.0', 'end').split('\n')
        self.cmds.clear()
        for cmd in cmds:
            if cmd.strip() == '':
                continue
            self.cmds.append(cmd.strip())
        return {
            "type": self.type,
            "cmds": self.cmds,
            "cmd": self.cmd,
            "wait": self.wait,
        }


class TaskEditor:
    # 子任务编辑器

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'task'
        self.task = ''
        self.root = None
    
    def init(self, task:str=""):
        # 初始化ui接管
        self.uixml.funcs['edit_task'] = self.edit_task
        self.taskEntry = self.uixml.tags['taskEntry'][0]
        self.task = task
        self.taskEntry.insert(0, task)
    
    def edit_task(self, e):
        # 编辑子任务（不能修改名称）
        task_name = self.taskEntry.get()
        if task_name == '' or task_name not in datas.all_tasks_name:
            d = Dialog(self.root, "error", themename)
            show_dialog(d, "无法编辑", f"任务 {task_name} 不存在", "msg", theme=themename)
            return
        create_editor(task_name, None, "EDIT", False)

    def get(self):
        # 获取子任务数据
        self.task = self.taskEntry.get()
        return {
            "type": self.type,
            "task": self.task,
        }


class WspEditor:
    # 工作区编辑器
    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'wsp'
        self.name = ''
        self.root = None
    
    def init(self, name:str=""):
        # 初始化ui接管
        self.uixml.funcs['open_quickup'] = self.open_quickup
        self.wspEntry = self.uixml.tags['wspEntry'][0]
        self.name = name
        self.wspEntry.insert(0, name)
    
    def open_quickup(self, e):
        # 打开QuickUp
        workspace_name = self.wspEntry.get()
        if workspace_name == '' or os.path.exists(datas.workspace + workspace_name) == False:
            d = Dialog(self.root, "error", themename)
            show_dialog(d, "无法打开", f"工作区 {workspace_name} 不存在", "msg", theme=themename)
            return
        if datas.workspace != './tasks/':
            workspace_name = datas.workspace[8:] + workspace_name
        run_cmd('QuickUp', 'QuickUp.exe', f'-w "{workspace_name}"', False)
    
    def get(self):
        # 获取工作区数据
        self.name = self.wspEntry.get()
        return {
            "type": self.type,
            "name": self.name,
        }


class TipEditor:
    # 提示编辑器
    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'tip'
        self.tip = ''
        self.wait = False
        self.show = True
        self.top = False
        self.root = None
        self.contentChanged = None
    
    def init(self, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
        # 初始化ui接管
        self.uixml.funcs['if_wait'] = self.change_wait_state
        self.uixml.funcs['show_tip'] = self.change_show_state
        self.uixml.funcs['top_tip'] = self.change_top_state
        self.textbox = self.uixml.tags['textbox'][0]
        self.wbutton = self.uixml.tags['wbutton'][-2]
        self.wbuttont = self.uixml.tags['wbutton'][0]
        self.tipcheckbox = self.uixml.tags['tipcheckbox'][-2]
        self.topcheckbox = self.uixml.tags['topcheckbox'][-2]
        self.textbox.insert('end', tip)
        if wait:
            self.wbutton.on()
        else:
            pass
        if show:
            self.tipcheckbox.on()
        else:
            pass
        if top:
            self.topcheckbox.on()
        else:
            pass
        self.textbox.delete('1.0', 'end')
        if themename == 'dark':
            self.textbox.config(insertbackground='#ffffff')
        self.textbox.insert('end', tip)
        self.textbox.update()
        self.textbox.bind('<<Modified>>', self.textContentChanged)
    
    def textContentChanged(self, e):
        # 文本内容变化
        self.textbox.edit_modified(False)
        self.contentChanged(None)
    
    def change_wait_state(self, flag):
        # 单线/并行切换
        if flag:
            self.uixml.realui.itemconfig(self.wbuttont, text='单线')
            self.wait = True
        else:
            self.uixml.realui.itemconfig(self.wbuttont, text='并行')
            self.wait = False
        self.contentChanged(None)
    
    def change_show_state(self, tag):
        # 显示/隐藏切换
        self.show = tag
        self.contentChanged(None)
    
    def change_top_state(self, tag):
        # 置顶/取消置顶切换
        self.top = tag
        self.contentChanged(None)
    
    def get(self):
        # 获取提示数据
        self.tip = self.textbox.get('1.0', 'end').strip()
        return {
            "type": self.type,
            "tip": self.tip,
            "wait": self.wait,
            "show": self.show,
            "top": self.top,
        }


class Editor(tk.Toplevel):

    def __init__(self, task:str='', callback=None, flag="EDIT", name_changeable=True):
        super().__init__()
        self.task = task
        self.data = {"name": task, "cwd": "", "tasks": [], "rate": False}
        self.tasks = []# 任务列表，模拟listview增删
        self.saved = True# 是否已保存

        width = 500
        height = 600
        geometry = '%dx%d' % (width, height)
        self.geometry(geometry)
        self.iconbitmap('./logo.ico')
        self.resizable(False, False)
        self.update_idletasks()
        if themename == 'dark':
            set_window_dark(self)
        self.focus_set()

        self.ui = BasicTinUI(self, background='#f3f3f3')
        self.ui.pack(fill=tk.BOTH, expand=True)
        self.uixml = TinUIXml(theme(self.ui))
        self.uixml.environment({
            'save_task': self.save_task,
            'add_task_cmd': self.add_task_cmd,
            'add_task_cmds': self.add_task_cmds,
            'add_task_task': self.add_task_task,
            'add_workspace': self.add_workspace,
            'add_tip': self.add_task_tip,
            'run_task': self.run_task,
            'set_cwd': self.set_cwd,
            'create_task_lnk': self.create_task_lnk,
            'open_local': self.open_local,
            'set_priority': self.set_priority,
        })
        with open('./ui-asset/editor.xml', 'r', encoding='utf-8') as f:
            self.uixml.loadxml(f.read())
        self.entry = self.uixml.tags['entry'][0]
        self.entryfunc = self.uixml.tags['entry'][1]
        self.entry.config(disabledbackground=self.entry.cget('background'), disabledforeground=self.entry.cget('foreground'))
        self.view = self.uixml.tags['view'][-2]
        _, ratingbarBack, self.ratingbar, _ = self.uixml.tags['ratingbar']
        self.ui.itemconfig(ratingbarBack, outline='#f3f3f3' if themename == 'light' else '#202020')

        self.entry.insert(0, task)
        self.entry.var.trace_add('write', self.contentChanged)
        if not name_changeable:
            self.entry.config(state='disabled')
        
        self.renew_title()
        self.protocol("WM_DELETE_WINDOW", self.close)

        with open('./ui-asset/editor-cmd.xml', 'r', encoding='utf-8') as f:
            self.cmdxml = f.read()
        with open('./ui-asset/editor-cmds.xml', 'r', encoding='utf-8') as f:
            self.cmdsxml = f.read()
        with open('./ui-asset/editor-task.xml', 'r', encoding='utf-8') as f:
            self.taskxml = f.read()
        with open('./ui-asset/editor-wsp.xml', 'r', encoding='utf-8') as f:
            self.wspxml = f.read()
        with open('./ui-asset/editor-tip.xml', 'r', encoding='utf-8') as f:
            self.tipxml = f.read()
        
        self.load_task()
        self.callback = callback
        self.flag = flag

        if self.task != '':
            task_editors[self.task] = self
        
        self.bind("<Control-w>", lambda e: self.close())
        self.bind("<Control-s>", self.save_task)
        self.bind("<Control-r>", self.run_task)
        self.bind("<Control-e>", self.set_cwd)
        self.bind("<Alt-a>", self.toggle_priority)
        self.bind("<Alt-f>", self.open_local)
        self.bind("<Alt-c>", self.add_task_cmd)
        self.bind("<Alt-s>", self.add_task_cmds)
        self.bind("<Alt-t>", self.add_task_task)
        self.bind("<Alt-w>", self.add_workspace)
        self.bind("<Alt-i>", self.add_task_tip)
    
    def renew_title(self):
        # 更新标题
        if self.task == '':
            title = "QuickUp 任务编辑器"
        else:
            title = "QuickUp 任务编辑器 - " + self.task
        if not self.saved:
            title += " (未保存)"
        self.title(title)
    
    def load_task(self):
        # 加载任务
        if self.task == '':
            self.original_rate = False
            return
        with open(datas.workspace + self.task + '.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.data['cwd'] = json_data.get('cwd', '')
            self.data['tasks'] = json_data['tasks']
            self.original_rate = self.data['rate'] = json_data.get('rate', False)
            if self.data['rate']:
                self.ratingbar.setrate(1)
        for one in self.data['tasks']:
            if one['type'] == 'cmd':
                self.add_task_cmd(None, one['target'], one['args'], one['admin'], False, one.get('max', False), one.get('min', False))
            elif one['type'] == 'wcmd':
                self.add_task_cmd(None, one['target'], one['args'], one['admin'], True, one.get('max', False), one.get('min', False))
            elif one['type'] == 'cmds':
                self.add_task_cmds(None, one['cmds'], one['cmd'], one['wait'])
            elif one['type'] == 'task':
                self.add_task_task(None, one['task'])
            elif one['type'] == 'wsp':
                self.add_workspace(None, one['name'])
            elif one['type'] == 'tip':
                self.add_task_tip(None, one['tip'], one['wait'], one['show'], one['top'])
        self.saved = True
        self.renew_title()
    
    def save_task(self, e) -> bool:
        # 保存任务
        # 返回True表示保存成功，False表示保存失败
        name = self.entry.get()
        # 判断任务名是否符合Windows系统文件名规范
        if not is_valid_windows_filename(name):
            self.saved = False
            d = Dialog(self, "error", themename)
            show_dialog(d, "无法保存", "任务名不符合Windows系统文件名规范", "msg", theme=themename)
            return False
        # 判断之前是否是空task名，或者有没有更改名称
        if self.task == '' and name != '':
            # 新建任务
            oldname = self.task
            self.task = name
            self.data['name'] = name
            filename = datas.workspace + self.task + '.json'
            if os.path.exists(filename):
                self.saved = False
                d = Dialog(self, "error", themename)
                show_dialog(d, "无法保存", "任务名已存在", "msg", theme=themename)
                self.task = oldname
                return False
            task_editors[self.task] = self
        elif self.task != '' and name != '' and name != self.task:
            # 重命名任务
            oldname = self.task
            self.task = name
            self.data['name'] = name
            filename = datas.workspace + self.task + '.json'
            if os.path.exists(filename):
                self.saved = False
                d = Dialog(self, "error", themename)
                show_dialog(d, "无法保存", "任务名已存在", "msg", theme=themename)
                self.task = oldname
                return False
            os.rename(datas.workspace + oldname + '.json', datas.workspace + self.task + '.json')
            del task_editors[oldname]
            task_editors[self.task] = self
            if self.flag == "EDIT":
                self.callback(oldname, self.task)
        elif self.task == '' or name == '':
            # 空任务名，不保存
            self.saved = False
            d = Dialog(self, "info", themename)
            show_dialog(d, "提示", "任务名不能为空", "msg", theme=themename)
            return False
        else:
            # 保存任务
            filename = datas.workspace + self.task + '.json'
        # 从self.tasks中取出数据，生成json
        self.data['tasks'] = []
        for one in self.tasks:
            self.data['tasks'].append(one.get())
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
        # 置顶优先级
        if self.data['rate'] != self.original_rate:
            if not os.path.exists(datas.workspace + 'priority.txt'):
                # 创建空文件
                with open(datas.workspace + 'priority.txt', 'w', encoding='utf-8') as f:
                    pass
            with open(datas.workspace + 'priority.txt', 'a+', encoding='utf-8') as f:
                if self.data['rate']:
                    f.write(self.task + '\n')
                else:
                    f.seek(0)
                    lines = f.readlines()
                    lines = [line.strip() for line in lines]
                    if self.task in lines:
                        lines.remove(self.task)
                    f.seek(0)
                    f.truncate()
                    f.write('\n'.join(lines))
                    if len(lines) != 0:
                        f.write('\n')
            self.original_rate = self.data['rate']
        self.saved = True
        self.renew_title()
        return True

    def run_task(self, e):
        # 运行任务
        if self.save_task(None):
            run_task(self.task)
    
    def set_cwd(self, e):
        # 设置当前工作目录
        d = Dialog(self, "string", themename)
        cwd = show_dialog(d, f"设置工作目录 - {self.task}", "请输入该任务工作目录"+"\t"*5, "input", theme=themename, input=self.data['cwd'])
        if cwd is not None:
            if cwd != self.data['cwd']:
                self.data['cwd'] = cwd
                self.saved = False
                self.renew_title()
    
    def create_task_lnk(self, e):
        # 创建快捷方式
        if self.task == '' or not self.saved:
            d = Dialog(self, "error", themename)
            show_dialog(d, "无法创建快捷方式", "请先保存任务", "msg", theme=themename)
            return
        create_task_lnk(self, self.task)
    
    def open_local(self, e):
        # 打开本地文件
        if self.task == '':
            d = Dialog(self, "error", themename)
            show_dialog(d, "无法打开文件", "请先保存任务", "msg", theme=themename)
            return
        if not os.path.exists(datas.workspace + self.task + '.json'):
            d = Dialog(self, "error", themename)
            show_dialog(d, "无法打开文件", "任务文件不存在", "msg", theme=themename)
            return
        subprocess.Popen(f'explorer /select,"{os.path.join(datas.workspace, self.task + ".json").replace('/', '\\')}"')

    def set_priority(self, num):
        # 设置优先级
        if num == 1 and self.data['rate'] == True:
            return
        self.data['rate'] = True if num == 1 else False
        self.saved = False
        self.renew_title()
    
    def toggle_priority(self, e):
        # 切换优先级
        if self.data['rate'] == True:
            self.ratingbar.setrate(0)
        else:
            self.ratingbar.setrate(1)

    def contentChanged(self, *args):
        # 内容发生变化
        if self.saved:
            self.saved = False
            self.renew_title()
    
    def add_task_cmd(self, e, target:str="", args:str="", admin:bool=False, wait:bool=False, runmax:bool=False, runmin:bool=False):
        # 添加命令任务
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e: on_ui_destroy(uixml))
        task = CmdEditor(uixml, self)
        uixml.environment({
            'delete_task': lambda e, task=task: self.delete_task(task),
        })
        uixml.loadxml(self.cmdxml)
        task.contentChanged = self.contentChanged
        task.init(target, args, admin, wait, runmax, runmin)
        targetEntry = uixml.tags['targetEntry'][0]
        argsEntry = uixml.tags['argsEntry'][0]
        targetEntry.var.trace_add('write', self.contentChanged)
        argsEntry.var.trace_add('write', self.contentChanged)
        self.tasks.append(task)
    
    def add_task_cmds(self, e, cmds:list=[], cmd:str='cmd', wait:bool=False):
        # 添加命令行任务
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e: on_ui_destroy(uixml))
        task = CmdsEditor(uixml)
        uixml.environment({
            'delete_task': lambda e, task=task: self.delete_task(task),
            'if_wait': None,
            'set_shell': None,
        })
        uixml.loadxml(self.cmdsxml)
        task.contentChanged = self.contentChanged
        task.init(cmds, cmd, wait)
        self.tasks.append(task)
    
    def add_task_task(self, e, stask:str=""):
        # 添加子任务
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e: on_ui_destroy(uixml))
        task = TaskEditor(uixml)
        task.root = self
        uixml.environment({
            'edit_task': None,
            'delete_task': lambda e, task=task: self.delete_task(task),
        })
        uixml.loadxml(self.taskxml)
        task.init(stask)
        taskEntry = uixml.tags['taskEntry'][0]
        taskEntry.var.trace_add('write', self.contentChanged)
        self.tasks.append(task)
    
    def add_workspace(self, e, name:str=""):
        # 添加工作区组
        if name == '':
            d = Dialog(self, "input", themename)
            name = show_dialog(d, "添加工作区组", "请输入工作区组名称"+"\t"*5, "input", theme=themename)
            if name is None or name == '':
                return
            if not os.path.exists(datas.workspace + name):
                d = Dialog(self, "warning", themename)
                res = show_dialog(d, "添加工作区组", f"工作区组 {name} 不存在，是否创建？", "msg", theme=themename)
                if res:
                    os.makedirs(datas.workspace + name)
                else:
                    return
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e: on_ui_destroy(uixml))
        task = WspEditor(uixml)
        task.root = self
        uixml.environment({
            'open_quickup': None,
            'delete_task': lambda e, task=task: self.delete_task(task),
        })
        uixml.loadxml(self.wspxml)
        task.init(name)
        wspEntry = uixml.tags['wspEntry'][0]
        wspEntry.var.trace_add('write', self.contentChanged)
        self.tasks.append(task)

    def add_task_tip(self, e, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
        # 添加备注
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = theme(ui)
        ui.bind('<Destroy>', lambda e: on_ui_destroy(uixml))
        task = TipEditor(uixml)
        task.root = self
        uixml.environment({
            'delete_task': lambda e, task=task: self.delete_task(task),
            'if_wait': None,
            'show_tip': None,
            'top_tip': None,
        })
        uixml.loadxml(self.tipxml)
        task.contentChanged = self.contentChanged
        task.init(tip, wait, show, top)
        self.tasks.append(task)

    def delete_task(self, task:Union[CmdEditor, TaskEditor]):
        # 删除任务
        self.saved = False
        self.renew_title()
        index = self.tasks.index(task)
        self.view.delete(index)
        self.tasks.remove(task)
    
    def cmd_run_as_admin(self, task:CmdEditor, tag:bool):
        # 命令行任务是否启用管理员权限
        self.saved = False
        self.renew_title()
        task.admin = tag
    
    def close(self):
        # 关闭编辑器
        if not self.saved:
            if config.settings['advanced']['autoSave']:
                # 自动保存
                res = True
            else:
                d = Dialog(self, "question", themename)
                res = show_dialog(d, "关闭编辑器", f"是否保存对 {self.task} 的更改?", "msg", theme=themename)
            if res:
                isSaved = self.save_task(None)
                if not isSaved:
                    # 保存失败，取消关闭
                    return
            elif res == False:
                pass
            else:
                # 取消关闭
                return
        self.destroy()
        if self.task != '':
            del task_editors[self.task]
            if self.flag == "NEW" and self.callback:
                self.callback(self.task)
        del self.uixml
        del self.data
        del self.tasks
        del self.ui
        del self.entryfunc
        del self.view
        del self.cmdxml
        del self


def create_editor(task:str='', callback=None, flag="EDIT", name_changeable=True):
    # 创建编辑器
    if task != '' and task in task_editors:
        # 任务编辑器已存在，激活
        task_editors[task].deiconify()
        task_editors[task].lift()
        if not name_changeable:
            task_editors[task].entry.config(state='disabled')
        else:
            task_editors[task].entry.config(state='normal')
        return
    Editor(task, callback, flag, name_changeable)
