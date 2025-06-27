# ./runner/create_lnk.py
"""
创建工作区、任务链接
"""
from tinui.TinUIDialog import Dialog

import config
import datas
from ui import utils


def create_workspace_lnk(root, workspace):
    theme = config.settings['general']['theme']
    d = Dialog(root, "question", theme)
    res = utils.show_dialog(d, "创建工作区快捷方式", f"是否在桌面创建工作区 {workspace} 的快捷方式？", "msg", theme)
    if res:
        root.config(cursor="wait")
        root.update_idletasks()
        utils.create_workspace_lnk(workspace)
        root.config(cursor="")
        root.update_idletasks()
        d = Dialog(root, "info", theme)
        utils.show_dialog(d, "创建工作区快捷方式", f"工作区 {workspace} 的快捷方式已创建。", "msg", theme)

def create_task_lnk(root, task):
    theme = config.settings['general']['theme']
    d = Dialog(root, "question", theme)
    res = utils.show_dialog(d, "创建任务快捷方式", f"是否在桌面创建任务 {task} 的快捷方式？", "msg", theme)
    if res:
        root.config(cursor="wait")
        root.update_idletasks()
        workspace = datas.workspace
        utils.create_task_lnk(workspace, task)
        root.config(cursor="")
        root.update_idletasks()
        d = Dialog(root, "info", theme)
        utils.show_dialog(d, "创建任务快捷方式", f"任务 {task} 的快捷方式已创建。", "msg", theme)
