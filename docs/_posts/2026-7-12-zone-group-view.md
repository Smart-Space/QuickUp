---
layout: post
title: Zone Group View
published: True
---

# 排布窗口预览

在2026-7-12发布的QuickUp 5.0 pre1（仅GitHub代码库发行栏目可获取）中，添加了排布窗口预览功能。该功能与Windows Snap分组贴靠窗口后的窗口组预览功能类似。

该功能作用于**一个**任务下、所有使用**窗口排布功能**的命令条目。QuickUp会创建一个宿主窗口，以QuickUp应用和图标的格式显示在任务栏中，标题为任务名。该宿主窗口会显示所有参与排布的窗口的**初始**位置和尺寸（会有一定变形），以缩略图形式呈现。当鼠标悬停在宿主窗口的任务栏缩略图时，会在大屏显示其下辖所有排布窗口的状态；单击激活时，会将所有下辖窗口调度到前台。这个宿主窗口本身不可见，且在所有下辖窗口关闭后，自动关闭。

以上所说的“一个”任务，是指单次运行的一个任务，同一个任务但是运行两次，是“两个”任务。

至少截止5.0 pre1，排布窗口预览有以下需要注意：

1. 强烈依赖窗口排布功能，如果这使得你的某个应用表现奇怪，请不要使用窗口排布；
2. 5.0 pre1不支持命令启动的QuickUp使用该功能（可能会出问题），后续已经解决；
3. 仅显示参与排布窗口的初始状态，不会更新应用缩略图的位置和尺寸；
4. 5.0 pre1包含4.12部分改进，可当作其预发布版本。高级设置文件中将`zoneGroupView`设为`false`，停用本功能。

---

# Zone Group View

In the QuickUp 5.0 pre1 released on July 12, 2026 (available only in the GitHub code repository section), a layout window preview feature was added. This feature is similar to the window group preview function when Windows Snap groups adjacent windows together. 

This function applies to all command entries that use the **zone group** under a **single task**. QuickUp will create a host window that displays the QuickUp application and icon in the taskbar format, with the task name as the title. This host window will show the **initial** positions and sizes (with some deformation) of all the arranged windows in a thumbnail format. When the mouse hovers over the taskbar thumbnail of the host window, the status of all the arranged windows under it will be displayed on the large screen; when clicked to activate, all the subordinate windows will be scheduled to the front. This host window itself is not visible, and it will automatically close when all the subordinate windows are closed.

The "one" task mentioned above refers to a single run of a task. The same task but run twice constitutes "two" tasks.

As of 5.0 pre1, the layout preview window has the following points to note:

1. Strongly rely on the zone group function. If this causes your application to behave strangely, please do not use it
2. 5.0 pre1 does not support the QuickUp function for command line (it may cause problems), and this issue has been resolved in the subsequent version.
3. Only displays the initial state of the arranged windows, and will not update the position and size of the application thumbnails.
4. 5.0 pre1 includes improvements from 4.12 and can be regarded as its pre-release version. In the advanced settings file, set `zoneGroupView` to `false` to disable this function.
