# ./runner/__init__.py
"""
QuickUp Task Runner Model
此文件中定义了任务数据类型基类
"""
CmdType = "cmd"# 命令类型
TaskType = "task"# 子任务类型
WcmdType = "wcmd"# 等待命令类型
CmdsType = "cmds"# 多个命令类型
WorkspaceType = "wsp"# 工作区类型
TipType = "tip"# 提示类型


class Task:

    def __init__(self, name:str, task_type:str):
        self.name = name
        self.type = task_type
