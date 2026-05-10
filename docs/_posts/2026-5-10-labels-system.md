---
layout: post
title: labels system
published: True
---

# 标签管理系统

QuickUp在4.7版本提供标签管理系统，在标签管理窗口中，可以添加、删除、修改已有标签，且查看特定标签关联的若干任务。

在任务编辑窗口中，可以为一个任务添加若干已有标签。这些标签不存储在任务文件里，而是单独存储在`{workspace}/labels.txt`，以`json`格式保存并由标签管理系统窗口维护，因此虽然两处修改后可能产生名称不同的情况，但标签系统仍应当是稳定正确的。

目前，QuickUp不提供对标签以及标签下任务的顺序保证和顺序修改功能，如有需要，可以自行小心修改。

---

# Labels Management System

In version 4.7 of QuickUp, a labels management system is provided. In the labels management window, you can add, delete, and modify existing tags, and view several tasks associated with a specific tag.

In the task editing window, several existing labels can be added to a task. These labels are not stored in the task file but are separately saved in `{workspace}/labels.txt` in `json` format and maintained by the labels management window. Therefore, although there may be different names after the two modifications, the label system should still be stable and correct.

Currently, QuickUp does not provide any guarantee or modification function for the order of labels and the tasks within the labels. If such functionality is needed, it can be modified manually by the user.