# ./ui/editor/cmdseditor.py
"""
命令行任务编辑器 - 支持 cmds 类型
"""
from tinui import TinUIXml
from . import base


class CmdsEditor:

    def __init__(self, uixml:TinUIXml):
        self.uixml = uixml
        self.type = 'cmds'
        self.cmds = []
        self.cmd = 'cmd'
        self.wait = False
        self.contentChanged = None
        self._destroyed = False

    def init(self, cmds:list=[], cmd:str='cmd', wait:bool=False):
        self.modified_bind = None
        self.uixml.funcs['if_wait'] = self.change_wait_state
        self.uixml.funcs['set_shell'] = self.set_shell
        self.textbox = self.uixml.tags['textbox'][0]
        self.textbox.bind("<Enter>", lambda _: self.uixml.realui.event_generate("<Enter>"), True)
        self.textbox.bind("<FocusIn>", lambda _: self.uixml.realui.event_generate("<Button-1>"), True)
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
        self.cmds = cmds
        self.textbox.delete('1.0', 'end')
        if base.themename == 'dark':
            self.textbox.config(insertbackground='#ffffff')
        self.textbox.insert('end', '\n'.join(cmds))
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

    def set_shell(self, cmd):
        self.cmd = cmd if cmd == 'cmd' else 'powershell'
        self.contentChanged(None)

    def get(self):
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
