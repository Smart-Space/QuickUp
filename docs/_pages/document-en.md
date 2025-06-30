---
title: QuickUp Document
layout: post
permalink: /document-en/
---

# Main Window

![](/assets/images/mainwindow.png)

The top bar of main window:

- task-search-entry: enter the name of the task to search for similar tasks. The fuzzy search algorithm in this part is the Longest Common Subsequence Algorithm, implemented by `./cppextend/quickfuzz.h `.
- add-button: click it to show a new-task editor window. Then you can create a new task throw this it.
- setting-button: click it to show setting window of QuickUp.
- about-button: click it to show some information about QuickUp.

The tasks-list-view of main window:

- task item:
  - name of each task.
  - run-button: click to start this task.
  - edit-button: click to open an editor window of this task.
  - delete-button: click to delete this task. **Noted that** any action of deleting a task is not recoverable. So be careful when you decide to remove a task when QuickUp asks you if you want to continue to do it.

> In **sub-workspace main window**, there are not setting-button or about-button. Instead, info-button and shortcut-button will take their places.
>
> - info-button: click to show the whole name of this sub-workspace.
> - shortcut-button: click to create a shortcut on desktop of this sub-workspace.

---

# Editor Window

![](/assets/images/editor.png)

The top bar of editor window:

- task-name-entry.

- button-part

  - save-button: click to save current edition of this task.

    > A new task will be added to the task-list-view after saving and closing this window.

  - run-button: click to start this task. An attempt will be made to save the task. Only when the task is not in a modified state can it be run.

  - path-button: click to set the working path of this task. **Noted that** if a sub-task has NULL working path, it will inherit its sup-task working path. If there is no working path at all, the default working path will be the place of folder of QuickUp.

  - star-button: click to add this task to (or delete it from) `priority.txt` of this workspace. For more information, please see [the priority of task](https://quickup.smart-space.com.cn/priority-of-task/).

  - open-button: click to show where the task `.json` file is.

  - shortcut-button: click to create a shortcut on desktop of this task.

- item-part

  - command

    - target: where the application is.
    - arguments: other contents to use in the command line to start this application.
    - Expansion button：
      - threading-mode: as default, to start this application with a sub-thread. Turn on to wait until this application finishes.
      - administrator-mode: turn on to start this application with administrator rights.
      - Maximum/Minimum.
  
  - command lines
  
    - text-box: the contents of command lines.
    - threading-mode: as default, to start these commands with a sub-thread. Turn on to wait until the commands are completed.
    - radio-box: choose `cmd` or `powershell` to run these command lines.
    
  - sub-task

    - edit-button: open a sub-task in the edit window. At this point, the task name cannot be modified.
    - sub-task-name-entry: type a name of one sub-task.

  - sub-workspace

    - open-button: open this workspace.

    - sub-workspace-name-entry: type a name of one sub-workspace.

      > Unlike other items, when user click this button, QuickUp will ask user to input the name of a sub-workspace. If the name does not exist, QuickUp will ask user whether to create this sub-workspace.
  
  - tip
  
    - text-box: the contents of tips.
    - threading-mode: as default, to show this tip with a sub-thread. Turn on to wait until the window is closed.
    - show-button: click to show this tip in a window, or nothing will happen.
    - top-button: whether to top the tip information window.

> Any action of edit will change the status of editor window into "unsaved". In this status, the window can't be closed until user chooses whether to save it or not.
>
> The following cases will make the saving failed:
>
> 1. The name of task is empty.
> 2. The name of task does not comply with Windows system file naming conventions.
> 3. The name of task has been used.
> 4. The QuickUp file operation failed.

---

# Setting Window

**The setting will influence all workspaces. And, it can just be modified under root workspace of QuickUp.**

To make QuickUp work as you think, please restart all workspaces when you change the configuration.

## General

![](/assets/images/setting-general.png)

### Theme

In QuickUp, you can set the appearance of it within light-mode or dark-mode. The last change will work after restarting QuickUp.

### Searching threshold

Set the threshold for fuzzy search. **Noted that** user should press the Enter key if making the change directly in the input box.

### Maximum number of matching results

Set the maximum number of matching results. 0 is unlimited. Currently, it can be set from 0 to 10. **Noted that** user should press the Enter key if making the change directly in the input box.

### Making QuickUp topmost

It is a function like its name.

### Closing QuickUp to system tray

It is a function like its name.

### Updating

User can check the version of QuickUp by clicking the button, or make QuickUp check new version by itself.

When user turns on QuickUp auto-checking, the new installer will be downloaded automatically. But user can install QuickUp of new version by self whether they turn on auto-checking or not.

## Advanced

![](/assets/images/setting-advanced.png)

### Auto-save when closing editor window

When user turns on this function, editor window will try to save the task when user closes it. **Noted that** it may be failed if one of the cases that stop editor saving a task occurs.

### Forbidding task with administrator rights

It is a function like its name.

### Starting QuickUp upon startup

QuickUp will register the startup application information `<quickup-path> -s` in the registry ` HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run`.

### Setting hot-key to raise QuickUp from system tray

 User can select function keys (at least one) in Control, Alt, Shift and with a character in English as a hot-key, to raise QuickUp from system tray.

> It can only raise the root workspace main window.

### QuickUp command line

User can use following arguments to start QuickUp:

- `-w | --workspace [name]`: open the specific workspace.
- `-t | --task [name]`: open the specific task.
- `-s | --silent`: open QuickUp as silent-mode. (only use when QuickUp can be closed to system tray)

## Storage

![](/assets/images/setting-storage.png)

In this page, user can view the structure of his or her workspaces and tasks.

User can refresh the view list or to open a task or a workspace folder.

## Shortcut

In this page, user can see all shortcut keys that QuickUp supports.

---

# System Tray

QuickUp can be closed to system tray. It can only be stopped by pressing the quit-button of the menu (mouse-right-click to show the menu) or shutdown the computer.

QuickUp (root workspace) can be raised by using the hot-key. Be sure there is not another application using the same hot-key.

---

# Command Line

`quickup [-w|--workspace] [-t|--task] [-s|--silent]`

`-w,--workspace`: open specific workspace. When there is no `-t`, this command just opens a workspace of QuickUp window.

`-t,--task`: run specific task.

`-s,--silent`: close to system stray if it can when QuickUp start.