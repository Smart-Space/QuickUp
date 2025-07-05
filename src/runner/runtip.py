# ./runner/runtip.py
"""
提示文本
"""
from tkinter import Toplevel, Label

import config
from runner import Task
from ui.utils import set_window_dark
import datas

def init_tip():
    global theme, themename
    if config.settings['general']['theme'] == 'dark':
        themename = 'dark'
    else:
        themename = 'light'

class TipUI(Toplevel):

    def __init__(self, name:str, tip:str, wait:bool=False, top:bool=False):
        super().__init__(datas.root)
        self.title(f'{name} 提示')
        self.iconbitmap('./logo.ico')
        self.minsize(300, 0)
        self.maxsize(700, 2000)# 我的想法是，写那么多，根本没有意义，别用QuickUp的备注功能
        label = Label(self, text=tip, font=('微软雅黑', 12), justify='left', anchor='w', wraplength=700)
        label.pack(fill='both', expand=True)
        self.update()
        if themename == 'dark':
            label.config(fg='#ffffff', bg='#202020')
            set_window_dark(self)
        else:
            label.config(fg='#000000', bg='#f3f3f3')
        if top:
            self.wm_attributes('-topmost', True)
        self.focus_set()
        if wait:
            self.grab_set()
            self.wait_window(self)

class RunTip(Task):
    def __init__(self, name:str, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
        super().__init__("tip", 'tip')
        self.name = name
        self.tip = tip
        self.wait = wait
        self.show = show
        self.top = top

    def run(self):
        if not self.show:
            return
        TipUI(self.name, self.tip, self.wait, self.top)

def run_tip(name:str, tip:str="", wait:bool=False, show:bool=True, top:bool=False):
    task = RunTip(name, tip, wait, show, top)
    task.run()
