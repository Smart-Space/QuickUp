---
layout: post
title: Background Layer
published: True
---

# 自定义背景层

QuickUp 5.2 (pro)起，`设置-常规`界面可以设置背景层样式。

QuickUp应用主窗口分为三层：

1. 底层，系统窗口，`窗口透明度`应用于此；
2. 背景层，显示自定义的颜色、图片，若设置为空，则显示样式背景色；
3. 交互层，显示交互控件，`背景透明度`应用于此。

注意，背景层本身是不透明且不可设置透明度的，交互层可设置透明度看到背景。

背景层设置为图片时，图片格式为`Gdiplus::Bitmap::FromFile`接受格式。

---

# Customize Background Layer

Since QuickUp 5.2 (pro), the `Settings - General` interface now allows you to set the style of the background layer.

The main window of the QuickUp application is divided into three layers: 

1. The bottom layer, system window, `Window Transparency` is applied to this;
2. The background layer, displays custom colors or images. If left blank, it shows the background color of the theme;
3. The interaction layer, displays interaction controls. `Background Transparency` is applied to this. 

**Note that** the background layer is inherently opaque and its transparency cannot be adjusted. The interactive layer, on the other hand, can have its transparency set to allow the background to be seen.

When the background layer is set to an image, the image format should be the one accepted by `Gdiplus::Bitmap::FromFile`.