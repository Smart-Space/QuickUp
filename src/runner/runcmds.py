# ./runner/runcmds.py
"""
指令多条命令
"""
from runner import Task
from cppextend.QUmodule import run_console_commands

class RunCmds(Task):
    def __init__(self, name:str, cmds:list, cmd:str, wait:bool, cwd:str):
        super().__init__(name, 'cmds')
        self.cmds = cmds
        self.cmd = cmd# cmd or powershell
        self.wait = wait
        self.cwd = cwd

    def run(self):
        run_console_commands(self.cmd, self.cmds, self.cwd, self.wait)

def run_cmds(name:str, cmds:list, cmd:str="cmd", wait:bool=True, cwd:str=None):
    task = RunCmds(name, cmds, cmd, wait, cwd)
    task.run()