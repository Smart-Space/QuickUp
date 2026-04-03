---
layout: post
title: zone record
published: True
---

# QuickUp窗口排布记录

QuickUp v4.5起，编辑界面可以直接记录当前正在使用的应用窗口及其位置和尺寸。

点击添加栏的“记录”图标，将会弹出一个问询对话框，在按下“YES”之前，可以调整当前所有正在使用的应用的窗口；按下“YES”之后，QuickUp会**尝试**记录以下信息：

- 所有应用主窗口的进程文件（可执行文件或UWP应用）
- 最小化的窗口
- 最大化的窗口
- 所有应用主窗口的位置和尺寸

以上信息将作为“命令”插入任务列表中，以供后续调整和编辑。

注意，无论是最大/最小化、位置尺寸指定、圆角保留等，都是QuickUp**尝试**告知应用，如果应用窗口行为奇怪，请取消使用QuickUp窗口排布。

---

# QuickUp window layout record

Starting from QuickUp v4.5, the editing interface can directly record the application window currently in use, its location and size.

Click the "Record" icon in the add column to pop up an asking dialog. Before pressing "YES", you can adjust the windows of all currently in use applications; after pressing "YES", QuickUp will **try to** record the following information:

- Process files (executables or UWP applications) for all application main windows
- minimized windows
- Maximized windows
- Location and size of the main window for all applications

The above information will be inserted into the task list as a "command" for subsequent adjustment and editing.

Note that whether it is maximizing/minimizing, specifying location size, retaining rounded corners, etc., QuickUp is **trying to** tell the application. If the application window behaves strangely, please cancel using QuickUp window zone.