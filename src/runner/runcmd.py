# ./runner/runcmd.py
"""
执行命令行命令
"""
import os

from runner import Task
import config
import datas
from cppextend.QUmodule import shell_execute_ex_wrapper

class RunCmd(Task):
    def __init__(self, name:str, cmd:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False, pos:list=[], zone_round:bool=False):
        super().__init__(name, 'cmd')
        self.admin = admin
        # 对于非系统或PATH环境变量软件，建议使用路径全称避免文档、卷、路径名错误
        # 毕竟都写成快捷启动方式了，在创建任务的时候耐心点没什么问题吧😏
        self.cmd = cmd.strip('"')
        if cwd == '':
            if os.path.isfile(self.cmd):
                self.cwd = os.path.dirname(self.cmd)
            else:
                self.cwd = ''
        else:
            self.cwd = cwd
        self.args = args
        self.maximize = maximize
        self.minimize = minimize
        self.pos = pos
        self.zone_round = zone_round

    def run(self):
        if not self.admin or config.settings['advanced']['disAdmin']:
            # 非管理员权限，直接运行
            admin = 0
        else:
            # 管理员权限
            admin = 1
        res = shell_execute_ex_wrapper(self.cmd, self.args, self.cwd, self.maximize, self.minimize, admin, 0, self.pos, self.zone_round)
        if res:
            # 出错
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"目标: {self.cmd}\n\n"\
            f"参数: {self.args}\n\n"\
            f"错误: {res.strip()}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')
            return False
        return True

def run_cmd(name:str, cmd:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False, pos:list=[], zone_round:bool=False):
    task = RunCmd(name, cmd, args, admin, cwd, maximize, minimize, pos, zone_round)
    return task.run()
