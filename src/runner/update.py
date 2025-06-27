# ./runner/update.py
"""
执行更新操作
"""
from urllib.request import urlopen, Request
import os
import subprocess
from threading import Thread

import datas

# 下载文件夹
installerexe = os.path.join(os.path.expanduser("~"), "Downloads", "QuickUpInstaller.exe")

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
headers = {"User-Agent": user_agent}
def __auto_check_update(settingwindow):
    # 检查更新
    url = "https://quickup.smart-space.com.cn/ver.txt"
    try:
        req = Request(url, headers=headers)
        with urlopen(req) as f:
            new_version = f.read().decode().strip()
        now1, now2 = datas.version.split(".")
        new1, new2 = new_version.split(".")
        if int(new1) > int(now1) or (int(new1) == int(now1) and int(new2) > int(now2)):
            settingwindow.event_generate("<<UpdateAvailable>>")
        else:
            pass
    except:
        pass

def auto_check_update(settingwindow):
    # 自动检查更新
    t = Thread(target=__auto_check_update, args=(settingwindow,), name="AutoCheckUpdate")
    t.daemon = True
    t.start()

def __update_program(settingwindow):
    # 更新程序
    try:
        req = Request("https://quickup.smart-space.com.cn/download.txt", headers=headers)
        with urlopen(req) as target:
            url = target.read().decode().strip()
        req = Request(url, headers=headers)
        with urlopen(req) as f:
            with open(installerexe, "wb") as code:
                code.write(f.read())
        settingwindow.event_generate("<<UpdateReady>>")
    except:
        settingwindow.event_generate("<<UpdateFailed>>")

def update_program(settingwindow):
    # 手动更新程序
    if os.path.exists(installerexe):
        settingwindow.event_generate("<<UpdateReady>>")
    else:
        t = Thread(target=__update_program, args=(settingwindow,), name="UpdateProgram")
        t.daemon = True
        t.start()

def update_QuickUp():
    # 更新QuickUp
    cmd = f'explorer /select,"{installerexe}"'
    subprocess.Popen(cmd, shell=True)
    datas.root_callback()
