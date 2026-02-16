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

    def __init__(self, name:str, cwd:str='', deamon:bool=True, callback=None):
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
        # callback为完成一个任务条目的回调函数
        # def callback(state:str, val=...)
        # state为任务状态，包括：running、success、error、set
        self.callback = callback
        self.callback_count = 0
        self.__call_back("set", len(self.tasks))
    
    def __call_back(self, state:str, val=1):
        if self.callback:
            self.callback(state, val)
    
    def __run_wcmd(self, target:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False, pos:list=[], zone_round:bool=False):
        res = run_wcmd(self.name, target, args, admin, cwd, maximize, minimize, pos, zone_round)
        if res:
            self.__call_back("success", self.callback_count)
        else:
            self.__call_back("error", self.callback_count)
        self.run()
    
    def __run_cmds(self, name:str, cmds:list, cmd:str, wait:bool, cwd:str=''):
        run_cmds(name, cmds, cmd, wait, cwd)
        self.run()
    
    def run(self):
        while self.tasks:
            task = self.tasks.pop(0)
            self.__call_back("running", self.callback_count+1)
            self.callback_count += 1
            if task['type'] == 'cmd':
                res = run_cmd(self.name, task['target'], task['args'], task['admin'], self.cwd, task.get('max', False), task.get('min', False), task.get('pos', []), task.get('zone_round', False))
                if  res:
                    self.__call_back("success", self.callback_count)
                else:
                    self.__call_back("error", self.callback_count)
            elif task['type'] == 'wcmd':
                t = Thread(target=self.__run_wcmd, name=task['target'], args=(task['target'], task['args'], task['admin'], self.cwd, task.get('max', False), task.get('min', False), task.get('pos', []), task.get('zone_round', False)))
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
                    self.__call_back("error", self.callback_count)
                    continue
                if datas.workname == '.':
                    workspace = task['name']
                else:
                    workspace = datas.workname + '/' + task['name']
                run_cmd(self.name+'_wsp', "QuickUp.exe", f'-w "{workspace}"', False)
                self.__call_back(False, "success", self.callback_count)
            elif task['type'] == 'tip':
                run_tip(self.name, task['tip'], task['wait'], task['show'], task['top'])

def run_task(name:str, deamon:bool=True, callback=None):
    task = RunTask(name, deamon=deamon, callback=callback)
    task.run()
