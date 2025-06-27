# ./runner/runcmd.py
"""
执行命令行命令
"""
import subprocess
import ctypes

from runner import Task
import config

class RunCmd(Task):
    def __init__(self, name:str, cmd:str, args:str, admin:bool, cwd:str=''):
        super().__init__(name, 'cmd')
        self.admin = admin
        self.cwd = cwd if cwd != '' else None
        if cmd.startswith('"') and cmd.endswith('"'):
            # 去除引号
            cmd = cmd[1:-1]
        # 对于非系统或PATH环境变量软件，建议使用路径全称避免文档、卷、路径名错误
        # 毕竟都写成快捷启动方式了，在创建任务的时候耐心点没什么问题吧
        self.cmd = cmd
        self.args = args
        if not admin:
            # start "" "{cmd}" {args}
            self.cmd = "start \"\" \"" + cmd + "\" " + args
        else:
            # 管理员权限
            # runas, {cmd}, {args}
            pass

    def run(self):
        if not self.admin or config.settings['advanced']['disAdmin']:
            # 非管理员权限，直接运行
            subprocess.Popen(self.cmd, shell=True, cwd=self.cwd if self.cwd else None)
        else:
            # 管理员权限，使用ctypes.windll.shell32.ShellExecuteW()
            hwnd = None
            operation = "runas"
            file = self.cmd
            params = self.args
            directory = self.cwd if self.cwd else None
            show_cmd = 1
            try:
                ctypes.windll.shell32.ShellExecuteW(hwnd, operation, file, params, directory, show_cmd)
            except:
                pass

def run_cmd(name:str, cmd:str, args:str, admin:bool, cwd:str=''):
    task = RunCmd(name, cmd, args, admin, cwd)
    task.run()
