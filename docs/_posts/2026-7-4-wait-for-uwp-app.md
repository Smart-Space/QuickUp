---
layout: post
title: Wait for UWP Apps
published: True
---

# UWP应用的单线等待

在此之前，由于UWP（以及使用这个框架的）应用本身具有统一启动进程，这个进程在启动后会结束，无论应用本身是否结束，导致在任务里无法进行单线等待。在QuickUp-4.10（开发版，未公开）中，对所有应用都会使用`\cppextend\zone.h`下的`find_target_window`方法，获取：

1. win32应用，获取进程对应窗口；
2. UWP（之类）框架应用，获取进程、对应启动窗口、窗口进程。

如果开启单线等待使得应用窗口行为奇怪，请不要使用该功能。

我不可能测试所有应用，如果遇到单线问题且希望解决，请自行下载本应用源码调试分析，单独的问题报告是没有意义的，我不会去专门测试。欢迎提供分析解答。

---

# Waiting for UWP Applications
Prior to this, since UWP (and applications using this framework) have a unified startup process, this process would terminate after startup, regardless of whether the application itself ended or not, resulting in the inability to perform single-threaded waiting in the task. In QuickUp-4.10 (development version, not publicly available), the `find_target_window` method under `\cppextend\zone.h` will be used for all applications to obtain: 

1. Win32 application, obtain the corresponding window of the process;
2. UWP (and similar) framework application, obtain the process, the corresponding startup window, and the window process. 

If enabling single-line waiting causes the application window to behave abnormally, please do not use this feature.