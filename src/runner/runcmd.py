# ./runner/runcmd.py
"""
执行命令行命令
"""
from runner import Task
import config
import datas
from cppextend.QUmodule import shell_execute_wrapper

class RunCmd(Task):
    def __init__(self, name:str, cmd:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False):
        super().__init__(name, 'cmd')
        self.admin = admin
        self.cwd = cwd
        if cmd.startswith('"') and cmd.endswith('"'):
            # 去除引号
            cmd = cmd[1:-1]
        # 对于非系统或PATH环境变量软件，建议使用路径全称避免文档、卷、路径名错误
        # 毕竟都写成快捷启动方式了，在创建任务的时候耐心点没什么问题吧
        self.cmd = cmd
        self.args = args
        self.maximize = maximize
        self.minimize = minimize

    def run(self):
        if not self.admin or config.settings['advanced']['disAdmin']:
            # 非管理员权限，直接运行
            operation = "open"
        else:
            # 管理员权限
            operation = "runas"
        res = shell_execute_wrapper(self.cmd, self.args, self.cwd, self.maximize, self.minimize, operation)
        if res:
            # 出错
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"目标: {self.cmd}\n\n"\
            f"参数: {self.args}\n\n"\
            f"错误: {res.strip()}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')

def run_cmd(name:str, cmd:str, args:str, admin:bool, cwd:str='', maximize:bool=False, minimize:bool=False):
    task = RunCmd(name, cmd, args, admin, cwd, maximize, minimize)
    task.run()
