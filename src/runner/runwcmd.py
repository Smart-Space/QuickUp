# ./runner/runwcmd.py
"""
执行单线命令
"""
import ctypes
from ctypes import wintypes

from runner import Task
import datas


# 定义 ShellExecuteEx 函数原型
# 定义 SHELLEXECUTEINFO 结构体
class SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", wintypes.ULONG),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", wintypes.INT),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", wintypes.LPVOID),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIcon", wintypes.HICON),
        ("hProcess", wintypes.HANDLE),
    ]

ShellExecuteEx = ctypes.windll.shell32.ShellExecuteExW
ShellExecuteEx.argtypes = [ctypes.POINTER(SHELLEXECUTEINFO)]
ShellExecuteEx.restype = wintypes.BOOL


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
        sei = SHELLEXECUTEINFO()
        if not self.admin:
            sei.lpVerb = "open"
        else:
            sei.lpVerb = "runas"
        sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
        sei.fMask = 0x00000040  # SEE_MASK_NOCLOSEPROCESS
        sei.hwnd = None
        sei.lpFile = self.cmd
        sei.lpParameters = self.args
        sei.lpDirectory = self.cwd if self.cwd else None
        if self.maximize:
            sei.nShow = 3  # SW_MAXIMIZE
        elif self.minimize:
            sei.nShow = 2  # SW_SHOWMINIMIZED
        else:
            sei.nShow = 5  # SW_SHOW
        if ShellExecuteEx(ctypes.byref(sei)):
            p = sei.hProcess
            ctypes.windll.kernel32.WaitForSingleObject(p, -1)
            ctypes.windll.kernel32.CloseHandle(p)
        else:
            # 出错
            error_msg = ctypes.FormatError()
            datas.root_error_message = f"任务: {self.name}\n\n"\
            f"目标: {self.cmd}\n\n"\
            f"参数: {self.args}\n\n"\
            f"错误: {error_msg}"
            if datas.root:
                datas.root.event_generate('<<RunCmdError>>')
            # else:
            #     print(datas.root_error_message)


def run_wcmd(name:str, cmd:str, args:str, admin:bool=False, cwd:str='None', maximize:bool=False, minimize:bool=False):
    task = RunWCmd(name, cmd, args, admin, cwd, maximize, minimize)
    task.run()
