---
layout: post
title: suspend open source
published: True
---

# 暂停开源

自QuickUp v4.5起，QuickUp项目暂停开源，已开源代码将永久保留开放，仅后续新代码不再跟进。这个决定有如下几个原因：

第一，截止到v4.3，QuickUp已经足够完善，v4.5仅添加了高DPI支持、窗口稳定还原、应用组记录等功能，算是锦上添花，并非必用功能。另外，作为一个个人项目，QuickUp已经完全能够满足我的使用需求，而我自认为我对于应用组便捷管理与启动的使用需求不低。暂停开源不等于暂停更新、更不等于停止更新（不过我觉得没什么新功能会更新了），但是新的维护代码并不会使得QuickUp整体架构发生巨变，没有必要再跟进新代码。

第二，我的本地开发代码库和开源代码仓库是两个东西，代码同步是手动的。当然，我有能力实现流水自动化，但我就是不想，没必要。这个是主要原因，加上第一点。

第三，QuickUp v4.5的部分新特性写起来比较乱（当然，实际上的可读性很好，只是感觉比较乱），主要是因为刚上来就使用TinUI的高DPI感知特性，然而QuickUp的UI是通过TinUIXml构建的，稳定性或许不如TinUI面板布局，我也不确定。所以免得未来对代码仓库进行大规模更改（如果恢复开源的话），目前暂停开源新代码。

第四，时间精力有限，我要准备接下来会面对的东西了。

感谢使用QuickUp。

---

# Suspend open source

Starting from QuickUp v4.5, the QuickUp project has suspended open source, and existing open source code will be permanently kept open, with only subsequent new code not being followed up. There are several reasons for this decision:

First, as of v4.3, QuickUp is complete enough. v4.5 only adds functions such as high DPI support, stable window restoration, and application group recording. It is a icing on the cake and is not a mandatory feature. In addition, as a personal project, QuickUp can fully meet my needs, and I think I have a high need for convenient management and launch of application groups. Pausing open source does not mean suspending updates, let alone stopping updates (but I don't think any new features will be updated), but the new maintenance code will not change the overall architecture of QuickUp, and there is no need to follow up with new code.

Second, my local development code base and open source code base are two different things, and code synchronization is manual. Of course, I have the ability to realize flow automation, but I just don't want to, there's no need. This is the main reason, plus the first point.

Third, some of the new features in QuickUp v4.5 are rather messy to write (of course, they are actually very readable, but they just feel messy), mainly because TinUI's high DPI sensing features have been used when they first started. However, QuickUp's UI is built through TinUIXml, and it may not be as stable as the TinUI panel layout, which I am not sure. Therefore, in order to avoid large-scale changes to the code base in the future (if open source is restored), open source new code is temporarily suspended.

Fourth, time and energy are limited, so I have to prepare for what I will face next.

Thank you.