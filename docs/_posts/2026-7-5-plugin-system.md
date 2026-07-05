---
layout: post
title: Plugin System
published: True
---

# QuickUp插件系统

自QuickUp-4.11起，提供基于Python（随本应用发行或开发版本）的基本插件系统。相比于通过执行命令来启动个人脚本，插件系统的意义在于：

- 方便管理个人脚本；
- 变量和过程持久化；
- 调用本应用接口（持续优化）。

但是也会受到以下限制：

- 不能过于复杂；
- 有导入和内建变量、函数使用限制；
- 无命令行调试（开发版除外）。

QuickUp执行插件功能，与插件名称无关，因此注意不要冲突；参数为Python风格，支持位置参数、关键字参数。

既然都用python写插件了，那么QuickUp的`/plugin/**`下的大体实现也很容易看懂，且在`/plugin/__init__.py`和`/plugin/README.md`中有说明。主要注意QuickUp中对插件脚本的限制问题。

---

# QuickUp Plugin System 
Starting from QuickUp-4.11, a basic plugin system based on Python (either included with this application or in the development version) is provided. Compared to launching individual scripts by executing commands, the significance of the plugin system lies in:

- Facilitates the management of individual scripts;
- Persistence of variables and processes;
- Calls the interface of this application (continuously optimized). 

However, there will also be the following limitations: 

- It should not be overly complicated;
- There are restrictions on the import and usage of built-in variables and functions;
- There is no command-line debugging (except in the development version). 

The QuickUp plugin performs the functionality. The name of the plugin is not relevant to this. Therefore, be careful not to cause any conflicts. The parameters are in Python style and support positional parameters as well as keyword parameters.