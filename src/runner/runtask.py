# ./runner/runtask.py
"""
执行任务、子任务
"""
import json
import os
datadir = os.path.expanduser("%APPDATA%\\QuickUp\\tasks\\")
from threading import Thread
from tinui.TinUIDialog import Dialog

from runner import Task
from runner.runcmd import run_cmd
from runner.runwcmd import run_wcmd
from runner.runcmds import run_cmds
from runner.runtip import run_tip
import datas
import config
from ui.utils import show_dialog

class RunTask(Task):

    def __init__(self, name:str, cwd:str='', deamon:bool=True):
        super().__init__(name, "task")
        filename = datas.workspace + name + '.json'
        if not os.path.exists(filename):
            if deamon:
                d = Dialog(datas.root, 'error', config.settings['general']['theme'])
                show_dialog(d, "错误", "未在当前任务空间内找到名为 {} 的任务。".format(name), "msg", config.settings['general']['theme'])
            self.tasks = []
            return
        with open(filename, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            if 'cwd' in json_data:
                self.cwd = json_data['cwd'] if json_data['cwd'] else cwd
            else:
                self.cwd = cwd
            self.tasks = json_data['tasks']
        self.deamon = deamon
    
    def __run_wcmd(self, target:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False):
        run_wcmd(self.name, target, args, admin, cwd, maximize, minimize)
        self.run()
    
    def __run_cmds(self, name:str, cmds:list, cmd:str, wait:bool, cwd:str=''):
        run_cmds(name, cmds, cmd, wait, cwd)
        self.run()
    
    def run(self):
        while self.tasks:
            task = self.tasks.pop(0)
            if task['type'] == 'cmd':
                run_cmd(self.name, task['target'], task['args'], task['admin'], self.cwd, task.get('max', False), task.get('min', False))
            elif task['type'] == 'wcmd':
                t = Thread(target=self.__run_wcmd, args=(task['target'], task['args'], task['admin'], self.cwd, task.get('max', False), task.get('min', False)), name=task['target'])
                t.daemon = self.deamon
                t.start()
                break
            elif task['type'] == 'cmds':
                t = Thread(target=self.__run_cmds, args=(self.name, task['cmds'], task['cmd'], task['wait'], self.cwd), name=task['cmd'])
                t.daemon = self.deamon
                t.start()
                break
            elif task['type'] == 'task':
                RunTask(task['task'], self.cwd, self.deamon).run()
            elif task['type'] == 'wsp':
                if task['name'] == '' or os.path.exists(datas.workspace + task['name']) == False:
                    if datas.root:
                        d = Dialog(datas.root, 'error', config.settings['general']['theme'])
                        show_dialog(d, "错误", "未在当前任务空间内找到名为 {} 的工作区。".format(task['name']), "msg", config.settings['general']['theme'])
                    continue
                if datas.workname == '.':
                    workspace = task['name']
                else:
                    workspace = datas.workname + '/' + task['name']
                run_cmd(self.name+'_wsp', "QuickUp.exe", f'-w "{workspace}"', False)
            elif task['type'] == 'tip':
                run_tip(self.name, task['tip'], task['wait'], task['show'], task['top'])

def run_task(name:str, deamon:bool=True):
    task = RunTask(name, deamon=deamon)
    task.run()
