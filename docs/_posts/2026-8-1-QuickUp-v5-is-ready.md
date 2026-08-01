---
layout: post
title: QuickUp v5 is Ready
published: True
---

# QuickUp v5 发布

2026-8-1，QuickUp ==5.1== 发布，包含==4.12==、==5.0 pre1==、==5.0 improved==的新功能与改进，以及新小版本的若干新优化与功能改进。

最重要的功能更新是正式支持窗口排布应用组的预览，使用者可直接在任务栏中找到单个任务排布组的预览图，鼠标悬停可展示预览大图，点击唤醒会调度所有窗口到前台，方便多应用窗口时的任务应用组切换。

其它重要功能更新：

- 通过`|label...|name...`在标签下搜索任务，标签采用关键字搜索，任务名采用模糊搜索；
- 插件功能提供新的API接口，可实现直接运行任务，或者构建临时任务结构直接运行；
- 命令集任务条目会单独创建一个命令行窗口执行，不再使用单一进程命令行或附带命令行，指令间通过管道通信，不包括在并行操作里；
- 任务编辑器中手动添加后会选中新任务条目，单行输入框滚动会带动整个任务条目列表；
- 热键可设置为空，不监听。

重要优化与修复：

- 修复命令行执行任务时无法窗口排布的问题；
- 修复等待命令(wcmd)的无法复制粘贴问题；
- [5.0 pre1] UWP框架应用的等待改为窗口关闭，且优化操作性能；
- [5.0 improved] 修复排布窗口预览右侧、下侧缩略图尺寸偏小的问题。

关于源码问题，前文提过，本文捋一遍。QuickUp一开始就不是“开源软件”，3.0版本开始公开源码；4.5版本因为时间上没空，暂停源码公开更新；4.6版本为了实现窗口组预览单开了一个分支；4.9版本继续恢复main分支代码公开更新；5.0版本起，pro(本来是pre的，一开始打错字了)分支彻底和main分支独立，依然不定期公开更新main分支源码，pro分支不会公开。

可以预见地，QuickUp在功能上这次真的已经足够完善，我自己用起来非常顺手，除了修复错误和维护，开发QuickUp的动力下降，另外我也不靠QuickUp吃饭，这是我的工具而已，后续main分支源码一定会断更，即使我会发布维护版本。

下次有动力进行功能更新，说不定等我用上多显示器的时候。

---

# QuickUp v5 Released

On August 1, 2026, QuickUp version 5.1 was released, featuring new functions and improvements such as ==4.12==, ==5.0 pre1==, and ==5.0 improved==, as well as several new optimizations and functional enhancements in the new minor version.

The most significant functional update is the official support for previewing of application zone groups. Users can directly find the preview image of a single task arrangement group in the taskbar. When the mouse hovers over it, a larger preview image will be displayed. Clicking on it will activate and schedule all windows to the front, facilitating the switching of application groups for multiple windows.

Other important function updates: 
- Through `|label...|name...` Search for tasks under the label. The label uses keyword search, while the task name uses fuzzy search.
- The plugin function provides new API interfaces, enabling direct execution of tasks or building a temporary task structure for direct execution.
- The **commands task** will be executed in a separate command line window, no longer using the process command line or an attached command line. Instructions communicate through pipes and are not included in parallel operations.
- In the task editor, when manually adding a new task entry, the selected task entry will be highlighted, and the scrolling of the single-line input box will affect the entire task entry list view. 、
- Hot key can be set to nothing.

Important optimizations and fixes: 
- Fixed the issue where the command line execution tasks couldn't arrange windows properly;
- Fixed the problem where waiting for commands (wcmd) couldn't be copied and pasted;
- [5.0 pre1] Changed the waiting mechanism for UWP framework applications to window closure, and optimized the operational performance;
- [5.0 improved] Fixed the issue where the thumbnail sizes on the right and bottom sides of the window preview were too small. 

Regarding the source code issue, as mentioned earlier, I will go through it again in this article. QuickUp was not an "open-source software" from the very beginning. The source code became public with version 3.0; due to time constraints, the source code public update was suspended in version 4.5; a separate branch was opened for window zone group preview in version 4.6; the main branch code update resumed in version 4.9; starting from version 5.0, the pro (originally pre, a typo occurred initially) branch became completely independent from the main branch, and the main branch source code was still updated irregularly.

