# datas.py
"""
QuickUp的共享数据模块
包含：
- 共享变量
- 共享常量
- 操作共享变量的函数
**获取共享变量直接使用datas._name_of_data_**
**由于QuickUp的主要业务逻辑不涉及多线程，因此本模块不考虑线程安全**
"""
import functools
import os
from tkinter import Tk

from cppextend.QUmodule import quick_fuzz, worker_size

import config

# 版本
version = "5.1"

scale_factor = 1.0# DPI缩放系数
@functools.cache
def mul_scale_factor(num:int) -> float:
    # 乘以缩放系数
    return num * scale_factor

is_msix = False# 是否是MSIX安装包

"""
操作函数：
- tasks_name_initial() 初始化/重新载入
- tasks_name_delete(name:str) -> res:bool 删除某一个值：返回成功与否
- tasks_name_add(name:str) -> res:bool 添加一个值：返回成功与否
- tasks_name_find(name:str) -> res:list 模糊查找：返回符合条件的列表
"""
# 任务名称集合，从./tasks/*.json初始化，始终按文本字典排序
all_tasks_name = []# 总tasks
tasks_name = []# 当前显示的tasks，datas.tasks_name是当前显示的所有任务名称，没有顺序

root_callback = None# 主窗口回调函数
root:Tk = None# 主窗口对象
root_error_message = None# 主窗口错误信息

app_controller = None# 应用控制接口

workspace = None# 工作区对象
workname = None# 工作区名称

titles = []# 标题栏文本与窗口句柄

worker_area = worker_size()# 屏幕可用区域

_priority_cache = []# priority.txt content cache
_priority_cache_mtime = None# last seen mtime of priority.txt
PRIORITY_FILENAME = 'priority.txt'

# ==========以下为操作函数==========

def tasks_name_initial():
    # 初始化tasks_name
    # 从./tasks/*.json获取文件名列表，添加到tasks_name
    # 如果没有./tasks文件夹，则创建
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    __load_tasks_name()

def __load_tasks_name():
    # 按文本字典排序tasks_name
    global tasks_name, all_tasks_name
    tasks_name.clear()
    for f in os.listdir(workspace):
        if f.endswith(".json") and (not f.endswith("[x].json") or config.settings['general']['showHidden']):
            # task-name[x].json可以看作是QuickUp的彩蛋
            # 用户可以自己在文件名中末尾添加[x]来隐藏任务
            tasks_name.append(f[:-5])
    tasks_name = sorted(tasks_name)
    all_tasks_name = tasks_name.copy()

def tasks_name_delete(name:str):
    # 从all_tasks_name和tasks_name中删除name
    # 如果name在tasks_name中，则从tasks_name中删除，并返回True
    # 如果name只在all_tasks_name中，则返回False
    all_tasks_name.remove(name)
    if name in tasks_name:
        tasks_name.remove(name)
        return True
    return False

def tasks_name_add(name:str):
    all_tasks_name.append(name)
    tasks_name.append(name)

def tasks_name_find(name:str, from_list=None):
    # 从tasks_name中模糊查找，返回符合条件的列表
    # 忽略大小写
    global tasks_name
    patternRank = config.settings['general']['patternRank']
    if from_list is None:
        from_list = all_tasks_name
    if name == '':
        tasks_name = from_list.copy()
        return tasks_name
    else:
        name = name.lower()
    max_search_count = config.settings['general']['maxSearchCount']
    if max_search_count == 0:
        max_search_count = len(from_list)
    tasks_name = quick_fuzz(from_list, name, patternRank, max_search_count)
    return tasks_name


# ==========以下为priority.txt相关函数==========

@functools.cache
def priority_path() -> str:
    return os.path.join(workspace, PRIORITY_FILENAME)

def read_priority() -> list:
    # 通过mtime缓存读取priority.txt中的任务名称列表
    # 如果文件不存在，则重置缓存并返回空列表
    global _priority_cache_mtime
    path = priority_path()
    if not os.path.exists(path):
        _priority_cache[:] = []
        _priority_cache_mtime = None
        return _priority_cache
    mtime = os.path.getmtime(path)
    if _priority_cache_mtime != mtime or not _priority_cache:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        _priority_cache[:] = [line.strip() for line in lines if line.strip()]
        _priority_cache_mtime = mtime
    return _priority_cache

def invalidate_priority_cache():
    # 强制下一次read_priority()调用重新从磁盘读取priority.txt
    global _priority_cache_mtime
    _priority_cache_mtime = None

def add_priority(task: str) -> None:
    # 添加一个任务名称到priority.txt末尾
    path = priority_path()
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            pass
    with open(path, 'a', encoding='utf-8') as f:
        f.write(task + '\n')
    invalidate_priority_cache()

def remove_priority(task: str) -> None:
    # 删除一个任务名称
    path = priority_path()
    if not os.path.exists(path):
        return
    with open(path, 'a+', encoding='utf-8') as f:
        f.seek(0)
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip()]
        if task in lines:
            lines.remove(task)
        f.seek(0)
        f.truncate()
        if lines:
            f.write('\n'.join(lines) + '\n')
    invalidate_priority_cache()

def rename_priority(oldname: str, newname: str) -> None:
    # 重命名一个任务名称
    path = priority_path()
    if not os.path.exists(path):
        return
    with open(path, 'a+', encoding='utf-8') as f:
        f.seek(0)
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip()]
        if oldname in lines:
            # 原地替换
            lines[lines.index(oldname)] = newname
        f.seek(0)
        f.truncate()
        if lines:
            f.write('\n'.join(lines) + '\n')
    invalidate_priority_cache()
