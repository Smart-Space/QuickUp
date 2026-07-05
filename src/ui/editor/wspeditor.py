# ./ui/editor/wspeditor.py
"""
工作区编辑器 - 支持 wsp 类型
"""
import os
from tinui import TinUIXml
from tinui.TinUIDialog import Dialog
from ui.utils import show_dialog
from runner.runtask import run_cmd
import datas
from . import base


class WspEditor:

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'wsp'
        self.name = ''
        self.root = None
        self._destroyed = False

    def init(self, name:str=""):
        self.uixml.funcs['open_quickup'] = self.open_quickup
        self.wspEntry = self.uixml.tags['wspEntry'][0]
        self.wspEntry.bind("<Enter>", lambda _: self.uixml.realui.event_generate("<Enter>"), True)
        self.wspEntry.bind("<FocusIn>", lambda _: self.uixml.realui.event_generate("<Button-1>"), True)
        self.wsp_trace = None
        self.name = name
        self.wspEntry.insert(0, name)

    def on_destroy(self, _):
        if self._destroyed:
            return
        self._destroyed = True
        if self.wsp_trace:
            self.wspEntry.var.trace_remove('write', self.wsp_trace)
        self.uixml.clean()

    def open_quickup(self, e):
        workspace_name = self.wspEntry.get()
        if workspace_name == '' or os.path.exists(datas.workspace + workspace_name) == False:
            d = Dialog(self.root, "error", base.themename)
            show_dialog(d, "无法打开", f"工作区 {workspace_name} 不存在", "msg", theme=base.themename)
            return
        if datas.workname != '.':
            workspace_name = datas.workname + '/' + workspace_name
        run_cmd('QuickUp', 'QuickUp.exe', f'-w "{workspace_name}"', False)

    def get(self):
        self.name = self.wspEntry.get()
        return {
            "type": self.type,
            "name": self.name,
        }
