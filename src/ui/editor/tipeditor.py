# ./ui/editor/tipeditor.py
"""
提示编辑器 - 支持 tip 类型
"""
from tinui import TinUIXml
from . import base


class TipEditor:

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'tip'
        self.tip = ''
        self.wait = False
        self.show = True
        self.top = False
        self.contentChanged = None
        self._destroyed = False

    def init(self, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
        self.modified_bind = None
        self.uixml.funcs['if_wait'] = self.change_wait_state
        self.uixml.funcs['show_tip'] = self.change_show_state
        self.uixml.funcs['top_tip'] = self.change_top_state
        self.textbox = self.uixml.tags['textbox'][0]
        self.textbox.bind("<Enter>", lambda _: self.uixml.realui.event_generate("<Enter>"), True)
        self.textbox.bind("<FocusIn>", lambda _: self.uixml.realui.event_generate("<Button-1>"), True)
        self.wbutton = self.uixml.tags['wbutton'][-2]
        self.wbuttont = self.uixml.tags['wbutton'][0]
        self.tipcheckbox = self.uixml.tags['tipcheckbox'][-2]
        self.topcheckbox = self.uixml.tags['topcheckbox'][-2]
        if wait:
            self.wbutton.on()
        if show:
            self.tipcheckbox.on()
        else:
            self.show = False
        if top:
            self.topcheckbox.on()
        if base.themename == 'dark':
            self.textbox.config(insertbackground='#ffffff')
        self.textbox.insert('end', tip)
        self.textbox.edit_modified(False)
        self.textbox.update()
        self.modified_bind = self.textbox.bind('<<Modified>>', self.textContentChanged)
        self.textbox.bind('<Destroy>', self.on_destroy)

    def on_destroy(self, _):
        if self._destroyed:
            return
        self._destroyed = True
        if self.modified_bind:
            self.textbox.unbind('<<Modified>>', self.modified_bind)
        self.uixml.clean()

    def textContentChanged(self, e):
        self.textbox.edit_modified(False)
        self.contentChanged(None)

    def change_wait_state(self, flag):
        if flag:
            self.uixml.realui.itemconfig(self.wbuttont, text='单线')
            self.wait = True
        else:
            self.uixml.realui.itemconfig(self.wbuttont, text='并行')
            self.wait = False
        self.contentChanged(None)

    def change_show_state(self, tag):
        self.show = tag
        self.contentChanged(None)

    def change_top_state(self, tag):
        self.top = tag
        self.contentChanged(None)

    def get(self):
        self.tip = self.textbox.get('1.0', 'end').strip()
        return {
            "type": self.type,
            "tip": self.tip,
            "wait": self.wait,
            "show": self.show,
            "top": self.top,
        }
