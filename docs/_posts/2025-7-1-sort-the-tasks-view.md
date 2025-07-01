---
layout: post
title: Sort the tasks in listview
published: True
---

# 关于任务名的排序

截至本文撰写，QuickUp的任务列表排序在新建任务后，可能会出现搜索栏清空后与再刷新后任务顺序不一致的问题。

QuickUp的搜索栏清空属于搜索事件，只不过展示全部任务，类似于搜索最大匹配数设置为`0`则进行无限制数量匹配。当搜索栏清空后，QuickUp直接显示全部任务，若新建任务后没有进行刷新，QuickUp将以内部全部任务列表顺序显示新建的任务的位置。也就是说，QuickUp不会在新建任务后主动对全部任务列表进行排序。

QuickUp的任务列表刷新与任务列表初始化排序等同。

该情况非程序错误，也不计划有相关修改。

> 不代表没有其它错误，只是当前未发现，且目前正常使用中不会有影响。

---

# Regarding the sorting of task names

As of the time of writing this article, the task list sorting in QuickUp may encounter a problem where the task order is inconsistent after the search bar is cleared and refreshed later, after creating a new task.

The clearing of the search bar in QuickUp is a search event, but it only displays all tasks. It is similar to setting the maximum number of matches to `0` for a search and performing an unlimited number of matches. When the search bar is cleared, QuickUp directly displays all tasks. If a new task is created without refreshing, QuickUp will display the location of the newly created task in the order of the internal list of all tasks. That is to say, QuickUp does not actively sort the entire task list after creating a new task.

The task list refresh in QuickUp is equivalent to the task list initialization and sorting.

This situation is not a error and no related modifications are planned.

> This doesn't mean there are no other errors. It's just that they haven't been discovered yet and there won't be any impact during normal use at present.
