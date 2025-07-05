# ./runner/runwcmd.py
"""
执行单线命令
"""
import subprocess
import ctypes
from ctypes import wintypes

from runner import Task


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
        if not admin:
            self.cmd = "start \"\" /wait "
            if self.maximize:
                self.cmd += "/max "
            if self.minimize:
                self.cmd += "/min "
            self.cmd += "\"" + cmd + "\" " + args
        else:
            pass
    
    def run(self):
        if not self.admin:
            p = subprocess.Popen(self.cmd, shell=True, cwd=self.cwd if self.cwd else None)
            p.wait()
        else:
            sei = SHELLEXECUTEINFO()
            sei.cbSize = ctypes.sizeof(SHELLEXECUTEINFO)
            sei.fMask = 0x00000040  # SEE_MASK_NOCLOSEPROCESS
            sei.hwnd = None
            sei.lpVerb = "runas"
            sei.lpFile = self.cmd
            sei.lpParameters = self.args
            sei.lpDirectory = self.cwd if self.cwd else None
            if self.maximize:
                sei.nShow = 3  # SW_MAXIMIZE
            elif self.minimize:
                sei.nShow = 2  # SW_SHOWMINIMIZED
            else:
                sei.nShow = 1  # SW_SHOWNORMAL
            if ShellExecuteEx(ctypes.byref(sei)):
                p = sei.hProcess
                ctypes.windll.kernel32.WaitForSingleObject(p, -1)
                ctypes.windll.kernel32.CloseHandle(p)
            else:
                # without UAC
                pass


def run_wcmd(name:str, cmd:str, args:str, admin:bool=False, cwd:str='None', maximize:bool=False, minimize:bool=False):
    task = RunWCmd(name, cmd, args, admin, cwd, maximize, minimize)
    task.run()
