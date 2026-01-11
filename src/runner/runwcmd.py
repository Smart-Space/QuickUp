# ./runner/runwcmd.py
"""
执行单线命令
"""
from runner import Task
import datas
from cppextend.QUmodule import shell_execute_ex_wrapper


class RunWCmd(Task):
    def __init__(self, name:str, cmd:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False):
        super().__init__(name, 'wcmd')
        self.cwd = cwd
        if cmd.startswith('"') and cmd.endswith('"'):
            self.cmd = cmd[1:-1]
        self.cmd = cmd
        self.args = args
        self.admin = admin
        self.maximize = maximize
        self.minimize = minimize
    
    def run(self):
        res = shell_execute_ex_wrapper(self.cmd, self.args, self.cwd, self.maximize, self.minimize, self.admin, self.name)
        if res:
            # 出错
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"目标: {self.cmd}\n\n"\
            f"参数: {self.args}\n\n"\
            f"错误: {res.strip()}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')


def run_wcmd(name:str, cmd:str, args:str, admin:bool=False, cwd:str='None', maximize:bool=False, minimize:bool=False):
    task = RunWCmd(name, cmd, args, admin, cwd, maximize, minimize)
    task.run()
