# labels/labelsmng.py
"""
标签管理模块(用txt格式区分任务)

每个工作区`datas.workspace`下管理`labels.txt`文件，格式如下：
{
    "all": ["label1", "label2"],
    "labels": {
        "label1": ["task1", "task2"],
        "label2": ["task3", "task1"]
    },
    "tasks": {
        "task1": ["label1", "label2"],
        "task2": ["label1"],
        "task3": ["label2"]
    }
}
labels.txt中包含两个字典：
- all：标签名称列表，按顺序保存所有标签名
- labels：键为标签名称，值为包含该标签的任务列表
- tasks：键为任务名称，值为包含该任务的标签列表
"""

import json
import os
from typing import Dict, List, TypedDict

import datas


class LabelsData(TypedDict):
    all: List[str]
    labels: Dict[str, List[str]]
    tasks: Dict[str, List[str]]


def __labels_path() -> str:
    return os.path.join(datas.workspace, "labels.txt")


def __empty_labels() -> LabelsData:
    return {"all": [], "labels": {}, "tasks": {}}


def __normalize_string_list(values) -> List[str]:
    if not isinstance(values, list):
        return []
    normalized: List[str] = []
    seen = set()
    for value in values:
        if isinstance(value, str) and value and value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def __normalize_labels_data(labels_data: dict) -> LabelsData:
    if not isinstance(labels_data, dict):
        return __empty_labels()
    labels = labels_data.get("labels")
    tasks = labels_data.get("tasks")
    all_labels = labels_data.get("all")
    normalized_labels: Dict[str, List[str]] = {}
    normalized_tasks: Dict[str, List[str]] = {}
    if isinstance(labels, dict):
        for label, task_list in labels.items():
            normalized_labels[label] = __normalize_string_list(task_list)
    if isinstance(tasks, dict):
        for task, label_list in tasks.items():
            normalized_tasks[task] = __normalize_string_list(label_list)
    normalized_all = __normalize_string_list(all_labels)
    if normalized_all:
        ordered_labels = []
        seen = set()
        for label in normalized_all:
            if label in normalized_labels and label not in seen:
                ordered_labels.append(label)
                seen.add(label)
        for label in normalized_labels:
            if label not in seen:
                ordered_labels.append(label)
                seen.add(label)
        normalized_all = ordered_labels
    else:
        normalized_all = list(normalized_labels.keys())
    return {"all": normalized_all, "labels": normalized_labels, "tasks": normalized_tasks}


def __sync_all_labels() -> None:
    labels = labels_data["labels"]
    all_labels = labels_data["all"]
    synced_all: List[str] = []
    seen = set()
    for label in all_labels:
        if label in labels and label not in seen:
            synced_all.append(label)
            seen.add(label)
    for label in labels:
        if label not in seen:
            synced_all.append(label)
            seen.add(label)
    labels_data["all"] = synced_all


def __task_exists(task: str) -> bool:
    if not task:
        return False
    task_path = os.path.join(datas.workspace, f"{task}.json")
    return os.path.exists(task_path)


def __add_unique(items: List[str], value: str) -> None:
    if value not in items:
        items.append(value)


def __remove_if_exists(items: List[str], value: str) -> None:
    if value in items:
        items.remove(value)


labels_data = __empty_labels()


def load_labels() -> None:
    """
    加载标签数据
    """
    global labels_data
    labels_path = __labels_path()
    if not os.path.exists(labels_path):
        labels_data = __empty_labels()
        save_labels()
        return
    try:
        with open(labels_path, "r", encoding="utf-8") as f:
            labels_data = __normalize_labels_data(json.load(f))
    except:
        labels_data = __empty_labels()


