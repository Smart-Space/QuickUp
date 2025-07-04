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
import os
import re

from cppextend.QUmodule import quick_fuzz

import config

# 版本
version = "3.2"

"""
操作函数：
- tasks_name_initial() 初始化/重新载入
- tasks_name_delete(name:str) -> res:bool 删除某一个值：返回成功与否
- tasks_name_add(name:str) -> res:bool 添加一个值：返回成功与否
- tasks_namn_find(name:str) -> res:list 模糊查找：返回符合条件的列表
- is_valid_windows_filename(filename:str) -> res:bool 检查文件名是否合法：返回合法与否
"""
# 任务名称集合，从./tasks/*.json初始化，始终按文本字典排序
all_tasks_name = []# 总tasks
tasks_name = []# 当前显示的tasks，datas.tasks_name是当前显示的所有任务名称，没有顺序

root_callback = None# 主窗口回调函数
root = None# 主窗口对象

workspace = None# 工作区对象


# ==========以下为操作函数==========

def tasks_name_initial():
    # 从./tasks/*.json获取文件名列表，添加到tasks_name
    # 按文本字典排序tasks_name
    # 如果没有./tasks文件夹，则创建
    global tasks_name, all_tasks_name
    if not os.path.exists(workspace):
        os.mkdir(workspace)
    for f in os.listdir(workspace):
        if f.endswith(".json"):
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

def tasks_namn_find(name:str):
    # 从tasks_name中模糊查找，返回符合条件的列表
    # 忽略大小写
    global tasks_name
    patternRank = config.settings['general']['patternRank']
    tasks_name.clear()
    if name == '':
        tasks_name = all_tasks_name.copy()
        return tasks_name
    else:
        name = name.lower()
    search_count = 0
    max_search_count = config.settings['general']['maxSearchCount']
    if max_search_count == 0:
        max_search_count = len(all_tasks_name)
    for n in all_tasks_name:
        if quick_fuzz(name, n.lower()) >= patternRank:
            tasks_name.append(n)
            search_count += 1
            if search_count >= max_search_count:
                break
    return tasks_name

invalid_chars = re.compile(r'[<>:"/\\|?*]')
def is_valid_windows_filename(filename):
    # 检查文件名是否包含非法字符
    if invalid_chars.search(filename):
        return False
    # 检查文件名是否以空格或点结束
    if filename.endswith(' ') or filename.endswith('.'):
        return False
    # 检查文件名是否为保留字
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    # 将文件名转换为大写进行比较
    uppercase_filename = filename.upper()
    if any(uppercase_filename == reserved_name for reserved_name in reserved_names):
        return False
    # 如果所有检查都通过，则返回True
    return True
