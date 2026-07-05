# ./ui/editor/taskeditor.py
"""
子任务编辑器 - 支持 task 类型
"""
from tinui import TinUIXml
from tinui.TinUIDialog import Dialog
from ui.utils import show_dialog
import datas
from . import base


class TaskEditor:

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'task'
        self.task = ''
        self.root = None
        self._destroyed = False

    def init(self, task:str=""):
        self.uixml.funcs['edit_task'] = self.edit_task
        self.taskEntry = self.uixml.tags['taskEntry'][0]
        self.taskEntry.bind("<Enter>", lambda _: self.uixml.realui.event_generate("<Enter>"), True)
        self.taskEntry.bind("<FocusIn>", lambda _: self.uixml.realui.event_generate("<Button-1>"), True)
        self.task_trace = None
        self.task = task
        self.taskEntry.insert(0, task)

    def on_destroy(self, _):
        if self._destroyed:
            return
        self._destroyed = True
        if self.task_trace:
            self.taskEntry.var.trace_remove('write', self.task_trace)
        self.uixml.clean()

    def edit_task(self, e):
        task_name = self.taskEntry.get()
        if task_name == '' or task_name not in datas.all_tasks_name:
            d = Dialog(self.root, "error", base.themename)
            show_dialog(d, "无法编辑", f"任务 {task_name} 不存在", "msg", theme=base.themename)
            return
        from .editor import create_editor
        create_editor(task_name, None, "EDIT", False)

    def get(self):
        self.task = self.taskEntry.get()
        return {
            "type": self.type,
            "task": self.task,
        }