def save_labels() -> bool:
    """
    保存标签数据，返回保存是否成功
    """
    labels_path = __labels_path()
    try:
        __sync_all_labels()
        os.makedirs(datas.workspace, exist_ok=True)
        with open(labels_path, "w", encoding="utf-8") as f:
            json.dump(labels_data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False


def get_labels() -> List[str]:
    """
    获取所有标签列表
    """
    return labels_data["all"].copy()


def add_label(label: str) -> bool:
    """
    添加标签，返回添加是否成功（标签已存在则返回False）
    """
    if not label:
        return False
    labels = labels_data["labels"]
    if label in labels:
        return False
    labels[label] = []
    labels_data["all"].append(label)
    return save_labels()


def delete_label(label: str) -> bool:
    """
    删除标签，返回删除是否成功（标签不存在则返回False）
    """
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    if label not in labels:
        return False
    label_tasks = labels.pop(label)
    __remove_if_exists(labels_data["all"], label)
    for task in label_tasks:
        task_labels = tasks.get(task, [])
        __remove_if_exists(task_labels, label)
        if task_labels:
            tasks[task] = task_labels
        else:
            tasks.pop(task, None)
    return save_labels()


def delete_task(task: str) -> bool:
    """
    删除任务，返回删除是否成功（任务不存在则返回False）
    """
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    if task not in tasks:
        return False
    task_labels = tasks.pop(task)
    for label in task_labels:
        label_tasks = labels.get(label, [])
        __remove_if_exists(label_tasks, task)
        labels[label] = label_tasks
    return save_labels()


def add_task_to_label(label: str, task: str) -> bool:
    """
    将任务添加到标签，返回添加是否成功（标签或任务不存在则返回False）
    """
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    if label not in labels:
        return False
    if not __task_exists(task):
        return False
    if task in labels[label]:
        return False
    label_tasks = labels[label]
    __add_unique(label_tasks, task)
    task_labels = tasks.get(task)
    if task_labels is None:
        task_labels = []
        tasks[task] = task_labels
    __add_unique(task_labels, label)
    return save_labels()


def remove_task_from_label(label: str, task: str) -> bool:
    """
    将任务从标签中移除，返回移除是否成功（标签或任务不存在则返回False）
    """
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    if label not in labels:
        return False
    task_labels = tasks.get(task)
    if task_labels is None:
        return False
    label_tasks = labels[label]
    if task not in label_tasks:
        return False
    __remove_if_exists(label_tasks, task)
    __remove_if_exists(task_labels, label)
    if task_labels:
        tasks[task] = task_labels
    else:
        tasks.pop(task, None)
    return save_labels()


def rename_label(old_label: str, new_label: str) -> bool:
    """
    重命名标签，返回重命名是否成功（旧标签不存在或新标签已存在则返回False）
    """
    if not old_label or not new_label:
        return False
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    all_labels = labels_data["all"]
    if old_label not in labels:
        return False
    if new_label in labels:
        return False
    label_tasks = labels.pop(old_label)
    labels[new_label] = label_tasks
    try:
        all_labels[all_labels.index(old_label)] = new_label
    except ValueError:
        all_labels.append(new_label)
    for task in label_tasks:
        task_labels = tasks.get(task)
        if task_labels is None:
            continue
        if old_label in task_labels:
            __remove_if_exists(task_labels, old_label)
            __add_unique(task_labels, new_label)
            tasks[task] = task_labels
    return save_labels()


def rename_task(old_task: str, new_task: str) -> bool:
    """
    重命名任务，返回重命名是否成功（旧任务不存在或新任务已存在则返回False）
    """
    if not old_task or not new_task:
        return False
    labels = labels_data["labels"]
    tasks = labels_data["tasks"]
    if old_task not in tasks:
        return False
    if new_task in tasks:
        return False
    task_labels = tasks.pop(old_task)
    tasks[new_task] = task_labels
    for label in task_labels:
        label_tasks = labels.get(label)
        if label_tasks is not None and old_task in label_tasks:
            __remove_if_exists(label_tasks, old_task)
            __add_unique(label_tasks, new_task)
            labels[label] = label_tasks
    return save_labels()


def move_task_line(label: str, old_index: int, new_index: int) -> bool:
    """
    调整标签内任务顺序，返回调整是否成功（标签不存在或索引无效则返回False）
    """
    labels = labels_data["labels"]
    if label not in labels:
        return False
    label_tasks = labels[label]
    if old_index < 0 or old_index >= len(label_tasks) or new_index < 0 or new_index >= len(label_tasks):
        return False
    task = label_tasks.pop(old_index)
    label_tasks.insert(new_index, task)
    labels[label] = label_tasks
    return save_labels()


def find_labels_by_task(task: str) -> list:
    """
    查找包含指定任务的标签列表，返回标签列表（任务不存在则返回空列表）
    """
    task_labels = labels_data["tasks"].get(task)
    return task_labels.copy() if task_labels is not None else []


def find_tasks_by_label(label: str) -> list:
    """
    查找包含指定标签的任务列表，返回任务列表（标签不存在则返回空列表）
    """
    label_tasks = labels_data["labels"].get(label)
    return label_tasks.copy() if label_tasks is not None else []
