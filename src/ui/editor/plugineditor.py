# ./ui/editor/plugineditor.py
"""
插件任务编辑器
"""
from tinui import TinUIXml
from tinui.TinUIDialog import Dialog
from ui.utils import show_dialog
from plugin.manager import plugin_manager
from . import base


class PluginEditor:
    # 插件编辑器
    def __init__(self, uixml:TinUIXml, editor):
        self.uixml = uixml
        self.ui = uixml.realui
        self.type = 'plugin'
        self.name = ''
        self.args = ''
        self.wait = False
        self.editor = editor
        self.contentChanged = None
    
    def init(self, name:str="", args:str="", wait:bool=False):
        # 初始化ui接管
        self.uixml.funcs['if_wait'] = self.if_wait
        self.uixml.funcs['task_pkg_info'] = self.task_pkg_info
        self.pluginEntry = self.uixml.tags['typeEntry'][0]
        self.pluginEntry.bind("<Enter>", lambda _: self.ui.event_generate("<Enter>"), True)
        self.pluginEntry.bind("<FocusIn>", lambda _: self.ui.event_generate("<Button-1>"), True)
        self.name = name
        self.pluginEntry.insert(0, name)
        self.argsEntry = self.uixml.tags['argsEntry'][0]
        self.argsEntry.bind("<Enter>", lambda _: self.ui.event_generate("<Enter>"), True)
        self.argsEntry.bind("<FocusIn>", lambda _: self.ui.event_generate("<Button-1>"), True)
        self.args = args
        self.argsEntry.insert(0, args)
        self.wbutton = self.uixml.tags['wbutton'][-2]
        self.wbuttont = self.uixml.tags['wbutton'][0]
        if wait:
            self.wbutton.on()
    
    def if_wait(self, flag):
        if flag:
            self.uixml.realui.itemconfig(self.wbuttont, text='单线')
            self.wait = True
        else:
            self.uixml.realui.itemconfig(self.wbuttont, text='并行')
            self.wait = False
        self.contentChanged(None)
    
    def task_pkg_info(self, _):
        name = self.pluginEntry.get()
        if name == '':
            return
        plugin_manager._discover_plugins()
        owner = plugin_manager.registry.task_sources.get(name)
        d = Dialog(self.editor, "info", base.themename)
        if owner:
            show_dialog(d, "插件信息", f"功能名称：{name}\n来源拓展：{owner}", "msg", theme=base.themename)
        else:
            show_dialog(d, "插件信息", f"未找到拓展功能：{name}\n请检查功能名称是否正确", "msg", theme=base.themename)

    def get(self):
        # 获取插件数据
        self.name = self.pluginEntry.get()
        self.args = self.argsEntry.get()
        return {
            "type": self.type,
            "name": self.name,
            "args": self.args,
            "wait": self.wait,
        }
