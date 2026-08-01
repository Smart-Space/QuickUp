# ./ui/editor/editor.py
"""
任务编辑器主窗口 - Editor 类与 create_editor 入口
"""
import os
import subprocess
import json
import tkinter as tk
from weakref import ref, ReferenceType
from typing import Union
from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog

import datas
from runner.runtask import run_task
import config
from ui.utils import set_window_dark, show_dialog, bind_shortcuts
from runner.create_lnk import create_task_lnk
from labels import labelsmng
from cppextend.QUmodule import is_valid_windows_filename, get_work_apps

from . import base
from .base import task_editors
from .cmdeditor import CmdEditor
from .cmdseditor import CmdsEditor
from .taskeditor import TaskEditor
from .wspeditor import WspEditor
from .tipeditor import TipEditor
from .plugineditor import PluginEditor
from .zonerecord import get_dialog as get_zone_record_dialog


class Editor(tk.Toplevel):

    def __init__(self, task:str='', callback=None, flag="EDIT", name_changeable=True):
        super().__init__()
        self.task = task
        self.data = {"name": task, "cwd": "", "tasks": [], "rate": False}
        self.tasks = []
        self.saved = True
        self.hidden = False
        self.task_index = None

        width = int(500*datas.scale_factor)
        height = int(630*datas.scale_factor)
        geometry = '%dx%d' % (width, height)
        self.geometry(geometry)
        self.iconbitmap('./logo.ico')
        self.resizable(False, False)
        self.update_idletasks()
        if base.themename == 'dark':
            set_window_dark(self)
        self.focus_set()

        self.ui = BasicTinUI(self, background='#f3f3f3')
        self.ui.set_scale(datas.scale_factor)
        self.ui.pack(fill=tk.BOTH, expand=True)
        self.uixml = TinUIXml(base.theme(self.ui, accent=base.accent_color))
        self.uixml.environment({
            'save_task': self.save_task,
            'add_task_cmd': self.add_task_cmd,
            'add_task_cmds': self.add_task_cmds,
            'add_task_task': self.add_task_task,
            'add_workspace': self.add_workspace,
            'add_tip': self.add_task_tip,
            'add_plugin': self.add_plugin,
            'run_task': self.run_task,
            'set_cwd': self.set_cwd,
            'create_task_lnk': self.create_task_lnk,
            'open_local': self.open_local,
            'set_priority': self.set_priority,
            'if_hide_task': None,
            'record_apps': self.record_apps,
            'select_task': self.select_task,
            'add_label': self.add_label,
        })
        with open('./ui-asset/editor.xml', 'r', encoding='utf-8') as f:
            self.uixml.loadxml(f.read())
        self.entry = self.uixml.tags['entry'][0]
        self.entryfunc = self.uixml.tags['entry'][1]
        self.entry.config(disabledbackground=self.entry.cget('background'), disabledforeground=self.entry.cget('foreground'))
        self.view = self.uixml.tags['view'][-2]
        self.ratingtext, _, _, self.ratingbar, _ = self.uixml.tags['ratingbar']

        hidebuttons = self.uixml.tags['hidebutton']
        self.hidebutton = hidebuttons[-2]
        self.hidebutton_icon = hidebuttons[0]
        if self.task.endswith('[x]'):
            self.hidebutton.on()
            self.ui.itemconfig(self.hidebutton_icon, text='\uED1A')
            self.hidden = True
        self.uixml.funcs.update({'if_hide_task': self.if_hide_task})

        self.entry_trace = None
        self.entry.insert(0, task)
        self.entry_trace = self.entry.var.trace_add('write', self.contentChanged)
        if not name_changeable:
            self.entry.config(state='disabled')

        self.labels = self.uixml.tags['labels'][-2]
        if self.task != '':
            tags = labelsmng.find_labels_by_task(self.task)
            for tag in tags:
                self.labels.add(tag, self.delete_label)

        self.renew_title()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind('<Destroy>', self.on_destroy)
        self.update_idletasks()

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
        with open('./ui-asset/editor-plugin.xml', 'r', encoding='utf-8') as f:
            self.pluginxml = f.read()

        self.load_task()
        self.callback = callback
        self.flag = flag

        if self.task != '':
            task_editors[self.task] = self

        editor_shortcuts = config.get_shortcuts('editor', config.DEFAULT_SHORTCUTS['editor'])
        bind_shortcuts(self, editor_shortcuts, {
            'close': lambda e: self.close(),
            'save': self.save_task,
            'run': self.run_task,
            'set_cwd': self.set_cwd,
            'toggle_priority': self.toggle_priority,
            'open_local': self.open_local,
            'add_cmd': self.add_task_cmd,
            'add_cmds': self.add_task_cmds,
            'add_task': self.add_task_task,
            'add_workspace': self.add_workspace,
            'add_tip': self.add_task_tip,
            'copy_task': self.copy_task,
            'paste_task': self.paste_task,
        })

    def renew_title(self):
        if self.task == '':
            title = "QuickUp 任务编辑器"
        else:
            title = "QuickUp 任务编辑器 - " + self.task
        if not self.saved:
            title += " (未保存)"
        self.title(title)

    def load_task(self):
        if self.task == '':
            self.original_rate = False
            return
        with open(datas.workspace + self.task + '.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.data['cwd'] = json_data.get('cwd', '')
            self.data['tasks'] = json_data['tasks']
            self.original_rate = self.data['rate'] = json_data.get('rate', False)
            if self.data['rate']:
                self.ratingbar.on()
        for one in self.data['tasks']:
            if one['type'] == 'cmd':
                self.add_task_cmd(None, one['target'], one['args'], one['admin'], False, one.get('max', False), one.get('min', False), one.get('pos', ()), one.get('zone_round', False))
            elif one['type'] == 'wcmd':
                self.add_task_cmd(None, one['target'], one['args'], one['admin'], True, one.get('max', False), one.get('min', False), one.get('pos', ()), one.get('zone_round', False))
            elif one['type'] == 'cmds':
                self.add_task_cmds(None, one['cmds'], one['cmd'], one['wait'])
            elif one['type'] == 'task':
                self.add_task_task(None, one['task'])
            elif one['type'] == 'wsp':
                self.add_workspace(None, one['name'])
            elif one['type'] == 'tip':
                self.add_task_tip(None, one['tip'], one['wait'], one['show'], one['top'])
            elif one['type'] == 'plugin':
                self.add_plugin(None, one['name'], one['args'], one['wait'])
        self.saved = True
        self.renew_title()

    def save_task(self, e) -> bool:
        name = self.entry.get()
        if not is_valid_windows_filename(name.upper()):
            self.saved = False
            d = Dialog(self, "error", base.themename)
            show_dialog(d, "无法保存", "任务名不符合Windows系统文件名规范", "msg", theme=base.themename)
            return False
        if self.task == '' and name != '':
            oldname = self.task
            self.task = name
            self.data['name'] = name
            filename = datas.workspace + self.task + '.json'
            if os.path.exists(filename):
                self.saved = False
                d = Dialog(self, "error", base.themename)
                show_dialog(d, "无法保存", "任务名已存在", "msg", theme=base.themename)
                self.task = oldname
                return False
            task_editors[self.task] = self
        elif self.task != '' and name != '' and name != self.task:
            oldname = self.task
            self.task = name
            self.data['name'] = name
            filename = datas.workspace + self.task + '.json'
            if os.path.exists(filename):
                self.saved = False
                d = Dialog(self, "error", base.themename)
                show_dialog(d, "无法保存", "任务名已存在", "msg", theme=base.themename)
                self.task = oldname
                return False
            if self.task.endswith('[x]'):
                d = Dialog(self, "warning", base.themename)
                show_dialog(d, "QuickUp 隐藏任务", "任务名以[x]结尾表示隐藏，将在下次启动QuickUp之后不再显示在任务列表中。" \
                "放心，这仍然是一个可用的任务，你可以随时通过其它任务或者QuickUp命令行运行它，别忘了\"[x]\"是它名字的一部分。" \
                "\n\n你可以随时将任务文件名的隐藏标记\"[x]\"去掉。", "msg", theme=base.themename)
            os.rename(datas.workspace + oldname + '.json', datas.workspace + self.task + '.json')
            del task_editors[oldname]
            task_editors[self.task] = self
            labelsmng.rename_task(oldname, self.task)
            if self.data['rate']:
                datas.rename_priority(oldname, self.task)
            if self.flag == "EDIT":
                self.callback(oldname, self.task)
        elif self.task == '' or name == '':
            self.saved = False
            d = Dialog(self, "info", base.themename)
            show_dialog(d, "提示", "任务名不能为空", "msg", theme=base.themename)
            return False
        else:
            filename = datas.workspace + self.task + '.json'
        self.data['tasks'] = []
        for one in self.tasks:
            self.data['tasks'].append(one.get())
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)
        if self.data['rate'] != self.original_rate:
            if self.data['rate']:
                datas.add_priority(self.task)
            else:
                datas.remove_priority(self.task)
            self.original_rate = self.data['rate']
        if self.task.endswith('[x]'):
            if not self.hidden:
                self.hidden = True
                self.hidebutton.on()
        else:
            if self.hidden:
                self.hidden = False
                self.hidebutton.off()

        self.saved = True
        self.renew_title()
        return True

    def run_task(self, _):
        if self.save_task(None):
            run_task(self.task)

    def set_cwd(self, _):
        d = Dialog(self, "string", base.themename)
        cwd = show_dialog(d, f"设置工作目录 - {self.task}", "请输入该任务工作目录"+"\t"*5, "input", theme=base.themename, input=self.data['cwd'])
        if cwd is not None:
            if cwd != self.data['cwd']:
                self.data['cwd'] = cwd
                self.saved = False
                self.renew_title()

    def create_task_lnk(self, _):
        if self.task == '' or not self.saved:
            d = Dialog(self, "error", base.themename)
            show_dialog(d, "无法创建快捷方式", "请先保存任务", "msg", theme=base.themename)
            return
        create_task_lnk(self, self.task)

    def open_local(self, _):
        if self.task == '':
            d = Dialog(self, "error", base.themename)
            show_dialog(d, "无法打开文件", "请先保存任务", "msg", theme=base.themename)
            return
        if not os.path.exists(datas.workspace + self.task + '.json'):
            d = Dialog(self, "error", base.themename)
            show_dialog(d, "无法打开文件", "任务文件不存在", "msg", theme=base.themename)
            return
        subprocess.Popen(f'explorer /select,"{os.path.join(datas.workspace, self.task + ".json").replace('/', '\\')}"')

    def if_hide_task(self, tag):
        name = self.entry.get()
        if tag:
            self.ui.itemconfig(self.hidebutton_icon, text='\uED1A')
            if not name.endswith('[x]'):
                self.entry.delete(0, 'end')
                self.entry.insert(0, name+'[x]')
        else:
            self.ui.itemconfig(self.hidebutton_icon, text='\uE7B3')
            if name.endswith('[x]'):
                self.entry.delete(0, 'end')
                self.entry.insert(0, name[:-3])
        self.hidden = tag
        self.contentChanged(None)

    def set_priority(self, tag:bool):
        if tag:
            self.ui.itemconfig(self.ratingtext, text='\uE735')
            if self.data['rate'] == True:
                return
        else:
            self.ui.itemconfig(self.ratingtext, text='\uE734')
        self.data['rate'] = tag
        self.saved = False
        self.renew_title()

    def toggle_priority(self, _):
        if self.data['rate'] == True:
            self.ratingbar.off()
        else:
            self.ratingbar.on()

    def contentChanged(self, *args):
        if self.saved:
            self.saved = False
            self.renew_title()

    def record_apps(self, _):
        res, record_zone, record_round = get_zone_record_dialog(self, base.themename)
        if res:
            apps = get_work_apps()
            for app in apps:
                if os.path.isfile(app["processName"]):
                    task_name = app["processName"]
                else:
                    app_names = app["processName"].split('_')
                    task_name = f'shell:AppsFolder\\{app_names[0]}_{app_names[-1]}!App'
                if not app["isMinimized"] and not app["isMaximized"] and record_zone:
                    rect = app["realRect"]
                    pos = [rect[1]//datas.scale_factor, rect[0]//datas.scale_factor,
                           (rect[3]-rect[1])//datas.scale_factor, (rect[2]-rect[0])//datas.scale_factor]
                    for i in range(len(pos)):
                        pos[i] = int(pos[i])
                else:
                    pos = []
                self.add_task_cmd(None, task_name, app["commandArgs"], False, False, app["isMaximized"], app["isMinimized"], pos, app["isRoundCorner"] if record_round else False)

    def add_task_cmd(self, _, target:str="", args:str="", admin:bool=False, wait:bool=False, runmax:bool=False, runmin:bool=False, pos:list=[], zone_round:bool=False):
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = CmdEditor(uixml, ui, self)
        uixml.environment({
            'delete_task': lambda _, task=ref(task): self.delete_task(task),
        })
        uixml.loadxml(self.cmdxml)
        task.contentChanged = self.contentChanged
        task.init(target, args, admin, wait, runmax, runmin, pos, zone_round)
        targetEntry = uixml.tags['targetEntry'][0]
        argsEntry = uixml.tags['argsEntry'][0]
        task.target_trace = targetEntry.var.trace_add('write', self.contentChanged)
        task.args_trace = argsEntry.var.trace_add('write', self.contentChanged)
        self.tasks.append(task)

    def add_task_cmds(self, _, cmds:list=[], cmd:str='cmd', wait:bool=False):
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = CmdsEditor(uixml)
        uixml.environment({
            'delete_task': lambda _, task=ref(task): self.delete_task(task),
            'if_wait': None,
            'set_shell': None,
        })
        uixml.loadxml(self.cmdsxml)
        task.contentChanged = self.contentChanged
        task.init(cmds, cmd, wait)
        self.tasks.append(task)

    def add_task_task(self, _, stask:str=""):
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = TaskEditor(uixml)
        task.root = self
        uixml.environment({
            'edit_task': None,
            'delete_task': lambda _, task=ref(task): self.delete_task(task),
        })
        uixml.loadxml(self.taskxml)
        task.init(stask)
        taskEntry = uixml.tags['taskEntry'][0]
        task.task_trace = taskEntry.var.trace_add('write', self.contentChanged)
        taskEntry.bind('<Destroy>', task.on_destroy)
        self.tasks.append(task)

    def add_workspace(self, _, name:str=""):
        if name == '':
            d = Dialog(self, "input", base.themename)
            name = show_dialog(d, "添加工作区组", "请输入工作区组名称"+"\t"*5, "input", theme=base.themename)
            if name is None or name == '':
                return
            if not os.path.exists(datas.workspace + name):
                d = Dialog(self, "warning", base.themename)
                res = show_dialog(d, "添加工作区组", f"工作区组 {name} 不存在，是否创建？", "msg", theme=base.themename)
                if res:
                    os.makedirs(datas.workspace + name)
                else:
                    return
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = WspEditor(uixml)
        task.root = self
        uixml.environment({
            'open_quickup': None,
            'delete_task': lambda _, task=ref(task): self.delete_task(task),
        })
        uixml.loadxml(self.wspxml)
        task.init(name)
        wspEntry = uixml.tags['wspEntry'][0]
        task.wsp_trace = wspEntry.var.trace_add('write', self.contentChanged)
        wspEntry.bind('<Destroy>', task.on_destroy)
        self.tasks.append(task)

    def add_task_tip(self, e, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = TipEditor(uixml)
        uixml.environment({
            'delete_task': lambda e, task=ref(task): self.delete_task(task),
            'if_wait': None,
            'show_tip': None,
            'top_tip': None,
        })
        uixml.loadxml(self.tipxml)
        task.contentChanged = self.contentChanged
        task.init(tip, wait, show, top)
        self.tasks.append(task)
    
    def add_plugin(self, e, name:str="", args:str="", wait:bool=False):
        self.saved = False
        self.renew_title()
        ui, _, uixml, _ = self.view.add()
        del uixml.ui
        uixml.ui = base.theme(ui, accent=base.accent_color)
        task = PluginEditor(uixml, self)
        uixml.environment({
            'delete_task': lambda _, task=ref(task): self.delete_task(task),
            'task_pkg_info': None,
            'if_wait': None,
        })
        uixml.loadxml(self.pluginxml)
        task.contentChanged = self.contentChanged
        task.init(name, args, wait)
        self.tasks.append(task)

    def delete_task(self, _task:ReferenceType[Union[CmdEditor, TaskEditor]]):
        task = _task()
        self.saved = False
        self.renew_title()
        index = self.tasks.index(task)
        if self.task_index == index:
            self.task_index = None
        elif self.task_index is not None and self.task_index > index:
            self.task_index -= 1
        self.view.delete(index)
        self.tasks.remove(task)

    def select_task(self, index):
        self.task_index = index

    def add_label(self):
        all_tags = labelsmng.get_labels()
        d = Dialog(self, "listbox", base.themename)
        label = show_dialog(d, "添加标签", "请选择要添加的标签", "choice", theme=base.themename, input=all_tags)
        if label is not None and label != '':
            if label in labelsmng.find_tasks_by_label(self.task):
                d = Dialog(self, "error", base.themename)
                show_dialog(d, "无法添加", f"任务已包含标签 {label}", "msg", theme=base.themename)
                return None, None
            match labelsmng.add_task_to_label(label, self.task):
                case True:
                    return label, self.delete_label
                case 2:
                    d = Dialog(self, "error", base.themename)
                    show_dialog(d, "无法添加", f"任务新建未保存", "msg", theme=base.themename)
                    return None, None
                case False:
                    return None, None
        return None, None

    def delete_label(self, label):
        labelsmng.remove_task_from_label(label, self.task)

    def copy_task(self, _):
        if self.task_index is not None:
            task = self.tasks[self.task_index]
            info = task.get()
            self.clipboard_clear()
            self.clipboard_append(json.dumps(info))

    def paste_task(self, _):
        try:
            clip_info = self.clipboard_get()
            info = json.loads(clip_info)
            match info['type']:
                case 'cmd':
                    self.add_task_cmd(None, info.get('target', ''), info.get('args', ''), info.get('admin', False), False, info.get('max', False), info.get('min', False), info.get('pos', []), info.get('zone_round', False))
                case 'wcmd':
                    self.add_task_cmd(None, info.get('target', ''), info.get('args', ''), info.get('admin', False), True, info.get('max', False), info.get('min', False), info.get('pos', []), info.get('zone_round', False))
                case 'cmds':
                    self.add_task_cmds(None, info.get('cmds', []), info.get('cmd', 'cmd'), info.get('wait', False))
                case 'task':
                    self.add_task_task(None, info.get('task', ''))
                case 'wsp':
                    self.add_workspace(None, info.get('name', ''))
                case 'tip':
                    self.add_task_tip(None, info.get('tip', ''), info.get('wait', False), info.get('show', True), info.get('top', False))
                case 'plugin':
                    self.add_plugin(None, info.get('name', ''), info.get('args', ''), info.get('wait', False))
                case _:
                    pass
        except:
            pass

    def close(self):
        if not self.saved:
            if config.settings['advanced']['autoSave']:
                res = True
            else:
                d = Dialog(self, "question", base.themename)
                res = show_dialog(d, "关闭编辑器", f"是否保存对 {self.task} 的更改?", "msg", theme=base.themename)
            if res:
                isSaved = self.save_task(None)
                if not isSaved:
                    return
            elif res == False:
                pass
            else:
                return
        self.destroy()
        if self.task != '':
            del task_editors[self.task]
            if self.flag == "NEW" and self.callback:
                self.callback(self.task, True)

    def on_destroy(self, _):
        if _.widget is not self:
            return
        if self.entry_trace:
            self.entry.var.trace_remove('write', self.entry_trace)
        for task in self.tasks:
            if hasattr(task, 'on_destroy'):
                task.on_destroy(None)
        self.uixml.clean()
        self.data.clear()
        self.tasks.clear()
        for attr in ('entry_trace',):
            delattr(self, attr)


def create_editor(task:str='', callback=None, flag="EDIT", name_changeable=True):
    if task != '' and task in task_editors:
        task_editors[task].deiconify()
        task_editors[task].lift()
        if not name_changeable:
            task_editors[task].entry.config(state='disabled')
        else:
            task_editors[task].entry.config(state='normal')
        return
    Editor(task, callback, flag, name_changeable)
