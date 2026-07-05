# ./ui/editor/cmdeditor.py
"""
命令任务编辑器 - 支持 cmd/wcmd 类型
"""
import os
import tkinter as tk
from webbrowser import open as webopen
from tinui import BasicTinUI, TinUIXml
from tinui.TinUIDialog import Dialog
from ui.utils import show_dialog
from cppextend.QUmodule import enable_entry_drop, disable_entry_drop
import datas
from . import base


class CmdEditor:

    def __init__(self, uixml:TinUIXml, ui:BasicTinUI, editor):
        self.uixml = uixml
        self.ui = ui
        self.type = 'cmd'
        self.target = ''
        self.args = ''
        self.admin = False
        self.runMAX = False
        self.runMIN = False
        self.pos = []
        self.zone_round = False
        self.contentChanged = None
        self.editor = editor
        self.zone_set_ui:BasicTinUI = None
        self._destroyed = False

    def init(self, target:str="", args:str="", admin:bool=False, wait:bool=False, runMAX:bool=False, runMIN:bool=False, pos:list=[], zone_round:bool=False):
        self.targetEntry = self.uixml.tags['targetEntry'][0]
        self.targetEntry.bind("<Enter>", lambda _: self.ui.event_generate("<Enter>"), True)
        self.targetEntry.bind("<FocusIn>", lambda _: self.ui.event_generate("<Button-1>"), True)
        self.argsEntry = self.uixml.tags['argsEntry'][0]
        self.argsEntry.bind("<Enter>", lambda _: self.ui.event_generate("<Enter>"), True)
        self.argsEntry.bind("<FocusIn>", lambda _: self.ui.event_generate("<Button-1>"), True)
        self.target_trace = None
        self.args_trace = None
        self.flyoutui:BasicTinUI = self.uixml.tags['flyout'][0]
        flyoutuixml:TinUIXml = self.uixml.tags['flyout'][1]
        del flyoutuixml.ui
        flyoutuixml.ui = base.theme(self.flyoutui, accent=base.accent_color)
        flyoutuixml.funcs.update({
            'if_wait': self.change_wait_state,
            'run_as_admin': None,
            'run_max': self.run_max,
            'run_min': self.run_min,
            'open_zone_set': self.open_zone_set
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
        flyoutuixml.funcs.update({'run_as_admin': self.run_as_admin})
        self.flyoutuixml = flyoutuixml
        if wait:
            self.wbutton.on()
        if runMAX:
            self.maxcheckbox.on()
        if runMIN:
            self.mincheckbox.on()
        self.target = target
        self.args = args
        self.admin = admin
        self.pos = pos
        self.zone_round = zone_round
        self.targetEntry.insert(0, target)
        self.dt = enable_entry_drop(self.targetEntry.winfo_id(), self.target_drop)
        self.targetEntry.bind('<Destroy>', self.on_destroy)
        self.argsEntry.insert(0, args)

    def on_destroy(self, _):
        if self._destroyed:
            return
        self._destroyed = True
        disable_entry_drop(self.dt)
        del self.dt
        if self.target_trace:
            self.targetEntry.var.trace_remove('write', self.target_trace)
        if self.args_trace:
            self.argsEntry.var.trace_remove('write', self.args_trace)
        self.targetEntry.unbind('<Destroy>')
        self.uixml.clean()
        self.flyoutuixml.clean()

    def run_as_admin(self, tag):
        self.admin = tag
        self.contentChanged(None)

    def change_wait_state(self, flag):
        if flag:
            self.type = 'wcmd'
            self.flyoutui.itemconfig(self.wbuttont, text='单线')
        else:
            self.type = 'cmd'
            self.flyoutui.itemconfig(self.wbuttont, text='并行')
        self.contentChanged(None)

    def run_max(self, tag):
        self.runMAX = tag
        self.contentChanged(None)

    def run_min(self, tag):
        self.runMIN = tag
        self.contentChanged(None)

    def open_zone_set(self, _):
        self.zone_set_ui = BasicTinUI(self.ui.master)
        self.zone_set_ui.set_scale(datas.scale_factor)
        self.zone_set_ui.pack(fill='both', expand=True)
        zone_set_ui_xml = TinUIXml(base.theme(self.zone_set_ui, accent=base.accent_color))
        zone_set_ui_xml.environment({
            'about-zone': self.about_zone_set,
            'delete': self.delete_zone_set,
            'save': self.save_zone_set,
            'close': self.close_zone_set,
            'lrs-l': None,
            'lrs-r': None,
            'lcrs-l': None,
            'lcrs-c': None,
            'lcrs-r': None,
            'lr-lb': None,
            'lr-ls': None,
            'lr-rb': None,
            'lr-rs': None,
            'quad-lt': None,
            'quad-rt': None,
            'quad-lb': None,
            'quad-rb': None,
            'keep-round': None,
        })
        with open('./ui-asset/zoneset.xml', 'r', encoding='utf-8') as f:
            xml = f.read().replace("%SCREENINFO%", base.screen_info)
            zone_set_ui_xml.loadxml(xml)
        self.zoneroundcheck = zone_set_ui_xml.tags['zoneroundcheck'][-2]
        if self.zone_round:
            self.zoneroundcheck.on()
        appentry:tk.Entry = zone_set_ui_xml.tags['appentry'][0]
        appentry.insert(0, self.targetEntry.get())
        appentry.config(state='readonly', readonlybackground=appentry.cget('background'))
        self.zone_set_ui.xentry = zone_set_ui_xml.tags['xentry'][0]
        self.zone_set_ui.yentry = zone_set_ui_xml.tags['yentry'][0]
        self.zone_set_ui.wentry = zone_set_ui_xml.tags['wentry'][0]
        self.zone_set_ui.hentry = zone_set_ui_xml.tags['hentry'][0]
        zone_set_ui_xml.funcs.update({
            'lrs-l': lambda _:self.__set_rect(*base.screen_rects['lrs'][0]),
            'lrs-r': lambda _:self.__set_rect(*base.screen_rects['lrs'][1]),
            'lcrs-l': lambda _:self.__set_rect(*base.screen_rects['lcrs'][0]),
            'lcrs-c': lambda _:self.__set_rect(*base.screen_rects['lcrs'][1]),
            'lcrs-r': lambda _:self.__set_rect(*base.screen_rects['lcrs'][2]),
            'lr-lb': lambda _:self.__set_rect(*base.screen_rects['lr'][0]),
            'lr-ls': lambda _:self.__set_rect(*base.screen_rects['lr'][1]),
            'lr-rb': lambda _:self.__set_rect(*base.screen_rects['lr'][2]),
            'lr-rs': lambda _:self.__set_rect(*base.screen_rects['lr'][3]),
            'quad-lt': lambda _:self.__set_rect(*base.screen_rects['quad'][0]),
            'quad-rt': lambda _:self.__set_rect(*base.screen_rects['quad'][1]),
            'quad-lb': lambda _:self.__set_rect(*base.screen_rects['quad'][2]),
            'quad-rb': lambda _:self.__set_rect(*base.screen_rects['quad'][3]),
            'keep-round': self.keep_zone_round
        })
        if self.pos:
            self.zone_set_ui.xentry.insert(0, str(self.pos[0]))
            self.zone_set_ui.yentry.insert(0, str(self.pos[1]))
            self.zone_set_ui.wentry.insert(0, str(self.pos[2]))
            self.zone_set_ui.hentry.insert(0, str(self.pos[3]))

    def about_zone_set(self, _):
        webopen('https://quickup.smart-space.com.cn/QuickUp-zone/')

    def delete_zone_set(self, _):
        self.pos = ()
        self.contentChanged(None)
        self.close_zone_set(None)

    def save_zone_set(self, _):
        x_str = self.zone_set_ui.xentry.get()
        y_str = self.zone_set_ui.yentry.get()
        w_str = self.zone_set_ui.wentry.get()
        h_str = self.zone_set_ui.hentry.get()
        if x_str.isdigit() and y_str.isdigit() and w_str.isdigit() and h_str.isdigit():
            x = int(x_str)
            y = int(y_str)
            w = int(w_str)
            h = int(h_str)
            self.pos = (x, y, w, h)
        else:
            d = Dialog(self.editor, "error", base.themename)
            show_dialog(d, "错误", "位置参数必须为数字", "msg", theme=base.themename)
            return
        self.contentChanged(None)
        self.close_zone_set(None)

    def close_zone_set(self, _):
        self.zone_set_ui.destroy()
        self.zone_set_ui = None

    def keep_zone_round(self, tag):
        self.zone_round = tag
        self.contentChanged(None)

    def target_drop(self, file):
        if os.path.isfile(file):
            self.targetEntry.delete(0, 'end')
            self.targetEntry.insert(0, file)
        else:
            self.targetEntry.delete(0, 'end')
            self.targetEntry.insert(0, f'shell:AppsFolder\\{file}')

    def __set_rect(self, x, y, w, h):
        self.zone_set_ui.xentry.delete(0, 'end')
        self.zone_set_ui.yentry.delete(0, 'end')
        self.zone_set_ui.wentry.delete(0, 'end')
        self.zone_set_ui.hentry.delete(0, 'end')
        self.zone_set_ui.xentry.insert(0, str(x))
        self.zone_set_ui.yentry.insert(0, str(y))
        self.zone_set_ui.wentry.insert(0, str(w))
        self.zone_set_ui.hentry.insert(0, str(h))

    def get(self):
        self.target = self.targetEntry.get()
        self.args = self.argsEntry.get()
        return {
            "type": self.type,
            "target": self.target,
            "args": self.args,
            "admin": self.admin,
            "max": self.runMAX,
            "min": self.runMIN,
            "pos": self.pos,
            "zone_round": self.zone_round,
        }
