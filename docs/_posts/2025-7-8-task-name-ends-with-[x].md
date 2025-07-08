---
layout: post
title: Task Name Ends With [x]
published: True
---
# 以"[x]"结尾的任务名

当一个任务名以"[x]"结尾时，例如`task-name[x]`（对应`task-name[x].json`），它将不会被列入QuickUp的任务列表，但是它仍然是一个QuickUp的任务，只不过在任务列表中隐藏了。

你仍可以通过以下方法运行它：

- 其它任务调用`task-name[x]`
- 使用`quickup -t "task-name[x]"`
- 快捷方式中使用上方命令行指令

> QuickUp的任务列表只在启动时扫描任务工作区目录，此后所有操作均应当在QuickUp中进行，包括将`task-name`改名为`task-name[x]`。你可以通过QuickUp的`设置-存储-刷新`查看实际工作目录中的变化。

隐藏任务是一个很好的功能，但QuickUp不计划在应用中支持任务的隐藏与显示的切换，重命名只是让这个任务在下次启动之后开始隐藏，而非立刻隐藏。用户需要手动将一个隐藏任务改为QuickUp任务列表中会显示的任务名。

这是**彩蛋**。

---

# Task names ending with "[x]"

When a task name ends with "[x]", for example, `task-name[x]` (corresponding to `task-name [x].json`), it will not be included in the QuickUp task list view, but it is still a QuickUp task, only hidden in the task list view.

You can still run it through the following methods:

- Other tasks call `task-name[x]`
- Use `quickup -t "task-name[x]"`
- Use the command-line instruction above in the shortcut

> The task list of QuickUp only scans the task workspace directory at startup. All subsequent operations should be carried out in QuickUp, including renaming `task-name` to `task-name [x]`. You can view the changes in the actual working directory through QuickUp's `Settings - Store - Refresh`.

Hiding tasks is a great feature, but QuickUp does not plan to support the switching between hiding and showing tasks in the application. Renaming only makes the task start to hide after the next startup, rather than immediately hiding it. Users need to manually change a hidden task to the task name that will be displayed in the QuickUp task list.

This is an **Easter egg**.