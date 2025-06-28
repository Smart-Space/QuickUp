---
layout: post
title: About QuickUp's workspace
published: True
---
# QuickUp的工作区组

工作区组类似于文件夹，实际上，QuickUp的任务系统就是单纯的文件夹结构，所有任务都放置在安装目录的`./tasks/`文件夹下，该文件夹是QuickUp的工作区空间，也是QuickUp的根工作区组。当直接运行QuickUp，或者使用`quickup -w .`时，启动的就是根工作区，QuickUp会读取根工作区组下的所有任务配置文件，并且将文件夹视作根工作区组的子工作区组。

同样的，当QuickUp打开任何一个工作区组，都会读取该目录下的所有任务配置文件，并且将里面的文件夹视作该工作区组的子工作区组。

> QuickUp的热键唤醒只对根工作区的QuickUp窗口有效。

创建的子工作区组有两种方法：

1. 在编辑窗口中点击“工作区组”按钮，在其中输入新的工作区组名称，并允许QuickUp创建新工作区组。
2. 在你希望的位置（当然是`./tasks/`下的某个位置）创建一个文件夹。

打开工作区组也有两种方法：

1. 在编辑窗口的工作区组栏目点击右上角的“打开”按钮。
2. 命令行中使用`quickup -w "<workspace-name>"`。

---

# QuickUp's Workspace

The workspace group is similar to a folder. In fact, the task system of QuickUp is a simple folder structure. All tasks are placed under the `./tasks/` folder in the installation directory. This folder is the workspace space of QuickUp and also the root workspace group of QuickUp. When running QuickUp directly or using `quickup -w.`, the root workspace is started. QuickUp reads all the task configuration files under the root workspace group and regards sub-folders as sub-workspace groups of the root workspace group.

Similarly, when QuickUp opens any workspace group, it will read all the task configuration files under that directory and regard the folders inside as sub-workspace groups of that workspace group.

> The hotkey wake-up of QuickUp is only effective for the QuickUp window of the root workspace.

There are two methods for creating a sub-workspace group:

1. In the editing window, click the "Workspace Group" button, enter the new workspace group name in it, and allow QuickUp to create a new workspace group.
2. Create a folder at the location you want (of course, somewhere under `./tasks/`).

There are also two ways to open the workspace group:

1. Click the "Open" button in the upper right corner of a Workspace Group column in the editing window.
2. Use `quickup -w "<workspace-name>"` in the command line.